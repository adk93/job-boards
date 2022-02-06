# Standard library imports
from abc import ABC, abstractmethod

# Third-party imports
import requests

# Local application imports

HEADERS = {"user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36",
           "Accept": "application/json",
           "Content-type": "application/json"}


class Parser(ABC):
    """Parser class used to be a parent for specific job board parsers"""
    def __init__(self, url_to_parse: str, company: str, headers: dict = HEADERS):
        self.parse_results = None
        self.url_to_parse = url_to_parse
        self.company = company
        self.headers = headers

    @abstractmethod
    def parse(self) -> None:
        pass


class JustJoinIt(Parser):
    """Class that supports parsing JustJoinIT job board"""
    def __init__(self, url_to_parse: str, company: str, headers: dict = HEADERS):
        super().__init__(url_to_parse, company, headers)

    def __repr__(self):
        return "JustJoinIt Parser"

    def parse(self) -> None:
        r = requests.get(self.url_to_parse, headers=self.headers)

        try:
            r.raise_for_status()
        except requests.RequestException as e:
            print(e)
            self.parse_results = {}

        self.parse_results = r.json()


class JobsForGeek(Parser):
    """Class that supports parsing JobsForGeek job board"""
    def __init__(self, url_to_parse: str, company: str, headers: dict = HEADERS):
        super().__init__(url_to_parse, company, headers)

    def __repr__(self):
        return "JobsForGeek Parser"

    def parse(self) -> None:
        r = requests.get(self.url_to_parse, headers=self.headers)

        try:
            r.raise_for_status()
        except requests.RequestException as e:
            print(e)
            self.parse_results = {}

        self.parse_results = r.json()


class NoFluffJobs(Parser):
    """Class that supports parsing NoFluffJobs job board"""
    params = {"region": "pl",
              "salaryCurrency": "PLN",
              "salaryPeriod": "month"}

    def __init__(self, url_to_parse: str, company: str, headers: dict = HEADERS):
        super().__init__(url_to_parse, company, headers)

    def __repr__(self):
        return "NoFluffJobs Parser"

    def parse(self) -> None:
        payload = {"rawSearch": self.company, "page": 1}

        r = requests.post(self.url_to_parse, headers=self.headers, params=self.params, json=payload)

        try:
            r.raise_for_status()
        except requests.RequestException as e:
            print(e)
            self.parse_results = {}
            return None

        self.parse_results = r.json()


class TheProtocol(Parser):
    def __init__(self, url_to_parse: str, company: str, headers: dict = HEADERS):
        super().__init__(url_to_parse, company, headers)

    def __repr__(self):
        return "The Protocol IT Parser"

    def parse(self) -> None:
        payload = {"keywords": [self.company]}

        r = requests.post(self.url_to_parse, headers=self.headers, json=payload)

        try:
            r.raise_for_status()
        except requests.RequestException as e:
            print(e)
            self.parse_results = {}
            return None

        self.parse_results = r.json()
