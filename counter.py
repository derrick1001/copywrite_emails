counts = {}
with open('offenders/tracked.txt', 'r') as f:
    emails = [email.rstrip('\n') for email in f]

print(f'Emails: {emails}\n')

for email in emails:
    counts[email] = counts.get(email, 0) + 1

print(f'Counts: {counts}')
