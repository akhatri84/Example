import smtplib
from decouple import config
from django.views.decorators.csrf import csrf_exempt
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from django.template.loader import render_to_string
from email.mime.image import MIMEImage

import os


@csrf_exempt
def sendMailApp(ADMIN_EMAIL, item, action, context):
    message = MIMEMultipart('alternative')

    if item == 'Feedback':
        message['subject'] = action + " action performed in Request for Support"
    else:
        message['subject'] = action + " action performed in " + item + " Module."

    template = render_to_string('mail_template.html', {"context": context, "item": item})

    part2 = MIMEText(template, 'html')
    message.attach(part2)

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    url = os.path.join(BASE_DIR, 'static/tcl-logo.png')
    img_data = open(url, 'rb').read()
    msImage = MIMEImage(img_data)
    msImage.add_header('Content-ID', '<image1>')

    message.attach(msImage)

    # # file text sending
    # txt_data = open('static/mail.txt', 'rt').read()
    # msText = MIMEText(txt_data)
    # msText.add_header('Content_ID', 'attachment',filename=txt_data)
    # message.attach(msText)
    # # file text sending

    with smtplib.SMTP(config('SMTP_EMAIL_SERVER'), 587) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.ehlo()
        smtp.login(config('EMAIL_ADDRESS'), config('EMAIL_PASSWORD'))

        smtp.sendmail(config('EMAIL_SENDER'), ADMIN_EMAIL, message.as_string())
    return "Message send"


@csrf_exempt
def sendCommunityMail(ADMIN_EMAIL, data):
    message = MIMEMultipart('alternative')

    
    
    message['subject'] = "New Member joined the community"

    template = render_to_string('community_template.html', {"fname":data["merge_fields"]["FNAME"],"lname":data["merge_fields"]["LNAME"],"phone":data["merge_fields"]["PHONE"],"email":data["email_address"],"company":data["merge_fields"]["COMPANY"]})

    part2 = MIMEText(template, 'html')
    message.attach(part2)

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    url = os.path.join(BASE_DIR, 'static/tcl-logo.png')
    img_data = open(url, 'rb').read()
    msImage = MIMEImage(img_data)
    msImage.add_header('Content-ID', '<image1>')

    message.attach(msImage)


    with smtplib.SMTP(config('SMTP_EMAIL_SERVER'), 587) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.ehlo()
        smtp.login(config('EMAIL_ADDRESS'), config('EMAIL_PASSWORD'))

        smtp.sendmail(config("NOREPLY_MAIL"), config('ADMIN_EMAIL'), message.as_string())
    return "Message send"
