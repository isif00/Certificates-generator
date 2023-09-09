import os
import csv
from bs4 import BeautifulSoup
import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By

load_dotenv()

#setting up a user
class User:
    def __init__(self, name, email, field1, field2):
        self.name = name
        self.email = email
        self.field1 = field1
        self.field2 = field2

#generate the template of the html file
def create_certaficat(name, field):
    #removing backslashes to avoid conflicts
    field_ = field.replace("/", "-")

    #creating new html file
    os.system(f"touch {name}-{field_}.html")
    file_path = f"{name}-{field_}.html"
    with open(file_path, "w") as file:
        with open("certaficat.html", "r") as template_file:
            html_content = template_file.read()

        file.write(html_content)

#writing on  the certaficat
def write_certaficat(name, field):

    field_ = field.replace("/", "-")
    file_path = f"{name}-{field_}.html"  
    with open(file_path, "r") as file:
        html_content = file.read()

    soup = BeautifulSoup(html_content, "html.parser")

    #this is changeable depends on the situtation
    h1_name = soup.find("h1", id="name")
    h1_name.string = name

    h1_field = soup.find("h1", id="field")
    h1_field.string = field

    with open(file_path, "w") as file:
        file.write(str(soup)) 

#converting the generated html to image
def html_to_image(name, field):
    options = webdriver.FirefoxOptions()
    driver = webdriver.Firefox(options=options)

    #this could be changed as well
    driver.get(f"file:///home/isifoo/Projects/Others/certaficates_sender/{name}-{field}.html")

    #the class name can be changed too
    elements = driver.find_elements(By.CLASS_NAME, 'gradient-container')

    for i, element in enumerate(elements):
    # Take a screenshot of the element
        element_screenshot = element.screenshot_as_png

        # Save the screenshot to a file
        output_image_path = f"{name}-{field}.png"
        with open(output_image_path, "wb") as f:
            f.write(element_screenshot)

    driver.quit()

#sending emails
def send_emails(name, field, email):
    sender_email = os.getenv("SENDER_EMAIL")
    sender_password = os.getenv("SENDER_PASSWORD")

    field_ = field.replace("/", "-")
    html = f"{name}-{field_}.html"

    #converting to image
    html_to_image(name, field_)

    output_image_path = html.replace(".html", ".png")
    #sending the image
    with open(output_image_path, "rb") as attachment:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())

    encoders.encode_base64(part)
    part.add_header(
    "Content-Disposition",
    f"attachment; filename= '{output_image_path}'",
    )

    message = MIMEMultipart()
    message['Subject'] = "Summer School Certaficats"
    message['From'] = sender_email
    message['To'] = email
    html_part = MIMEText("<h1>Congratulation, your certaficat is ready</h1>", "html")
    message.attach(html_part)
    message.attach(part)

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, email, message.as_string())


#looping through the students
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

