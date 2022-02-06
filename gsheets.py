# Standard library imports
from typing import List
import os
import ast
from datetime import datetime

# Third party imports
import gspread
from dotenv import load_dotenv

# Local application imports


load_dotenv(".env")
CREDENTIALS = ast.literal_eval(os.getenv("service_account_json"))


class Gsheets:
    """Connects to a google spreadsheet, reads and writes data"""
    def __init__(self, spreadsheet_id: str):
        self.spreadsheet_id = spreadsheet_id
        self.client = self.authenticate_gsheets()

    def authenticate_gsheets(self) -> gspread.client:
        scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
                 "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]

        return gspread.service_account_from_dict(CREDENTIALS)

    def get_data_from_sheet(self, sheet_name: str, range: str = None) -> List[List]:
        """Grabs data from a specified sheet. Uses given range. If range is not given returns all data in a sheet"""
        sheet = self.client.open_by_key(self.spreadsheet_id).worksheet(sheet_name)
        data = sheet.get_all_values() if range is None else sheet.get(range)
        return data

    def update_gsheets(self, sheet_name: str, data: List[List]) -> None:
        """Writes data to a sheet. If range is not given it writes data starting from a cell A1"""
        sheet = self.client.open_by_key(self.spreadsheet_id)

        # Clear sheet before updating
        self.clear_sheet(sheet_name)

        sheet.values_append(sheet_name, {'valueInputOption': 'USER_ENTERED'}, {'values': data})

    def clear_sheet(self, sheet_name: str):
        sheet = self.client.open_by_key(self.spreadsheet_id)
        sheet.worksheet(sheet_name).clear()

    def add_log(self, sheet_name: str, message: str):
        sheet = self.client.open_by_key(self.spreadsheet_id)
        ws = sheet.worksheet(sheet_name)
        now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        ws.append_row([now, message])
