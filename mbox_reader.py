#!/home/derrick/venv/bin/python3

from datetime import datetime as dt
from re import search
from time import sleep
from mailbox import mbox
from os import path
from subprocess import run
import logging


# Set global variables
MAILDIR = '/home/derrick/.thunderbird/28rm5iqs.default-release/Mail/Local Folders/Archives.sbd/Copyright'
WORKDIR = '/home/derrick/.local/share/derrick/default/python_scripts/copyright_emails/'
LOGDIR = '/home/derrick/.local/share/derrick/default/python_scripts/copyright_emails/logs/'


# LOGGING CONFIGURATION
formatter = logging.Formatter(fmt="%(levelname)s %(asctime)s: %(message)s (Line: %(lineno)d in %(filename)s)",
                              datefmt="%H:%M:%S")

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(formatter)

file_handler = logging.FileHandler(f"{LOGDIR}copyright_{dt.now().strftime("%m-%d-%y_%H:%M:%S")}.log", "w")
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)

logger.addHandler(console_handler)
logger.addHandler(file_handler)


def extract_attachments(message):
    for part in message.walk():
        if part.get_content_maintype() == 'multipart':
            continue
        fname = part.get_filename()
        if fname:
            filepath = path.join(WORKDIR, fname)
            if not path.isfile(filepath):
                with open(filepath, 'wb') as f:
                    f.write(part.get_payload(decode=True))
                yield filepath
                # print(f"Saved: {filepath}")


def parse_ip(filename):
    with open(filename, 'r') as f:
        for line in f:
            match = search(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', line)
            if match:
                return match.group()


def parse_sub(response: str):
    e9 = search(r'[A-Z][a-z\-]{2,11}-E9-1', response)
    ont_id = search(r'\(\d{2,5}', response)
    return e9.group(), ont_id.group().lstrip('(')


def cleanup():
    rm = run('rm *.xml', shell=True)
    return rm


def locate_customer(address: str):
    from calix.cx_detail import cx
    from calix.smx_search import search_all

    response = search_all(address)
    if response.status_code == 200:
        data = response.json()[0].get('desc')
    e9 = search(r'[A-Z][a-z\-]{2,11}-E9-1', data)
    ont_id = search(r'\(\d{2,5}', data)
    customer = cx(e9.group(), ont_id.group().lstrip('('))
    if customer is not None:
        em = customer.get('locations')[0].get('contacts')[0].get('email', "No email").lower()
        print(f"{address}, {em}")
        sleep(1)
        return em
    else:
        print(f"No customer information available for address {address}")
        return


def parse_messages():
    addresses = []
    attachments = []
    for message in mbox(MAILDIR):
        if 'Notice of Claimed Infringement' in message['subject']:
            files = extract_attachments(message)
            for file in files:
                address = parse_ip(file)
                print(f"Parsed {address}")
                sleep(1)
                addresses.append(address)
                attachments.append(file)
    return addresses, attachments


def get_emails(addresses: list) -> list:
    emails = [locate_customer(ip) for ip in addresses]
    return emails


def compose_email(emails: list, attachments: list):
    from copyright_body import body
    for email, attachment in zip(emails, attachments):
        run(['thunderbird', '-compose', f"to={email},subject='Notice of Claimed Infringement',body={body},attachment={attachment}"])


if __name__ == "__main__":
    addresses, attachments = parse_messages()
    emails = get_emails(addresses)
    for email, attachment in zip(emails, attachments):
        print(f"\n{email}, {attachment.split('/')[9]}")
        sleep(1)
    compose_email(emails, attachments)
    print(f'\nSleeping for {len(addresses)} seconds')
    sleep(len(addresses))
    send_emails = input("Done sending mail?: ")
    if send_emails == 'y':
        print('Cleaning up...')
        cleanup()
    print('Done')
