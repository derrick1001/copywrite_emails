counts = {}
emails = ["null@null.com", "someone@somewhere.com", "null@null.com"]

print('Emails:', emails)

print('Counting...')
for email in emails:
    counts[email] = counts.get(email, 0) + 1
print('Counts', counts)
