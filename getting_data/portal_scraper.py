import requests
from bs4 import BeautifulSoup

from models import ProcessedFile
import zipfile
import io


SCRAPE_URL = "https://portal.mpsv.cz/sz/stat/nz/qrt"
BASE_URL = "https://portal.mpsv.cz"


class MpsvPortal:

    def __init__(self, db_session, logger):
        self.db_session = db_session
        self.soup = self.get_parsed_statistics_page()
        self.logger = logger

    @staticmethod
    def get_parsed_statistics_page():
        response = requests.get(SCRAPE_URL)
        return BeautifulSoup(response.text, features="lxml")

    def get_unprocessed_files_urls(self):
        monthly_stats = self.soup.find("table", {"class": "OKtable OKbasic2"})
        locations = []
        for td in monthly_stats.find_all("td"):

            file_url = self.find_file_location(td=td)

            if file_url is None:
                continue
            else:
                existing_object = self.db_session.query(ProcessedFile).filter_by(url=file_url).first()
                if existing_object is None:
                    locations.append(file_url)
        return locations

    @staticmethod
    def get_single_excel( url):
        y = requests.get(BASE_URL + url, stream=True)
        with zipfile.ZipFile(io.BytesIO(y.content)) as zip_ref:
            file_names = zip_ref.namelist()

            if len(file_names) != 1:
                # TODO: problem, 2014 jsou i nejake jine
                return None, None
                raise ValueError
            return file_names[0], zip_ref.open(file_names[0])

    def get_excels_to_process(self) -> dict:
        """

        :return: dict of name: {url, excels}. Excel object can be passed to pandas df constructor
        """
        files = {}
        process_urls = self.get_unprocessed_files_urls()
        self.logger.info(f"Found new excel files to process at {process_urls}")
        for i, url in enumerate(process_urls):
            if url is None:
                continue
            excel_name, excel = self.get_single_excel(url)
            if excel is None:
                continue
            files[excel_name] = {"file": excel, "url": url}
        return files

    @staticmethod
    def find_file_location(td):
        a = td.find("a", {"class": "OKbold OKdistinct2 downloadFileLink"})
        if a is None:
            return
        return a.get("href")


if __name__ == "__main__":
    from db_handle import Session
    port = MpsvPortal(db_session=Session())
    non_processed_urls = port.get_excels_to_process()
