from __future__ import print_function

import os.path
import pickle

import google
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from base64 import urlsafe_b64decode

# Requests all privileges
from googleapiclient.errors import HttpError

SCOPES = 'https://www.googleapis.com/auth/gmail.settings.basic'


def get_size_format(b, factor=1024, suffix='B'):
    """
    Scale bytes to a proper format
    e.g:
        1253656 => '1.20MB'
    """
    for unit in ['', 'K', 'M', 'G', 'T', 'P', 'E', 'Z']:
        if b < factor:
            return f"{b:.2f}{unit}{suffix}"
        b /= factor
    return f"{b:.2f}Y{suffix}"


def clean(text):
    # pretty text for naming a folder
    return "".join(c if c.isalnum() else '_' for c in text)


def gen_folder_name(text):
    folder_name = clean(text)
    folder_count = 0
    while os.path.isdir(folder_name):
        folder_count += 1
        if folder_name[-1].isdigit() and folder_name[-2] == "_":
            folder_name = f"{folder_name[:-2]}_{folder_count}"
        elif folder_name[-2:].isdigit() and folder_name[-3] == "_":
            folder_name = f"{folder_name[:-3]}_{folder_count}"
        else:
            folder_name = f"{folder_name[:-3]}_{folder_count}"
    os.mkdir(folder_name)
    return folder_name


def parse_parts(service, parts, folder_name, message):
    """
        Utility function that parses email partition's content
    """
    if parts:
        for part in parts:
            filename = part.get('filename')
            body = part.get('body')
            mime_type = part.get('mimeType')
            data = body.get('data')
            file_size = body.get('size')
            part_headers = part.get('headers')
            if part.get('parts'):
                # recursion is necessary when a part has other parts inside
                parse_parts(service, part.get('parts'), folder_name, message)
            if mime_type == 'text/plain':
                # parse email mail in case of plain text
                if data:
                    text = urlsafe_b64decode(data).decode()
                    print(text)
            elif mime_type == 'text/html':
                # parse HTML content and save the content
                if not filename:
                    filename = 'index.html'
                filepath = os.path.join(folder_name, filename)
                print(data)
                print('Saving HTML to', filepath)
                with open(filepath, 'wb') as f:
                    f.write(urlsafe_b64decode(data))
            else:
                for part_header in part_headers:
                    part_header_name = part_header.get('name')
                    part_header_value = part_header.get('value')
                    if part_header_name == 'Content-Disposition':
                        if 'attachment' in part_header_value:
                            print("Saving the file:", filename, "size:", get_size_format(file_size))
                            attachment_id = body.get("attachmentId")
                            attachment = service.users().messages() \
                                .attachments().get(id=attachment_id, userId='me', messageId=message['id']).execute()
                            data = attachment.get("data")
                            filepath = os.path.join(folder_name, filename)
                            if data:
                                with open(filepath, 'wb') as f:
                                    f.write(urlsafe_b64decode(data))


def gmail_authenticate():
    creds = None
    # the file token.pickle store the user's access and refresh the tokens, and it
    # created automatically when the authorization flow completes for the first time
    if os.path.exists('token.pickle'):
        with open('token.pickle', "rb") as token:
            creds = pickle.load(token)
    # if credits are not valid, let the user login
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
            # save credentials for the next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)
    service = build('gmail', 'v1', credentials=creds)
    return service


def search_messages(service, query):
    result = service.users().messages().list(userId='me', q=query).execute()
    messages = []
    if 'messages' in result:
        messages.extend(result['messages'])
    while 'nextPageToken' in result:
        page_token = result['nextPageToken']
        result = service.users().messages().list(userId='me', q=query, pageToken=page_token).execute()
        if 'messages' in result:
            messages.extend(result['messages'])
    return messages


def read_message(service, message):
    print('ok')
    msg = service.users().messages().get(userId='me', id=message['id'], format='full').execute()
    payload = msg['payload']
    headers = payload.get('headers')
    parts = payload.get('parts')
    folder_name = 'email'
    has_subject = False
    if headers:
        for header in headers:
            name = header.get('name')
            value = header.get('value')
            print(f'{name.upper()}: {value.upper()}')
            if name.lower() == 'subject':
                has_subject = True
                folder_name = gen_folder_name(folder_name)
        if not has_subject:
            if not os.path.isdir(folder_name):
                os.mkdir(folder_name)
        parse_parts(service, parts, folder_name, message)
