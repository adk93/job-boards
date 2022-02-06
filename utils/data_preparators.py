# Standard library imports
from dataclasses import asdict, dataclass
from typing import List

# Third party imports
import pandas as pd

# Local application imports


def convert_dataclass_to_dataframe(dclass: dataclass) -> pd.DataFrame:
    return pd.DataFrame(asdict(offer) for offer in dclass.offers)


def convert_dataframe_to_list_of_lists(df: pd.DataFrame) -> List[List]:
    return [df.columns.values.tolist()] + df.values.tolist()


def convert_dict_to_str(l: list) -> str:
    string = ""
    try:
        for element in l:
            for k, v in element.items():
                string += f"{v}"
    except TypeError as e:
        print(e)
    except AttributeError as e:
        print(e)
        return l

    return string

def extract_employment_type(x: List, e_type: str, col_name: str):

    try:
        data = list(filter(lambda y: True if y['type'] in e_type else False, x))
        return data[0][col_name]
    except TypeError as e:
        print(e)
        print(x)
        return "N/A"
    except IndexError as e:
        print(e)
        print(x)
        return "N/A"
