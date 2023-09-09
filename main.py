import os
import csv
from bs4 import BeautifulSoup
import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()

class User:
    def __init__(self, name, email, field1, field2):
        self.name = name
        self.email = email
        self.field1 = field1
        self.field2 = field2

def create_certaficat(name, field):
    field_ = field.replace("/", "-")
    os.system(f"touch {name}-{field_}.html")
    file_path = f"{name}-{field_}.html"
    print(file_path)
    with open(file_path, "w") as file:
        with open("certaficat.html", "r") as template_file:
            html_content = template_file.read()

        file.write(html_content)

def write_certaficat(name, field):
    field_ = field.replace("/", "-")
    file_path = f"{name}-{field_}.html"  
    with open(file_path, "r") as file:
        html_content = file.read()

    soup = BeautifulSoup(html_content, "html.parser")

    h1_name = soup.find("h1", id="name")
    h1_name.string = name

    h1_field = soup.find("h1", id="field")
    h1_field.string = field

    with open(file_path, "w") as file:
        file.write(str(soup)) 


def send_emails(name, field, email):
    sender_email = os.getenv("SENDER_EMAIL")
    sender_password = os.getenv("SENDER_PASSWORD")

    field_ = field.replace("/", "-")
    html = f"{name}-{field_}.html"

    with open(html, "rb") as attachment:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())

    encoders.encode_base64(part)
    part.add_header(
    "Content-Disposition",
    f"attachment; filename= f'{html}'",
    )

    message = MIMEMultipart()
    message['Subject'] = "Summer School Certaficats"
    message['From'] = "salmisifofedz@gmail.com"
    message['To'] = email
    html_part = MIMEText("your certaficat is ready")
    message.attach(html_part)
    message.attach(part)

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, email, message.as_string())



        
with open('users.csv', 'r', newline='') as csv_file:
    csv_reader = csv.reader(csv_file)

    for row in csv_reader:
        user = User(row[0].replace(" ", "-"), row[1], row[4].replace(" ", "-"), row[5].replace(" ", "-"))
        create_certaficat(user.name, user.field1)
        create_certaficat(user.name, user.field2)

        write_certaficat(user.name, user.field1)
        write_certaficat(user.name, user.field2)
        
        send_emails(user.name, user.field1, user.email)
        send_emails(user.name, user.field2, user.email)

