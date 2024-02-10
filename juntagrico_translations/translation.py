from juntagrico.entity.subtypes import SubscriptionProduct, SubscriptionType, SubscriptionSize
from modeltranslation.translator import register, TranslationOptions


@register(SubscriptionProduct)
class SubscriptionProductTranslationOptions(TranslationOptions):
    fields = ('name', 'description',)


@register(SubscriptionSize)
class SubscriptionSizeTranslationOptions(TranslationOptions):
    fields = ('long_name', 'description',)


@register(SubscriptionType)
class SubscriptionTypeTranslationOptions(TranslationOptions):
    fields = ('long_name', 'description',)
