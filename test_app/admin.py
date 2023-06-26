from django.contrib import admin
from .models import *


class TelephonyProviderAdmin(admin.ModelAdmin):
    list_display = ['id', 'sip_gateway_address', 'username', 'password']
    search_fields = ["username"]


class AudioFileAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'name', 'file']
    search_fields = ["name"]


class SubscriberAdmin(admin.ModelAdmin):
    list_display = ['id', 'phone_number', 'user']
    search_fields = ["name"]


admin.site.register(TelephonyProvider, TelephonyProviderAdmin)
admin.site.register(AudioFile, AudioFileAdmin)
admin.site.register(Subscriber, SubscriberAdmin)
admin.site.register(UserSettings)