from django.core.exceptions import ValidationError
from django.forms import HiddenInput
from juntagrico.dao.subscriptiontypedao import SubscriptionTypeDao
from juntagrico.entity.depot import Depot
from juntagrico.forms import RegisterMemberForm, EditMemberForm, EditCoMemberForm, RegisterMultiCoMemberForm, \
    RegisterFirstMultiCoMemberForm, MemberBaseForm, SubscriptionPartSelectForm
from juntagrico.util import temporal
from juntagrico.views_create_subscription import CSAddMemberView
from juntagrico.views_subscription import SignupView


class MyOverrideMemberForm(MemberBaseForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['first_name'].label = "Name oder Nickname"
        self.initial['last_name'] = '-'
        self.fields['last_name'].widget = HiddenInput()
        self.initial['addr_street'] = '-'
        self.fields['addr_street'].widget = HiddenInput()
        self.initial['addr_zipcode'] = '-'
        self.fields['addr_zipcode'].widget = HiddenInput()
        self.initial['addr_location'] = '-'
        self.fields['addr_location'].widget = HiddenInput()
        self.initial['addr_location'] = '-'
        self.fields['addr_location'].widget = HiddenInput()
        self.initial['phone'] = '-'
        self.fields['phone'].widget = HiddenInput()
        self.fields['mobile_phone'].widget = HiddenInput()
        self.fields['birthday'].widget = HiddenInput()


class MyRegisterMemberForm(MyOverrideMemberForm, RegisterMemberForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['agb'].label = "Ich möchte gerne an der diesjährigen b-Allmende teilnehmen."


class MyEditMemberForm(MyRegisterMemberForm, EditMemberForm):
    pass


class MyEditCoMemberForm(MyOverrideMemberForm, EditCoMemberForm):
    pass


class MyRegisterMultiCoMemberForm(MyOverrideMemberForm, RegisterMultiCoMemberForm):
    pass


class MyRegisterFirstMultiCoMemberForm(MyOverrideMemberForm, RegisterFirstMultiCoMemberForm):
    pass


class MyCSAddMemberView(CSAddMemberView):
    def get_form_class(self):
        return MyEditCoMemberForm if self.edit else \
            MyRegisterMultiCoMemberForm if self.cs_session.co_members else MyRegisterFirstMultiCoMemberForm


class MySignupView(SignupView):
    def get_form_class(self):
        return MyEditMemberForm if self.cs_session.edit else MyRegisterMemberForm

    def form_valid(self, form):
        # pre-fill session to skip location and start date selection
        self.cs_session.depot = Depot.objects.first()
        self.cs_session.start_date = temporal.start_of_next_business_year()
        return super().form_valid(form)


def subscription_select_cleaner(self):
    super(SubscriptionPartSelectForm, self).clean()
    # check that at least one field is selected
    selected = False
    for name, value in self.cleaned_data.items():
        if name.startswith('amount['):
            if value is True:
                selected = True
                break
    if not selected:
        raise ValidationError('Wähle mindestens einen Tag aus')


def my_get_selected(self):
    return {
        sub_type: 1 if getattr(self, 'cleaned_data', {}).get('amount[' + str(sub_type.id) + ']', False) else 0
        for sub_type in SubscriptionTypeDao.get_all()
    }
