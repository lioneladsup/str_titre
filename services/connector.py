import json
from googleapiclient import discovery
from oauth2client import client
from oauth2client import GOOGLE_REVOKE_URI, GOOGLE_TOKEN_URI
import httplib2
import os
from dotenv import load_dotenv
load_dotenv() 


LOCAL = os.getenv('LOCAL')

GA3_SECRETS = {}

if LOCAL == 'True': 
    GA3_SECRETS = json.load(open(os.getenv("GA3_SECRETS")))
elif LOCAL == 'False':
    GA3_SECRETS = json.loads(os.getenv("GA3_SECRETS"))


def refresh_google_api_secrets(gg_api_secrets):
    # When we run in the server we create a creds 
    # using .dat file we already have with a refresh token
    credentials = client.OAuth2Credentials(
        access_token=None,  # set access_token to None since we use a refresh token
        client_id=gg_api_secrets['client_id'],
        client_secret=gg_api_secrets['client_secret'],
        refresh_token=gg_api_secrets['refresh_token'],
        token_expiry=None,
        token_uri=GOOGLE_TOKEN_URI,
        user_agent=None,
        revoke_uri=GOOGLE_REVOKE_URI)

    credentials.refresh(http=httplib2.Http())
    return credentials

def create_google_analytics_service(google_analytics_refreshed_secrets):
    '''This function will create authorize access to the GA API with refreshed token'''
    
    http_var = google_analytics_refreshed_secrets.authorize(http=httplib2.Http())

    ga_service = discovery.build(
        'analyticsreporting',
        'v4',
        http=http_var)
    return ga_service



def get_google_analytics_service():
    refreshed_secrets = refresh_google_api_secrets(GA3_SECRETS)
    service = create_google_analytics_service(refreshed_secrets)
    return service


if __name__== "__main__":
    print(GA3_SECRETS, LOCAL)
    # print(get_google_analytics_service())