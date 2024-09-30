import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import datetime as dt
import glob
import pandas as pd

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = os.getenv("SHEET_ID")
Month = dt.datetime.now().strftime("%B")
SAMPLE_RANGE_NAME = "Transactions|" + Month


def getSheet():
  """Shows basic usage of the Sheets API.
  Prints values from a sample spreadsheet.
  """
  creds = None
  # The file token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
  if os.path.exists(".config/gspread/token.json"):
    creds = Credentials.from_authorized_user_file(".config/gspread/token.json", SCOPES)
  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
          ".config/gspread/credentials.json", SCOPES
      )
      creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open("token.json", "w") as token:
      token.write(creds.to_json())

  try:
    service = build("sheets", "v4", credentials=creds)

    # Call the Sheets API
    sheet = service.spreadsheets()
    result = (
        sheet.values()
        .get(spreadsheetId=SAMPLE_SPREADSHEET_ID, range=SAMPLE_RANGE_NAME)
        .execute()
    )
    values = result.get("values", [])

    if not values:
      print("No data found.")
      return

    df = pd.DataFrame(values)
    filepaths = glob.glob("data/current/*.csv")
    print(filepaths)
    if filepaths != []:
        filename = filepaths[0].split("/")[-1]
        if filename == dt.datetime.now().strftime("%Y-%m-%d") + ".csv":
            filename = filename.replace(".csv", "_" + str(dt.datetime.now().time()) +".csv")
        os.replace(filepaths[0], "data/archive/" + filename)
    df.to_csv("data/current/" + dt.datetime.now().strftime("%Y-%m-%d") + ".csv", index=False)
    return df
  except HttpError as err:
    print(err)