from django.apps import AppConfig
from django.forms import BooleanField, HiddenInput


class AllmendConfig(AppConfig):
    name = 'begegnungsallmende'
    verbose_name = "b-allmend"

    def ready(self):
        # remove no subscription selection
        from juntagrico import forms
        original_init = forms.SubscriptionPartSelectForm.__init__

        def new_init(self, selected, *args, **kwargs):
            original_init(self, selected, *args, **kwargs)
            del self.helper.layout[-2]
            new_fields = {}
            for key, field in self.fields.items():
                if key.startswith('amount['):
                    new_fields[key] = BooleanField(label=field.label, required=False, initial=field.initial != 0)
            self.fields.update(new_fields)

        forms.SubscriptionPartSelectForm.__init__ = new_init
        from begegnungsallmende.overrides import subscription_select_cleaner, my_get_selected
        forms.SubscriptionPartSelectForm.clean = subscription_select_cleaner
        forms.SubscriptionPartSelectForm.get_selected = my_get_selected

        original_profile_init = forms.MemberProfileForm.__init__

        def new_profile_init(self, *args, **kwargs):
            original_profile_init(self, *args, **kwargs)
            self.fields['first_name'].label = "Name oder Nickname"
            self.fields['last_name'].widget = HiddenInput()
            self.fields['addr_street'].widget = HiddenInput()
            self.fields['addr_zipcode'].widget = HiddenInput()
            self.fields['addr_location'].widget = HiddenInput()
            self.fields['addr_location'].widget = HiddenInput()
            self.fields['phone'].widget = HiddenInput()
            self.fields['mobile_phone'].widget = HiddenInput()
            self.fields['birthday'].widget = HiddenInput()
            self.fields['iban'].widget = HiddenInput()

        forms.MemberProfileForm.__init__ = new_profile_init
