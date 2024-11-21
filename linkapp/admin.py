from django.contrib import admin

# Register your models here.

from . models import *

admin.site.register(UserVerification)
admin.site.register(GoogleUser)
admin.site.register(UserProfile)
admin.site.register(GoogleUserProfile)
admin.site.register(Interest)
admin.site.register(InterestGoogle)
admin.site.register(UserProperty)
admin.site.register(GoogleUserProperty)
admin.site.register(PropertyImage)
admin.site.register(GooglePropertyImage)
admin.site.register(Like)
admin.site.register(Subscription)


