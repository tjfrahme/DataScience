import base64
import requests
import json
import pandas as pd
import time
import gspread  #Google Sheets unit
from google.oauth2.service_account import Credentials
from google.auth.transport.requests import AuthorizedSession
import gspread_dataframe as gd

# gets token needed for authentication
# https://developers.marketo.com/rest-api/authentication/
def get_token():
    req_token = requests.get('https://HIDDEN.mktorest.com/identity/oauth/token?grant_type=client_credentials&client_id=HIDDEN&client_secret=HIDDEN')
    token = req_token.json()['access_token']
    return token

#basic api call, used throughout program
def api_call (api_request):
    #calls then creates token
    tokencall = f"Bearer {get_token()}"
    headers = {'Authorization': tokencall}

    base_url= 'https://HIDDEN.mktorest.com'
    
    #api request should be in form of --->   api_call('/rest/asset/v1/programs.json')
    
    return requests.get(base_url + api_request, headers = headers).json()


#basic api post call, used throughout program
def api_post_call(api_request, data):
    #calls then creates token
    bearer = f"Bearer {get_token()}"
    headers = {'Authorization': bearer}

    base_url= 'https://HIDDEN.mktorest.com'
    
    #api request should be in form of --->   api_call('/rest/asset/v1/programs.json')
    
    return requests.post(base_url + api_request, headers = headers, json = data).json()

# returns the number of campaign members in a program
def members_in_program(id):
    
    create_api_call = f"/rest/v1/programs/{id}/members.json?filterType=statusName&filterValues=Member"
    cm_size = len(api_call(create_api_call)['result'])
    
    return cm_size

# gets folder for Nurture > Demand Gen
# api_call('/rest/asset/v1/folders.json?root={"id": 3728, "type": "Folder"}')
#gets list of nurture programs for Nurture > Demand Gen
def get_nurture_programsid():

    nurtures = api_call('/rest/asset/v1/programs.json?filterType=folderId&filterValues=3728')

    list_nurtures = []
    #loops through api call and selects program ID
    for item in nurtures['result']:
        if members_in_program(item["id"]) > 0:   # checks to make sure there are campaign members as 0 creates an error
            list_nurtures.append(item["id"])
        else: 
            pass
    list_nurtures.remove(1868)   # problem with this program not returning proper format
    
    return list_nurtures

# gets list of fields to export, and takes in programId
def get_payload(programId):
    payload = { 
       "format": "CSV",
       "fields": [ 
            "id",
            "sfdcLeadId",
            "statusName",
            "program",
            "isExhausted",
            "Status__c",
            "ICP__c",
            "MQL_Date_new__c",
            "Re_MQL_Date_new__c",
            "mkto71_Behavioral_Score__c",
            "mkto71_Demographic_Score__c",
            "CreatedAt__c"
       ],
       "filter": { 
          "programId":programId
       }
    }

    return payload

# Bulk Program Member Extract

# https://developers.marketo.com/rest-api/bulk-extract/bulk-program-member-extract/#creating_a_job

# 1) Create a job
#         POST /bulk/v1/program/members/export/create.json 

# 2) Push job to be queed
#         POST /bulk/v1/program/members/export/{exportId}/enqueue.json

# 3) Get Status us job
#         GET /bulk/v1/program/members/export/{exportId}/status.json

# 4) Retrieve Data
#         GET /bulk/v1/program/members/export/{exportId}/file.json


#steps 1 and 2, creates the job and queues it
def create_job(programid):
    parameters = get_payload(programid)

    # creates job
    exportid = api_post_call('/bulk/v1/program/members/export/create.json', parameters)['result'][0]['exportId']
    
    # sends job to queue
    apitoque = f"/bulk/v1/program/members/export/{exportid}/enqueue.json"
    api_post_call(apitoque,'')
    
    return exportid  


def get_status(job_id):
    
    statuscall = f"/bulk/v1/program/members/export/{job_id}/status.json"
    get_status = api_call(statuscall)
    return get_status['result'][0]['status']


# step 4, retrieves data
def get_data(job_id):
    
    tokencall = f"Bearer {get_token()}"
    headers = {'Authorization': tokencall}
    
    base_url= f"https://HIDDEN.mktorest.com/bulk/v1/program/members/export/{job_id}/file.json?"
    
        
    for i in range(10):
        if get_status(job_id) == 'Completed':
            return requests.get(base_url, headers = headers).content
            break
        else:
            time.sleep(30)
#             print(get_status(job_id))


def convertDataFrame(data):
    
    my_data = data.decode('utf-8')
    my_data = my_data.split()
    my_data = [elem.split(',') for elem in my_data]

    df = pd.DataFrame(my_data[1::], columns=my_data[0])
    return df


# gets SFDC report data
def get_sfdc_data():
    scopes =["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets',"https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]
    credentials = Credentials.from_service_account_file('mycred.json', scopes=scopes)
    gc = gspread.Client(auth=credentials)
    gc.session = AuthorizedSession(credentials)
    wks = gc.open('nurtureMarketoSFDC').worksheet('Sheet1')
    sfdc_data = gd.get_as_dataframe(worksheet=wks)
    return sfdc_data


def write_to_sheets(df):    
    scopes =["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets',"https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]
    credentials = Credentials.from_service_account_file('mycred.json', scopes=scopes)
    gc = gspread.Client(auth=credentials)
    gc.session = AuthorizedSession(credentials)
    wks = gc.open('nurtureMarketo').worksheet('Sheet2')
    gd.set_with_dataframe(wks, df)


# runs job for a single program id and returns a dataframe
def run_program_data(programId):
    
    exportid = create_job(programId)  #kicks off job and enques it
    
    time.sleep(15)
  
    data = get_data(exportid)  # gets data for single program

    create_df = convertDataFrame(data)  #converts to a df
    
    return create_df


def main_program():
    
    list_programs = get_nurture_programsid()   #['1351', '1594', '1361', '1742', '1346', '1600']
    
    all_df = pd.DataFrame(columns = get_payload(1351)['fields'])  #creates blank df with column headers

    for program in list_programs:
        new_df = run_program_data(program)
        all_df = all_df.append(new_df, ignore_index=True)

    all_df = all_df[pd.to_numeric(all_df.id, errors='coerce').notnull()]   # removes invalid id rows

    sfdc_data = get_sfdc_data()   #gets sfdc_data 
    
    combined_df = pd.merge(all_df, sfdc_data, how='left', left_on= 'sfdcLeadId', right_on= '18 digit lead ID')  #joins the program info data and the salesforce data 
    
    write_to_sheets(combined_df)