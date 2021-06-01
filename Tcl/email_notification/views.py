from django.shortcuts import render,HttpResponse
from utilities.mail_notification import sendNotification



def product_summary_notification(request):
    try:
        sendNotification("vincenzo@truecostlabel.com")
        return HttpResponse("Mail Sent")
    except:
        return HttpResponse("Failed to Send mail")

