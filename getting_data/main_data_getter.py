import os
from getting_data.portal_scraper import MpsvPortal
from db_handle import Session, test_engine, table_exists
from getting_data.excel_parser import ExcelParser
from models import ProcessedFile, create_all_tables
from config import ROOT_DIR, DATA_GETTER_LOGGER
from getting_data.demographics_scraper import DemographicsStats


def main_data_getter():
    engine = test_engine()

    if not table_exists("district_city_mapping", engine):
        if os.path.exists(ROOT_DIR + "district_city_mapping.csv"):
            import pandas as pd
            mappings = pd.read_csv(ROOT_DIR + "district_city_mapping.csv")
            mappings.to_csv("district_city_mapping.csv", index=False)
            mappings.to_sql("district_city_mapping", engine, index=False)
        else:
            from helpers import get_city_district_mapping
            mappings = get_city_district_mapping()
            mappings.to_sql("district_city_mapping", engine, index=False)

    demos = DemographicsStats(engine, DATA_GETTER_LOGGER)
    if demos.should_scrape():
        demos.get_demographic_statistics()
        demos.write_to_db()

    if not table_exists("processed_files", engine):
        create_all_tables(engine)
    db_sess = Session()
    # get files which haven't been added to DB
    non_processed_files = MpsvPortal(db_session=db_sess, logger=DATA_GETTER_LOGGER).get_excels_to_process()

    # todo: vyresit kdyz nebyla data mesicne

    for name, excel_info in non_processed_files.items():
        excel = excel_info["file"]
        excel_url = excel_info["url"]
        parser = ExcelParser(name, excel)

        unemployment_lasting_districts, unemployment_lasting_cities = parser.get_unemployment_lasting_statistics()
        isco_districts, isco_cities = parser.get_isco_structure_statistics()
        edu_districts, edu_cities = parser.get_age_statistics()
        age_districts, age_cities = parser.get_age_statistics()
        total_districts, total_cities = parser.get_total_statistics()
        ozp_districts, ozp_cities = parser.get_ozp_statistics()

        # context manager rolls back operations, if any single operation fails
        with engine.begin() as conn:
            # writes to db
            for var_name, var_obj in locals().copy().items():
                if "_cities" in var_name or "_districts" in var_name:
                    try:
                        parser.add_year_month_column(var_obj).to_sql(
                            con=conn, name=var_name, index=False, if_exists="append"
                        )
                    except ValueError as e:
                        DATA_GETTER_LOGGER.warn(f"Failed to write to db {e}")
            db_sess.add(ProcessedFile(url=excel_url))
        db_sess.commit()
        DATA_GETTER_LOGGER.info(f"Successfully managed to add data to db for {name} at {excel_url}")
    DATA_GETTER_LOGGER.info("Successfully run data getter")


if __name__ == '__main__':
    main_data_getter()


