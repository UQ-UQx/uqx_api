"""
WSGI config for uqx_api project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/howto/deployment/wsgi/
"""

import os
import sys
APP_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(APP_BASE_DIR)

os.environ["DJANGO_SETTINGS_MODULE"] = "uqx_api.settings"

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()