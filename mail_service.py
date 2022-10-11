from imap_tools import MailBox, AND
from cyber_parser import parse_cyber_daily_newsletter, cyber_daily_html_to_text
from parser_utils import clean,gen_folder_name,save_html_byte_content

import shutil

def login_mailbox(server, user, password):
    mailbox = MailBox(server).login(user, password)
    return mailbox


def fetch_messages(mailbox,subject,cursor):
    mail_folder_prefix = 'email'
    messages = mailbox.fetch(AND(subject=subject))
    for message in messages:
        folder_name = gen_folder_name(mail_folder_prefix)
        byte_content = message.html.encode('utf8')
        save_html_byte_content(folder_name, byte_content)
        text_filepath = cyber_daily_html_to_text(folder_name)
        parse_cyber_daily_newsletter(text_filepath,cursor)
        shutil.rmtree(folder_name) 
        #mailbox.delete([msg.uid])

