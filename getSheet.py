from dotenv import load_dotenv
import os
import requests

load_dotenv()

# Get the environment variables
API_KEY = os.getenv("API_KEY")
SHEET_ID = os.getenv("SHEET_ID")
SHEET_NAME = os.getenv("SHEET_NAME")

ENDPOINT_GOOGLE_SHEETS = f"https://sheets.googleapis.com/v4/spreadsheets/{SHEET_ID}/values/{SHEET_NAME}!A1:Z?alt=json&key={API_KEY}"

def getSheet():
    try:
        response = requests.get(ENDPOINT_GOOGLE_SHEETS)
        response.raise_for_status()
        data = response.json()
        return data
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    data = getSheet()
    if data:
        print(data)
    else:
        print("No data found")