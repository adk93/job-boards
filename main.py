# Standard library imports
from typing import Callable, List
import itertools

# Third-party imports
import pandas as pd

# Local application imports
from parser import JustJoinIt, JobsForGeek, NoFluffJobs, TheProtocol
from data import JobOffers
from utils import data_extractors, data_preparators
from gsheets import Gsheets

PARSERS = {"JustJoinIT": {"factory": JustJoinIt,
                          "url": "https://justjoin.it/api/offers/search?company_names[]={{company}}",
                          "data_extractor": data_extractors.just_join_it_data_extractor},
           "JobsForGeek": {"factory": JobsForGeek,
                           "url": "https://jobsforgeek.com/api/public/job-offer",
                           "data_extractor": data_extractors.jobs_for_geek_extractor},
           "NoFluffJobs": {"factory": NoFluffJobs,
                           "url": "https://nofluffjobs.com/api/search/posting",
                           "data_extractor": data_extractors.no_fluff_jobs_extractor}
           }

SPREADSHEET_ID: str = "1A3m62e6OALSkoSv8XNzbCTLO9kktMlL86VnZLWOOUsY"
SOURCE_SHEET_NAME: str = "KONKURENCJA"
DEST_SHEET_NAME: str = "OFERTY"
LOG_SHEET_NAME: str = "LOGI"


def add_logs(message: str):
    gsheet = Gsheets(SPREADSHEET_ID)
    gsheet.add_log(LOG_SHEET_NAME, message)


def get_companies_list(range: str) -> List:
    add_logs("Fetching list of companies to parse")
    gsheet = Gsheets(SPREADSHEET_ID)
    data: List[List] = gsheet.get_data_from_sheet(SOURCE_SHEET_NAME, range)
    flat_data: List = list(filter(lambda x: True if x != "" else False, list(itertools.chain(*data))))
    add_logs("List of companies parsed")
    return flat_data


def parse_data_by_company(url: str, company: str, ParserFactory: Callable,
                          DataExtractor: Callable, data_collector: JobOffers) -> None:
    add_logs(f"Parsing: {company}")
    parser = ParserFactory(url, company)
    parser.parse()
    parse_results = parser.parse_results
    add_logs(f"{company} parsed! Now extracting...")
    DataExtractor(parse_results, data_collector, company)
    add_logs(f"{company} data extracted")


def parse_companies(companies: List, data_collector: JobOffers) -> None:
    for company in companies:
        for job_board_parser in PARSERS.values():
            add_logs(f"Preparing to parse {company} on {repr(job_board_parser['factory'])}")
            url_to_parse = job_board_parser['url'].replace("{{company}}", company)
            parse_data_by_company(url_to_parse,
                                  company,
                                  job_board_parser['factory'],
                                  job_board_parser['data_extractor'],
                                  data_collector)


def get_previous_postings_from_gsheets() -> List[List]:
    add_logs("Retrieving previous offers data")
    gsheet = Gsheets(SPREADSHEET_ID)
    return gsheet.get_data_from_sheet(DEST_SHEET_NAME)


def prepare_data_for_sending(data_collector: JobOffers) -> List[List]:
    # Get previously posted data as a pandas dataframe
    src_data: List[List] = get_previous_postings_from_gsheets()
    head = src_data.pop(0)
    src_data_df = pd.DataFrame(data=src_data, columns=head)

    # convert parsed data to a pandas dataframe
    add_logs("Converting parsed data to a dataframe")
    parsed_data: pd.DataFrame = data_preparators.convert_dataclass_to_dataframe(data_collector)
    add_logs("Data converted into a dataframe")

    # extract data from column of employment_types
    helper_cols_dict = {"employment_types": ["b2b", "UoP"],
                        "extracted_data": ['salary_min', 'salary_max', 'currency']}

    add_logs("Extracting salary data")
    for e_type in helper_cols_dict['employment_types']:
        for data in helper_cols_dict['extracted_data']:
            col_name = f"{e_type}_{data}"
            e_type_modified = e_type.upper() if e_type == "b2b" else "UOPPERMANENT"

            parsed_data[col_name] = parsed_data['employment_types'].apply(
                lambda x: data_preparators.extract_employment_type(x, e_type_modified, data)
            )

    parsed_data.drop('employment_types', axis=1, inplace=True)

    # append both dataframes to each other
    combined_data = src_data_df.append(parsed_data)

    # drop duplicates on combined dataframe
    combined_data_wd = combined_data.drop_duplicates(subset=["company", "job_title", "published_at"])

    combined_data_wd['skills'] = combined_data_wd['skills'].apply(
        lambda x: data_preparators.convert_dict_to_str(x))

    combined_data_wd = combined_data_wd.fillna('')

    # Convert dataframe with removed duplicates to a list of lists
    combined_data_as_list = data_preparators.convert_dataframe_to_list_of_lists(combined_data_wd)
    return combined_data_as_list


def post_job_offers(data: List[List]) -> None:
    add_logs("Updating data in a sheet")
    gsheet = Gsheets(SPREADSHEET_ID)
    gsheet.update_gsheets(DEST_SHEET_NAME, data)
    add_logs("Data updated!")


def main() -> None:
    # Get list of companies to look for
    companies = get_companies_list("A2:A")
    print(companies)

    # Initialize JobOffers dataclass
    job_offers = JobOffers()

    # Parse companies and add results to dataclass object
    parse_companies(companies, job_offers)
    print(job_offers)

    # Convert data from dataclass to pandas dataframe, remove duplicates from existing postings, prepare data
    data = prepare_data_for_sending(job_offers)
    print(data)

    # post job offers from a clean data
    post_job_offers(data)


if __name__ == "__main__":
    main()
