# Standard library imports

from abc import ABC, abstractmethod

# Third-party imports
import requests
import pandas as pd
import gspread
import numpy


class offers(ABC):
    def __init__(self, sheet_name, technologies=None, levels=None, spreadsheet="Oferty", validate=True):
        self.technologies = technologies
        self.levels = levels
        self.spreadsheet = spreadsheet
        self.validate = validate
        self.sheet_name = sheet_name
        self.client = None
        self.df = None
        self.reference_df = None


    def _authenticate_gsheets(self):
        from oauth2client.service_account import ServiceAccountCredentials

        scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
                 "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]

        creds = ServiceAccountCredentials.from_json_keyfile_name(r"Oferty pracy-4d1bc6616cb2.json",
                                                                 scope)

        self.client = gspread.authorize(creds)

    def _get_reference_data(self):

        self._authenticate_gsheets()

        sheet = self.client.open(self.spreadsheet).worksheet(self.sheet_name)

        try:
            data = sheet.get_all_values()
            head = data.pop(0)

            reference_df = pd.DataFrame(data, columns=head)
            reference_df = reference_df.drop([''], axis=1)
        except:
            reference_df = pd.DataFrame()
        finally:
            self.reference_df = reference_df

    def compare_dataframes(self):
        joined_df = self.reference_df.append(self.df)
        return joined_df.drop_duplicates()

    def update_gsheets(self, df_to_send):
        sheet = self.client.open(self.spreadsheet).worksheet(self.sheet_name)
        last_row = len(df_to_send) - 1

        first_row = 2
        first_col = 1
        last_row = last_row + 2
        last_col = len(df_to_send.columns)

        cell_list = sheet.range(first_row, first_col, last_row, last_col)

        for cell in cell_list:
            value = df_to_send.iat[cell.row-2, cell.col-1]
            if isinstance(value, numpy.bool_):
                value = bool(value)
            cell.value = value

        sheet.update_cells(cell_list)

        for n, col in enumerate(df_to_send.columns):
            sheet.update_cell(1, n+1, col)

    def process(self):
        self._get_reference_data()

        if len(self.reference_df) == 0:
            self.reference_df = self.df

        compared_df = self.compare_dataframes()
        self.update_gsheets(compared_df)

    @abstractmethod
    def parse(self) -> None:
        """Parse a website"""


class justJoinIt(offers):

    def parse(self):

        def employment_types(x, _type):
            try:
                return x[0]['salary'][_type]
            except:
                return "N/A"

        def skills(x):
            return ", ".join([i['name'] for i in x])

        headers = {"Referer": "https://justjoin.it/all/javascript/junior",
                   "Accept": "application/json",
                   "Content-type": "application/json"}

        r = requests.get(r"https://justjoin.it/api/offers", headers=headers)

        df = pd.DataFrame(r.json())

        df = df[df['marker_icon'].isin(self.technologies) & (df['experience_level'].isin(self.levels))]

        df['min_salary'] = df['employment_types'].apply(lambda x: employment_types(x, 'from'))
        df['max_salary'] = df['employment_types'].apply(lambda x: employment_types(x, 'to'))
        df['currency_salary'] = df['employment_types'].apply(lambda x: employment_types(x, 'currency'))

        df['skills_str'] = df['skills'].apply(skills)
        df['url'] = df['id'].apply(lambda x: r"https://justjoin.it/offers/" + x)

        df = df[['published_at', 'company_name', 'company_size', 'company_url', 'title', 'marker_icon', 'min_salary', 'max_salary',
                 'currency_salary', 'skills_str', 'remote', 'workplace_type', 'city', 'address_text', 'latitude',
                 'longitude', 'id', 'url']]

        self.df = df


class noFluffJobs(offers):
    def parse(self):
        headers = {"Accept": "application/json",
                   "Content-type": "application/json"}

        params = {"region": "pl",
                  "salaryCurrency": "PLN",
                  "salaryPeriod": "month"}

        payload = {"criteriaSearch": {"location": {"picked": [],
                                                   "custom": []},
                                      "category": ["backend"],
                                      "country": [],
                                      "employment": [],
                                      "company": [], "seniority": [],
                                      "requirement": {"picked": [],
                                                      "custom": []},
                                      "salary": [],
                                      "more": {"picked": [],
                                               "custom": []}},
                   "page": 1}

        endpoitnt = "https://nofluffjobs.com/api/search/posting"
        r = requests.get(endpoitnt, headers=headers, params=params, json=payload)
        data = r.json()

        df = pd.DataFrame(data['postings'])

        df['min_salary'] = df['salary'].apply(lambda x: str(x['from']))
        df['max_salary'] = df['salary'].apply(lambda x: str(x['to']))
        df['currency_salary'] = df['salary'].apply(lambda x: x['currency'])
        df['type_salary'] = df['salary'].apply(lambda x: x.get('type', 'N/A'))
        df['city'] = df['location'].apply(lambda x: x.get('places', [])[0].get("city", "N/A"))
        df['latitude'] = df['location'].apply(
            lambda x: x.get('places', [])[0].get("geoLocation", {}).get("latitude", "N/A"))
        df['longitude'] = df['location'].apply(
            lambda x: x.get('places', [])[0].get("geoLocation", {}).get("longitude", "N/A"))
        df['posted'] = pd.to_datetime(df['posted'], unit='ms').dt.strftime("%Y-%m-%d")
        df['regions'] = df['regions'].apply(lambda x: ", ".join(x))
        df['flavors'] = df['flavors'].apply(lambda x: ", ".join(x))

        df = df[df['technology'].isin(self.technologies) & (
        df['seniority'].apply(lambda x: set(self.levels).issubset(set(x))))]

        df['seniority'] = df['seniority'].apply(lambda x: ", ".join(x))

        df = df[['category', 'flavors', 'id', 'name', 'onlineInterviewAvailable',
                 'posted', 'regions', 'seniority', 'technology', 'title', 'url',
                 'min_salary', 'max_salary', 'currency_salary', 'type_salary',
                 'city', 'latitude', 'longitude']]

        self.df = df


class jobsForGeek(offers):
    def parse(self):

        def is_in_technology(iterable, x):
            for i in iterable:
                if i in x:
                    return True
            else:
                return False

        headers = {"Accept": "application/json",
                   "Content-type": "application/json"}

        endpoint = "https://jobsforgeek.com/api/public/job-offer"

        r = requests.get(endpoint, headers=headers)
        data = r.json()
        df = pd.DataFrame(data)

        df['url'] = df['id'].apply(lambda x: "https://jobsforgeek.com/job-offers/details/" + str(x))
        df.drop('lastBumpTime', axis=1, inplace=True)
        df = df[df['skills'].isnull() == False]

        df = df[(df['experience'] < 24) & (df['skills'].apply(lambda x: is_in_technology(self.technologies, x)))]

        df['skills'] = df['skills'].apply(lambda x: ", ".join(x))
        df['id'] = df['id'].astype(str)
        df['experience'] = df['experience'].astype(str)
        df = df.fillna('')

        self.df = df

def main():
    jjit = justJoinIt("JustJoinIt", ['javascript', 'java', 'python'], ['junior'])
    jjit.parse()
    jjit.process()

    nfj = noFluffJobs("NoFluffJobs", ['javascript', 'java', 'python'], ['Junior'])
    nfj.parse()
    nfj.process()

    jfg = jobsForGeek("JobsForGeek", ['Java', 'JavaScript', 'React', 'Node', 'CSS', 'Spring', 'Python'])
    jfg.parse()
    jfg.process()


if __name__ == "__main__":
    main()