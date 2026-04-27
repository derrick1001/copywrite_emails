#!/home/derrick/venv/bin/python3

from re import search
from time import sleep

from mailbox import mbox
from os import path
from subprocess import run


MAILDIR = '/home/derrick/.thunderbird/28rm5iqs.default-release/Mail/Local Folders/Copyright'
TEMPDIR = '/home/derrick/.local/share/derrick/default/projects/copyright_emails/'


def extract_attachments(message):
    for part in message.walk():
        if part.get_content_maintype() == 'multipart':
            continue
        fname = part.get_filename()
        if fname:
            filepath = path.join(TEMPDIR, fname)
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


def cleanup():
    rm = run('rm *.xml', shell=True)
    return rm


def locate_customer(address: str):
    # from juniper.routers import routers
    # from juniper.mx import MX
    from calix.cx_detail import cx
    from calix.smx_search import search_all

    query = search_all(address)

    # for ip, hostname in routers.items():
    #    junos = MX(ip, hostname)
    #    print(f"Checking {hostname}...")
    #    binding = junos.connection.send_command_timing(
    #        f"show dhcp relay binding {address} detail")
    #    print(binding)
    #    if "BOUND" in binding:
    #        print(f"Customer located on {hostname}")
    #        circuit_id = junos.connection.send_command_timing(f"show subscribers detail address {address} | match Circuit")
    #        if circuit_id == '':
    #            print(f"No circuit id listed for address {address}")
    #            continue
    #        e9 = circuit_id.split(':')[1].lstrip()
    #        ont_id = search(r'\d{3,5}$', circuit_id.split(':')[2].rstrip('\n'))
    #        customer = cx(e9, ont_id.group())
    #        if customer is not None:
    #            em = customer.get('locations')[0].get('contacts')[0].get('email', "No email").lower()
    #            print(f"{address}, {em}")
    #            return em
    #        else:
    #            print(f"No customer information available for address {address}")
    #            return


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
    addresses = list(dict.fromkeys(addresses))
    return addresses, attachments


def get_emails(addresses: list) -> list:
    emails = [locate_customer(ip) for ip in addresses]
    return emails


def compose_email(emails: list, attachments: list):
    from copyright_body import body
    # for email, attachment in zip(emails, attachments):
    #    thunderbird = run("thunderbird -compose \"to=\'dishman@cvecfiber.com\',subject=\'Notice of Claimed Infringement\',body={body},attacthment={attachment})
    thunderbird = run(['thunderbird', '-compose', f"to='dishman@cvecfiber.com',subject='Notice of Claimed Infringement',body={body}"])


if __name__ == "__main__":
    # addresses, attachments = parse_messages()
    # emails = get_emails(addresses)
    compose_email(1, 2)
    # cleanup()
