from django.apps import AppConfig
from django.forms import BooleanField


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
                    new_fields[key] = BooleanField(label=field.label, required=False)
            self.fields.update(new_fields)

        forms.SubscriptionPartSelectForm.__init__ = new_init
        from begegnungsallmende.overrides import subscription_select_cleaner, my_get_selected
        forms.SubscriptionPartSelectForm.clean = subscription_select_cleaner
        forms.SubscriptionPartSelectForm.get_selected = my_get_selected
