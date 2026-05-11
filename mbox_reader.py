#!/home/derrick/venv/bin/python3

from typing import Generator
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


def extract_attachments(message) -> Generator:
    for part in message.walk():
        if part.get_content_maintype() == 'multipart':
            continue
        fname = part.get_filename()
        if fname:
            logger.info(f"Found {fname}")
            filepath = path.join(WORKDIR, fname)
            if not path.isfile(filepath):
                with open(filepath, 'wb') as f:
                    f.write(part.get_payload(decode=True))
                    logger.info(f"Saved {f} in {WORKDIR}")
                yield filepath


def parse_ip(filename):
    with open(filename, 'r') as f:
        for line in f:
            match = search(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', line)
            if match:
                logger.info(f"Parsed {match.group()} from {filename.split('/')[-1]}")
                return match.group()


# def parse_sub(response: str):
#    e9 = search(r'[A-Z][a-z\-]{2,11}-E9-1', response)
#    ont_id = search(r'\(\d{2,5}', response)
#    return e9.group(), ont_id.group().lstrip('(')


def cleanup():
    logger.info(f"Removing all .xml files from {WORKDIR}")
    run('rm *.xml', shell=True)
    logger.info(f"Removing parsed messages from {MAILDIR}")
    run(f"echo '' > {MAILDIR}", shell=True)


def locate_customer(address: str):
    from calix.cx_detail import cx
    from calix.smx_search import search_all

    response = search_all(address)
    if response.status_code == 200:
        data = response.json()[0].get('desc')
    else:
        logger.critical(f"Got {response.status_code}, exiting")
    e9 = search(r'[A-Z][a-z\-]{2,11}-E9-1', data)
    logger.info(f"Matched {e9.group()} from {data}")
    ont_id = search(r'\(\d{2,5}', data)
    logger.info(f"Matched {ont_id.group().lstrip('(')} from {data}")
    customer = cx(e9.group(), ont_id.group().lstrip('('))
    if customer is not None:
        em = customer.get('locations')[0].get('contacts')[0].get('email', "No email").lower()
        logger.info(f"Matched {address} to customer {em}")
        sleep(1)
        return em
    else:
        logger.critical(f"No customer information found in {customer}")
        return


def parse_messages():
    addresses = []
    attachments = []
    logger.info(f"Parsing {MAILDIR}")
    for message in mbox(MAILDIR):
        if 'Notice of Claimed Infringement' in message['subject']:
            files = extract_attachments(message)
            for file in files:
                logger.info(f"Extracted {file.split('/')[-1]}")
                address = parse_ip(file)
                sleep(1)
                addresses.append(address)
                logger.info(f"Added {address} to {type(addresses)} {addresses=}".split("=")[0])
                attachments.append(file)
                logger.info(f"Added {file} to {attachments=}".split("=")[0])
    logger.info(f"Returning {addresses} {attachments} from {parse_messages.__name__}")
    return addresses, attachments


def get_emails(addresses: list) -> list:
    emails = [locate_customer(ip) for ip in addresses]
    logger.info(f"Returning {emails}")
    return emails


def compose_email(emails: list, attachments: list):
    from copyright_body import body
    logger.info(f"Creating {len(emails)} email(s) to be sent")
    for email, attachment in zip(emails, attachments):
        run(['thunderbird', '-compose', f"to={email},subject='Notice of Claimed Infringement',body={body},attachment={attachment}"])


if __name__ == "__main__":
    addresses, attachments = parse_messages()
    emails = get_emails(addresses)
    for email, attachment in zip(emails, attachments):
        logger.info(f"{email} will be attached with {attachment.split('/')[9]}")
        sleep(1)
    logger.info(f"Composing emails to be sent to {emails}")
    compose_email(emails, attachments)
    clean_dir = input("Cleanup? ")
    if clean_dir == 'y':
        logger.info(f"Running {cleanup.__name__}")
        cleanup()
    logger.info("Done, exiting")
