import argparse
import json
import requests
import google.auth.transport.requests

from google.oauth2 import service_account

PROJECT_ID = 'muutsche'
BASE_URL = 'https://fcm.googleapis.com'
FCM_ENDPOINT = 'v1/projects/' + PROJECT_ID + '/messages:send'
FCM_URL = BASE_URL + '/' + FCM_ENDPOINT
SCOPES = ['https://www.googleapis.com/auth/firebase.messaging']

# [START retrieve_access_token]
def _get_access_token():
  """Retrieve a valid access token that can be used to authorize requests.

  :return: Access token.
  """
  credentials = service_account.Credentials.from_service_account_file(
    'service_account.json', scopes=SCOPES)
  request = google.auth.transport.requests.Request()
  credentials.refresh(request)
  return credentials.token
# [END retrieve_access_token]

def _send_fcm_message(fcm_message):
  """Send HTTP request to FCM with given message.

  Args:
    fcm_message: JSON object that will make up the body of the request.
  """
  # [START use_access_token]
  headers = {
    'Authorization': 'Bearer ' + _get_access_token(),
    'Content-Type': 'application/json; UTF-8',
  }
  # [END use_access_token]
  resp = requests.post(FCM_URL, data=json.dumps(fcm_message), headers=headers)

  if resp.status_code == 200:
    print('Message sent to Firebase for delivery, response:')
    return {
      'status': 200,
      'message': 'Message sent'
      }
  else:
    return {
      'status': resp.status_code,
      'message': 'Unable to send message'
      }
  
def _build_common_message(event):
  # Extract the message from the incoming event
  message = event.get('message', {})
  topic = message.get('topic', '')
  notification = message.get('notification', {})
  title = notification.get('title', 'Default Title')
  body = notification.get('body', 'Default Body')
  custom_data = message.get('data', {})
  """Construct common notifiation message.

  Construct a JSON object that will be used to define the
  common parts of a notification message that will be sent
  to any app instance subscribed to the news topic.
  """
  return {
    'message': {
      'topic': topic,
      'notification': {
        'title': title,
        'body': body
      },
      'data': custom_data
    }
  }

def lambda_handler(event, context):
    common_message = _build_common_message(event=event)
    print('FCM request body for message using common notification object:')
    print(json.dumps(common_message, indent=2))
 # Send the FCM message and capture the response
    response = _send_fcm_message(common_message)
    
    # Return the response from the Lambda function
    return response