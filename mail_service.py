import imaplib
import email
import os


def login_mailbox(username, password, imap_server):
    imap = imaplib.IMAP4_SSL(imap_server)
    imap.login(username, password)


def logout_mailbox(imap):
    imap.close()
    imap.logout()
