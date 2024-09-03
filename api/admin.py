from django.contrib import admin

# Register your models here.
from api.models import Review

admin.site.register(Review)
locals()