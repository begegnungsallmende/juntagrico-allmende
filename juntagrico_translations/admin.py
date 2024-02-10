from modeltranslation.admin import TranslationAdmin
from django.contrib import admin

from juntagrico.entity.subtypes import SubscriptionProduct, SubscriptionSize, SubscriptionType
from juntagrico.admins.subscription_product_admin import SubscriptionProductAdmin
from juntagrico.admins.subscription_size_admin import SubscriptionSizeAdmin
from juntagrico.admins.subscription_type_admin import SubscriptionTypeAdmin


class TranslatedSubscriptionProductAdmin(SubscriptionProductAdmin, TranslationAdmin):
    pass


class TranslatedSubscriptionSizeAdmin(SubscriptionSizeAdmin, TranslationAdmin):
    pass


class TranslatedSubscriptionTypeAdmin(SubscriptionTypeAdmin, TranslationAdmin):
    pass


# juntagrico must be above this app in INSTALLED_APPS to make this work
admin.site.unregister(SubscriptionProduct)
admin.site.register(SubscriptionProduct, TranslatedSubscriptionProductAdmin)
admin.site.unregister(SubscriptionSize)
admin.site.register(SubscriptionSize, TranslatedSubscriptionSizeAdmin)
admin.site.unregister(SubscriptionType)
admin.site.register(SubscriptionType, TranslatedSubscriptionTypeAdmin)
