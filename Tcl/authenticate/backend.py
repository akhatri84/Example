import logging

from django.apps import apps as django_apps
from django.conf import settings
from django.utils.encoding import smart_text
from django.utils.translation import ugettext as _
from graphql import GraphQLError
from django_cognito_jwt.validator import TokenError, TokenValidator


logger=logging.getLogger(__name__)

class JSONWebTokenAuthentication()