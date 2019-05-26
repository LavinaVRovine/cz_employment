import pandas as pd
import re
from helpers import create_month_start
from config import SHEET_NAME, UNEMPLOYED_COL_NAME
from getting_data.excel_search_indices import ExcelIndexFinder
pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)


class ExcelParser:
    def __init__(self, file_path, file):
        self.file_path = file_path
        self.excel = file
        self.excel_indexer = ExcelIndexFinder(self.excel)
        self.statistics_sheet_name = SHEET_NAME
        self.year, self.month = self.parse_time_frame()
        self.year_month = create_month_start(self.year, self.month)

    def add_year_month_column(self, df):
        df["year_month"] = self.year_month
        return df

    def parse_time_frame(self):
        matches = re.findall(re.compile(r"(\d+_\d+)"), self.file_path)
        if len(matches) != 1:
            # todo vyresit at nefailuje, ale exitne
            raise ValueError
        return matches[0].split("_")

    @staticmethod
    def split_to_city_location(df, column_name="location"):
        # typo in old excels
        df.loc[df["location"] == "Zlínsky kraj", "location"] = "Zlínský kraj"
        districts = df[(
                (df[column_name].str.contains("kraj")) |
                (df[column_name].str.contains("Kraj")) |
                (df[column_name] == "Praha")
        )]
        cities = df[~(df[column_name].str.contains("kraj") | df[column_name].str.contains("Kraj"))]
        return districts, cities

    @staticmethod
    def remove_total_row(df):
        if type(df) == pd.DataFrame:
            return df.iloc[:-1, :]
        elif type(df) == pd.Series:
            return df.iloc[:-1]
        else:
            raise

    def get_total_statistics(self) -> tuple:
        df = self.df_loader(
            *self.get_range_to_limit_wb_loader(" U c h a z e č i    c e l k e m", "celkem", - 1),
            names=["location", UNEMPLOYED_COL_NAME], header=None).reset_index().dropna()
        return self.split_to_city_location(self.remove_total_row(df))

    def get_ozp_statistics(self) -> tuple:

        df = self.df_loader(*self.get_range_to_limit_wb_loader(" U c h a z e č i    c e l k e m", "z toho"))
        df = self.clear_unpivot_df(df)
        df = self.rename_pivoted_df(df, "type_of_disability")
        return self.split_to_city_location(df)

    def get_range_to_limit_wb_loader(self, main_header, sub_header, rows_between_main_sub=0):
        """
        The excel is quite structureless. Method finds range, where data should be located based on headers
        :param main_header: could be total, women atc.
        :param sub_header: could be age header, education header etc.
        :param rows_between_main_sub: magic param to correctly return row index of subheader, if there is a blank row
        :return: tuple of row where the sub header starts, list of column indices with data + index(location) column
        """

        main_header_locs = self.excel_indexer.find_header_location(main_header)
        sub_locs = self.excel_indexer.find_header_location(sub_header, row_start=main_header_locs["row"],
                                                           column_start=main_header_locs["col_start"],
                                                           column_stop=main_header_locs["col_stop"])
        # +1 is different indexing
        return sub_locs["row"] + 1 + rows_between_main_sub, [0] + list(
            range(sub_locs["col_start"], sub_locs["col_stop"])
        )

    def clear_unpivot_df(self, df):

        return self.remove_total_row(df).unstack().reset_index().dropna()

    def df_loader(self, row_start, column_indices, **kwargs):

        return pd.read_excel(self.excel,
                             sheet_name=self.statistics_sheet_name,
                             skiprows=row_start, index_col=0, usecols=column_indices, **kwargs)

    @staticmethod
    def rename_pivoted_df(df, lvl_zero_name):
        return df.rename({"level_0": lvl_zero_name, "level_1": "location", 0: UNEMPLOYED_COL_NAME}, axis=1)

    def get_age_statistics(self):
        df = self.df_loader(
            *self.get_range_to_limit_wb_loader(" U c h a z e č i    c e l k e m", "Věková struktura", 1)
        )
        df = df.drop("do 18 let", axis=1)
        if "věk" in df.columns:
            df = df.drop("věk", axis=1)
        df = self.clear_unpivot_df(df)
        df = self.rename_pivoted_df(df, "age_range")
        return self.split_to_city_location(df)

    def get_education_statistics(self):

        df = self.df_loader(
            *self.get_range_to_limit_wb_loader(" U c h a z e č i    c e l k e m", "Vzdělanostní struktura", 0)
        )
        # fing fers. they have two row headers god fing damnit!
        new_names = []
        for i, col in enumerate(df.columns):
            if "Unnamed" in col:
                new_names.append(df.iloc[0, i])
            else:
                new_names.append(f"{col} {df.iloc[0, i]}")
        df.columns = new_names
        df = df.iloc[2:, :]
        df = self.clear_unpivot_df(df)
        df = self.rename_pivoted_df(df, "education")
        return self.split_to_city_location(df)

    def get_isco_structure_statistics(self):
        df = self.df_loader(*self.get_range_to_limit_wb_loader(
            " U c h a z e č i    c e l k e m", "Struktura podle zaměstnání (CZ-ISCO)", 1
        ))
        df = self.rename_pivoted_df(self.clear_unpivot_df(df), "CZ_ISCO_lvl")

        return self.split_to_city_location(df)

    def get_unemployment_lasting_statistics(self):
        df = self.df_loader(*self.get_range_to_limit_wb_loader(
            " U c h a z e č i    c e l k e m", "Délka nezaměstnanosti", 0
        ))
        df = self.rename_pivoted_df(self.clear_unpivot_df(df), "unemployment_lasting")
        df[UNEMPLOYED_COL_NAME] = pd.to_numeric(df[UNEMPLOYED_COL_NAME])
        return self.split_to_city_location(df)
