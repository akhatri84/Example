from django.shortcuts import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import re
import json

from django.conf import settings
from mailchimp_marketing import Client
from mailchimp_marketing.api_client import ApiClientError


# Create your views here.

@csrf_exempt
def subscription(request):
    if request.method == "POST":
        email = request.POST['email']
        firstname = request.POST.get('firstname', '')
        lastname = request.POST.get('lastname', '')

        if not re.match(r".+@.+\..+", email):
            return HttpResponse("Please enter a valid email address")

        mailchimp = Client()
        mailchimp.set_config({
            "api_key": settings.MAILCHIMP_API_KEY,
            "server": settings.MAILCHIMP_DATA_CENTER,
        })

        member_info = {
            "email_address": email,
            "merge_fields": {
                "FNAME": firstname,
                "LNAME": lastname
            },
            "status": "subscribed",
        }

        try:
            response = mailchimp.lists.add_list_member(settings.MAILCHIMP_EMAIL_LIST_ID, member_info)

            return HttpResponse(json.dumps(response))
        except ApiClientError as error:
            return HttpResponse(format(error.text))
