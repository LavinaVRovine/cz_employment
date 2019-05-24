import datetime
import re


def create_month_start(year, month):
    if type(year) == str:
        year = int(year)
    if type(month) == str:
        month = int(month)
    return datetime.datetime(2000+year, month, 1)


def get_city_district_mapping():
    from config import DATA_GETTER_LOGGER
    import pandas as pd
    try:
        df = pd.read_html("https://cs.wikipedia.org/wiki/Administrativn%C3%AD_d%C4%9Blen%C3%AD_%C4%8Ceska")[1]
        df["district"] = df["Kraj"].str.replace(r"\(\d{1,3}.ORP\)", "").str.strip()
        relevant_data = df.iloc[:, [2, 4]]
        return relevant_data
    except Exception as e:
        print(f"Failed to get districts mapping due to {e}")
        DATA_GETTER_LOGGER.fatal(f"Failed to get districts mapping due to {e}")


def clear_kraj(kraj):
    return re.compile(re.escape('kraj'), re.IGNORECASE).sub("", kraj)


COLUMN_NAMES_MAPPING = {
    "district": "Kraj", "location": "Okres?",  "unemployment_count": "Počet nezaměstnaných",
    "year_month": "Rok-měsíc", "year": "Rok", "people_count": "Obyvatel",
    "unemployment_pct": "Nezaměstnanost"
}
