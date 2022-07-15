from base64 import decode
import imaplib
import email
from email.header import decode_header
import os
import csv
import getpass

if os.path.exists('log.txt'):
    os.remove('log.txt')

log = open('log.txt', 'w')

# if emails.txt exists and its not empty, truncate it
if os.path.exists('emails.txt'):
    with open('emails.txt', 'r+') as f:
        f.truncate(0)

log.write('Initialized the log file...\n')

username = ''
password = ''

try:
    with open('login.csv', 'r') as f:
        reader = csv.reader(f)
        # read the first row
        username, password = next(reader)
    
    print("Are these correct?\nUsername: " + username + "\nPassword: " + password[:2] + len(password) * '*')
    cd = input("(y/n): ")
    if cd == 'y':
        pass
    else:
        # throw error if username or password is not correct
        raise Exception('Username or password is not correct')
except:
    username = input("Username: ")
    password = getpass.getpass("Password: ")

    confirm = False

    while not confirm:
        print("Email: " + username)
        print("Password: " + password[:2] + len(password) * "*")
        confirm = input("Is this correct? (y/n): ")
        if confirm == 'y':
            confirm = True
            with open('login.csv', 'w') as f:
                # delete everything in the file
                f.truncate(0)
                writer = csv.writer(f)
                # write the new username and password
                writer.writerow([username, password])

        

    with open('login.csv', 'w') as f:
        writer = csv.writer(f)
        writer.writerow([username, password])





# use your email provider's IMAP server, you can look for your provider's IMAP server on Google
# or check this page: https://www.systoolsgroup.com/imap/
# for office 365, it's this:
imap_server = "outlook.office365.com"

ina = input("Would you like to log the emails that are allowed? (y/n) ")

log.write("Looked over the credentials...\n")

def clean(text):
    # clean text for creating a folder
    return "".join(c if c.isalnum() else "_" for c in text)

try:
    log.write("Attempting Login!!!\n")
    # create an IMAP4 class with SSL, use your email provider's IMAP server
    imap = imaplib.IMAP4_SSL(imap_server)
    # authenticate
    imap.login(username, password)
    log.write("Logged in successfully!!!\n")
    # select a mailbox (in this case, the inbox mailbox)
    # use imap.list() to get the list of mailboxes
    status, messages = imap.select("INBOX")

    # total number of emails
    messages = int(messages[0])

    log.write("Found " + str(messages) + " emails in the inbox...\n")

    allowed_senders = []

    with open("allowed_senders.txt", "r") as f:
        for line in f:
            allowed_senders.append(line.strip())

    log.write("Found " + str(len(allowed_senders)) + " allowed senders...\n")

    log.write("Beginning to parse emails...\n")

    for i in range(messages, 0, -1):
        # fetch the email
        status, data = imap.fetch(str(i), "(RFC822)")
        # decode the email
        email_body = email.message_from_bytes(data[0][1])
        # if the sender is in the list of allowed senders, print the email, subject, and sender
        if email_body["From"] in allowed_senders:
            print("-"*50)
            print("HIT: " + email_body["From"] + ": " + email_body["Subject"])
            body = email_body.get_payload(0)
            if ina.lower() == "y":
                with open("emails.txt", "a") as f:
                    f.write("!! Beginning of email: " + email_body["From"] + ": " + email_body["Subject"] + "\n")
                    f.write(email_body["From"] + ": " + email_body["Subject"] + "\n")
                    f.write(str(body) + "\n")
                    f.write("\n"*5)
                    f.write("!! END OF EMAIL FROM " + email_body["From"] + "!!" + "\n")
                    f.write("="*50 + "\n")
            else:
                print(str(body))

            log.write("! Logged sender {0}\n".format(email_body["From"]))

            print("-"*50)
        else:
            print("!!!!! Sender {0} was skipped, because it's not in the list of allowed senders".format(email_body["From"]))
            

    log.write("Finished parsing emails...\n")

    log.write("Logging out...\n")

    log.write("Closing the log file...\n")

    log.close()

    # close the connection and logout
    imap.close()
    imap.logout()
except:
    log.write("Login failed!!!\n")
    print("Login failed")








input("Press Enter to exit...")