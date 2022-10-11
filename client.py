#from gmail_service import search_messages, read_message, gmail_authenticate
from mail_service import login_mailbox, fetch_messages
from db_manager import create_postgresql_connection,create_db_scheme,close_postgresql_connection
from cyber_parser import parse_cyber_daily_newsletter

import sys


def main():
    psql_connection,cursor = create_postgresql_connection('cyber_daily','cyber_daily','cyber_daily_newsletter')
    create_db_scheme(cursor)
    if sys.argv[1] == '-- info':
        print("\nThis parser allows you to extract information "
              "about Cyber Daily Newsletter released by Recorded Future")
    if sys.argv[1] == '-- help':
        print("\nYou have to enter the following arguments to run this script: imap server, mail, password")

    if len(sys.argv) == 4:
        imap = sys.argv[1]
        email = sys.argv[2]
        password = sys.argv[3]
        mailbox = login_mailbox(imap,email,password)
        fetch_messages(mailbox,'Cyber Daily',cursor)
    else:
        print("\n Insufficient numbers of parameters")

    close_postgresql_connection(psql_connection,cursor)



if __name__ == '__main__':
    main()
