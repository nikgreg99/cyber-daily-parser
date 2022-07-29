from gmail_service import search_messages, read_message, gmail_authenticate


def main():
    service = gmail_authenticate()
    query = 'Cyber Daily'
    # get emails that match the query you specify
    messages = search_messages(service,query)
    # for each email matched, read it (output plain/text to console & save HTML and attachments)
    for message in messages:
        read_message(service, message)


if __name__ == '__main__':
    main()