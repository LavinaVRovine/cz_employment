
import pandas as pd

from sqlalchemy import create_engine
from config import DATABASE_URL, ROOT_DIR, UNEMPLOYED_COL_NAME

engine = create_engine(DATABASE_URL)

# TODO: refactor

def load_age_data():
    CITY_DISTRICT_MAPPING = pd.read_csv(ROOT_DIR + "\\district_city_mapping.csv")
    CITY_DISTRICT_MAPPING.loc[CITY_DISTRICT_MAPPING["district"] == "Praha", "Obec s rozšířenou působností"] = "Praha"

    age_district_df = pd.read_sql_table(con=engine, table_name="age_districts")
    age_cities_cities = pd.read_sql_table(con=engine, table_name="age_cities")
    age_cities_df = pd.merge(CITY_DISTRICT_MAPPING, age_cities_cities, left_on="Obec s rozšířenou působností",
                             right_on="location")
    age_cities_df = age_cities_df.drop("Obec s rozšířenou působností", axis=1)

    demo_statistics = pd.read_sql_table(con=engine, table_name="demographic_statistics")
    grouped_demo_stats = demo_statistics.groupby(["year", "location","district"], as_index=False)["people_count"].sum()
    age_cities_df["year"] = age_cities_df["year_month"].dt.year

    age_cities_df_counts = pd.merge(age_cities_df, grouped_demo_stats, left_on=["location", "year"],
                                      right_on=["location", "year"], how="left")

    age_cities_df_counts = age_cities_df_counts.rename({"district_x": "district"}, axis=1)
    age_cities_df_counts = age_cities_df_counts.drop("district_y", axis=1)
    age_cities_df_counts["unemployment_pct"] = age_cities_df_counts[UNEMPLOYED_COL_NAME] / age_cities_df_counts[
        "people_count"]

    return age_district_df, age_cities_df_counts


def load_totals_data():
    CITY_DISTRICT_MAPPING = pd.read_csv(ROOT_DIR + "\\district_city_mapping.csv")
    CITY_DISTRICT_MAPPING.loc[CITY_DISTRICT_MAPPING["district"] == "Praha", "Obec s rozšířenou působností"] = "Praha"

    total_district_df = pd.read_sql_table(con=engine, table_name="total_districts")
    demo_statistics = pd.read_sql_table(con=engine, table_name="demographic_statistics")
    total_cities_cities = pd.read_sql_table(con=engine, table_name="total_cities")
    grouped_demo_stats = demo_statistics.groupby(["year", "district"], as_index=False)["people_count"].sum()
    total_district_df["year"] = total_district_df["year_month"].dt.year
    total_districts_count = pd.merge(total_district_df, grouped_demo_stats, left_on=["location", "year"],
             right_on=["district", "year"], how="left")
    total_districts_count["unemployment_pct"] = total_districts_count[UNEMPLOYED_COL_NAME] / total_districts_count[
        "people_count"]


    total_cities_df = pd.merge(CITY_DISTRICT_MAPPING, total_cities_cities, left_on="Obec s rozšířenou působností",
                               right_on="location")
    total_cities_df = total_cities_df.drop("Obec s rozšířenou působností", axis=1)


    total_cities_df["year"] = total_cities_df["year_month"].dt.year

    total_cities_df_counts = pd.merge(total_cities_df, demo_statistics, left_on=["location", "year"],
                                      right_on=["location", "year"], how="left")

    total_cities_df_counts = total_cities_df_counts.rename({"district_x": "district"}, axis=1)
    total_cities_df_counts = total_cities_df_counts.drop("district_y", axis=1)
    total_cities_df_counts["unemployment_pct"] = total_cities_df_counts[UNEMPLOYED_COL_NAME] / total_cities_df_counts["people_count"]

    return total_districts_count, total_cities_df_counts


def load_table_data(total_cities_df):
    total_cities_df_location = total_cities_df.groupby(
        ["district", "location", "year_month"], as_index=False
    )["people_count", "unemployment_count"].agg({"people_count": "sum", "unemployment_count": "mean"})

    total_cities_for_table = total_cities_df_location.groupby(
        ["district", "location"], as_index=False
    )["people_count", UNEMPLOYED_COL_NAME].mean()
    total_cities_for_table["unemployment_pct"] = \
        total_cities_for_table[UNEMPLOYED_COL_NAME] / total_cities_for_table["people_count"]
    return total_cities_for_table


if __name__ == '__main__':
    load_age_data()

