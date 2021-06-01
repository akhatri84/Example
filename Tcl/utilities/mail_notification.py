import smtplib
from decouple import config
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from django.template.loader import render_to_string
from email.mime.image import MIMEImage
from product.models import ProductMonthClickCount
from django.db.models import Count
import datetime

import os


def sendNotification(toemail):
    message = MIMEMultipart('alternative')

    message['subject'] = "Product Clicks"

    dt=datetime.datetime.today()
    yr=dt.year
    mn=dt.month
    mnname=datetime.datetime.now().strftime("%B")


    pmc = ProductMonthClickCount.objects.filter(deleted=0,month=mn,year=yr).values('product_id__user_id__onboardingmodel__company').annotate(
        Count('product_id_id'))


    template = render_to_string('Product_wise_summary.html', {"data": pmc,"mn":mnname,"yr":yr})


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

        smtp.sendmail(config('EMAIL_SENDER'), toemail, message.as_string())
