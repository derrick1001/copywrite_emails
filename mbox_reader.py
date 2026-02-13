#!/home/derrick/venv/bin/python3

from re import search

from mailbox import mbox
from os import path
from subprocess import run


MAILDIR = '/home/derrick/.thunderbird/28rm5iqs.default-release/Mail/Local Folders/Inbox'
# MAILDIR = '/home/derrick/.thunderbird/28rm5iqs.default-release/Mail/pop.gmail-2.com/Inbox'
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
    from juniper.routers import routers
    from juniper.mx import MX
    from calix.cx_detail import cx

    for ip, hostname in routers.items():
        junos = MX(ip, hostname)
        binding = junos.connection.send_command_timing(
            f"show dhcp relay binding {address}")
        if "BOUND" in binding:
            print(f"Customer located on {hostname}")
            break
    circuit_id = junos.connection.send_command_timing(
        f"show subscribers detail address {address} | match Circuit")
    e9 = circuit_id.split(':')[1].lstrip()
    ont_id = search(r'\d{3,5}$', circuit_id.split(':')[2].rstrip('\n'))
    customer = cx(e9, ont_id.group())
    em = customer.get('locations')[0].get('contacts')[0].get('email').lower()
    return em


if __name__ == "__main__":
    addresses = set()
    for message in mbox(MAILDIR):
        if 'Notice of Claimed Infringement' in message['subject']:
            files = extract_attachments(message)
            for file in files:
                address = parse_ip(file)
                addresses.add(address)
    emails = [locate_customer(ip) for ip in addresses]
    print(emails)
    cleanup()
