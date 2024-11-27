import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import numpy as np
import pandas as pd
from google.oauth2 import service_account
import re

main_script_path = os.path.abspath('.')
json_file_path = os.path.join(main_script_path, 'Data/keysMCCSheet.json')
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

creds = service_account.Credentials.from_service_account_file(json_file_path, scopes = SCOPES)

def import_sheet(url_gsheet) :

    x = url_gsheet
    id_gsheet = re.search('d\/([a-zA-Z0-9_-]+)',x).group(1)
    gid_gsheet = re.search('gid=([a-zA-Z0-9_-]+)',x).group(1)
    service = build('sheets', 'v4', credentials=creds)
    sheet_metadata = service.spreadsheets().get(spreadsheetId=id_gsheet).execute()
    sheet = service.spreadsheets()
    sheets = sheet_metadata.get('sheets', '')
    for i in sheets : 
        title = i['properties']['title']
        sheet_id = i['properties']['sheetId']
        if gid_gsheet == str(sheet_id) :
            result = sheet.values().get(spreadsheetId = id_gsheet, range = title).execute()
            values = result.get('values')  
            return pd.DataFrame(columns = values[0], data = values[1:len(values)])
        else :
            1

def export_tosheet(url, df) :
    produit = df.fillna(0) 
    Data = []
    Weight = produit.values.tolist()
    ColumnName = list(produit.keys())
    Data.append(ColumnName)
    for i in Weight :
        Data.append(i)

    x = url
    id_gsheet = re.search('d\/([a-zA-Z0-9_-]+)',x).group(1)
    gid_gsheet = re.search('gid=([a-zA-Z0-9_-]+)',x).group(1)
    service = build('sheets', 'v4', credentials=creds)
    sheet = service.spreadsheets()
    sheet_metadata = service.spreadsheets().get(spreadsheetId=id_gsheet).execute()
    sheets = sheet_metadata.get('sheets', '')
    for i in sheets : 
        title = i['properties']['title']
        sheet_id = i['properties']['sheetId'] 
        if gid_gsheet == str(sheet_id) :
            NAME_PAGE = title


            import socket
            socket.setdefaulttimeout(2000)

            clear = sheet.values().clear(spreadsheetId = id_gsheet,
                                            range = NAME_PAGE).execute()   

            request = sheet.values().update(spreadsheetId = id_gsheet, 
                                            range = NAME_PAGE, 
                                            valueInputOption = "USER_ENTERED", 
                                            body = {"values" : Data}).execute()
        else :
            1





