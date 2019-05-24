import xlrd
from config import SHEET_NAME


class ExcelIndexFinder:

    def __init__(self, excel_file=None):
        if excel_file is None:
            self.workbook = xlrd.open_workbook("D:\\Downloads\\strukt-2019-04 (1)\\2Q19_04 internet.xlsx")
        else:
            data = excel_file.read()
            self.workbook = xlrd.open_workbook(file_contents=data)

        self.sheet = self.workbook.sheet_by_name(SHEET_NAME)

    def find_start_location(self, value_to_find, row_start, column_start, column_end):
        for row_num in range(row_start, 20):
            row_values = self.sheet.row_values(row_num)
            for col_num in range(column_start, column_end):
                if row_values[col_num] == value_to_find:
                    return row_values, row_num, col_num

    @staticmethod
    def find_end_location(row_values, col_num, value_to_find):
        for i, value in enumerate(row_values[col_num:]):
            if value != "" and value != value_to_find:
                return i + col_num

    def find_header_location(self, value_to_find, row_start=0, column_start=0, column_stop=150):
        row_values, row_num, col_start = self.find_start_location(value_to_find, row_start, column_start, column_stop)
        if row_values is None:
            raise IOError(f"failed to find requested keyword in file: {value_to_find}")

        col_stop = self.find_end_location(row_values, col_start, value_to_find)

        return {"row": row_num, "col_start": col_start, "col_stop": col_stop}
