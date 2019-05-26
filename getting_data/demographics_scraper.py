import requests
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime
from db_handle import table_exists


class DemographicsStats:

    def __init__(self, db_engine, logger):
        self.engine = db_engine
        self.table_exists = table_exists("demographic_statistics", self.engine)
        self.max_data_year = None
        self.data = None
        self.logger = logger

    def should_scrape(self):
        if not self.table_exists:
            return True
        elif self.table_exists and self.max_data_year is None:
            max_data_year = self.get_max_year()
            self.max_data_year = max_data_year
            return datetime.now().year > max_data_year

        else:
            return False

    def get_max_year(self):
        x = pd.read_sql_query("SELECT max(year) from demographic_statistics", con=self.engine)
        if len(x) == 0:
            raise Exception

        return x.iat[0, 0]

    @staticmethod
    def fake_this_year(data_df, max_data_year):
        """
        as stats for this year aren't available yet, we use LY stats as a proxy for this year's stats
        :param data_df:
        :param max_data_year: max year which we have data for, most likely current year - 1
        :return: df with faked data
        """
        data_df = data_df[data_df["Rok"] == max_data_year]
        data_df = data_df.loc[:, ["Rok", "Název obce", "Stav 31.12."]]
        data_df = data_df.rename({"Stav 31.12.": "Stav 1.1."}, axis=1)
        data_df["Rok"] = max_data_year + 1
        return data_df

    def elections_in_progress(self, response):

        if "voleb je omezen provoz" in response.text:
            self.logger.fatal("Demo Statistics are disabled during elections, because reason")
            raise Exception("Demo Statistics are disabled during elections, because reason")

    def get_demographic_statistics(self):
        url = "https://www.czso.cz/csu/czso/databaze-demografickych-udaju-za-obce-cr"
        base_url = "https://www.czso.cz"
        response = requests.get(url)
        if response.status_code != 200:
            raise ConnectionError
        self.elections_in_progress()
        soup = BeautifulSoup(response.text, features="lxml")

        table = soup.find("table")

        output = None
        max_year = None

        for a in table.find_all("a"):
            district = a.find_previous_sibling("b").text.strip()
            if district == "Hl. m. Praha":
                district = "Praha"
            location = a.text
            link = a.get("href")
            if link is None or "obce_d" not in link:
                raise AssertionError
            df = pd.read_excel(base_url+link)

            max_data_year = df["Rok"].max()
            if max_year is None:
                max_year = max_data_year
            elif max_year != max_data_year:
                raise Exception(f"Data might be corrupt in {a}")

            current_year_fake = self.fake_this_year(df, max_year)
            df = df.loc[:, ["Rok", "Název obce", "Stav 1.1."]]

            df = pd.concat([df, current_year_fake])
            df["location"] = location
            df["district"] = district
            df = df.rename({"Rok": "year", "Název obce": "city", "Stav 1.1.": "people_count"}, axis=1)
            # 1980 is sometimes dash -
            df["people_count"] = pd.to_numeric(df["people_count"], errors="coerce")

            if output is None:
                output = df
            else:
                output = pd.concat([output, df])
        self.data = output
        return output

    def write_to_db(self):
        if self.data is None:
            raise Exception
        self.data.to_sql(con=self.engine, name="demographic_statistics", if_exists="replace", index=False)
        self.logger.info(f"Demographic statistics rewritten due to table exists:{self.table_exists} "
                         f"or {datetime.now().year} > {self.max_data_year}")


if __name__ == "__main__":
    from db_handle import test_engine
    from config import DATA_GETTER_LOGGER
    engine = test_engine()
    d = DemographicsStats(engine, DATA_GETTER_LOGGER)
    if d.should_scrape():
        d.get_demographic_statistics()
        d.write_to_db()
