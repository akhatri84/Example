import json
import re

from decouple import config
from django.conf import settings
from django.shortcuts import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from mailchimp_marketing import Client
from mailchimp_marketing.api_client import ApiClientError

from email_notification.notify_client import sendCommunityMail
from .models import JoinCommunityModel


# Create your views here.

@csrf_exempt
def join_community(request):
    if request.method == "POST":
        email = request.POST['email']
        firstname = request.POST.get('firstname', '')
        lastname = request.POST.get('lastname', '')
        phone = request.POST.get('phone', '')
        company = request.POST.get('company', '')

        if not re.match(r".+@.+\..+", email):
            return HttpResponse("Please enter a valid email address")

        mailchimp = Client()
        mailchimp.set_config({
            "api_key": settings.MAILCHIMP_API_KEY_COMM,
            "server": settings.MAILCHIMP_DATA_CENTER_COMM,
        })

        member_info = {
            "email_address": email,
            "merge_fields": {
                "FNAME": firstname,
                "LNAME": lastname,
                "PHONE": phone,
                "COMPANY": company
            },
            "status": "subscribed",
        }

        try:
            join_community, created = JoinCommunityModel.objects.get_or_create(
                email=email,
                fname=firstname,
                lname=lastname,
                phone=phone,
                company=company
            )

            # if created:
            #     response = mailchimp.lists.add_list_member(settings.MAILCHIMP_EMAIL_LIST_ID_COMM, member_info)
            # else:
            response = member_info

            #sendCommunityMail(config("ADMIN_EMAIL"), member_info)

            return HttpResponse(json.dumps(response))
        except ApiClientError as error:
            return HttpResponse(format(error.text))
