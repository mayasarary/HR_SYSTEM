from django.contrib import admin
#import hr.hr.policies.models

from policies.models import Policy

admin.site.register(Policy)