from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.forms import HiddenInput
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.views.generic import FormView
from juntagrico import forms, views_subscription
from juntagrico.dao.subscriptiontypedao import SubscriptionTypeDao
from juntagrico.entity.depot import Depot
from juntagrico.forms import RegisterMemberForm, EditMemberForm, EditCoMemberForm, RegisterMultiCoMemberForm, \
    RegisterFirstMultiCoMemberForm, MemberBaseForm, SubscriptionPartSelectForm
from juntagrico.util import temporal
from juntagrico.view_decorators import create_subscription_session
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


@create_subscription_session
def set_defaults(request, session, *args, **kwargs):
    session.depot = Depot.objects.first()
    session.start_date = temporal.start_of_next_business_year()
    return redirect('cs-co-members')


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


class CSCustomForm(forms.Form):
    languages = forms.CharField(required=True, label='Welche Sprache(n) sprichst/verstehst du?', max_length=50)
    children = forms.CharField(required=False, label='Kinder (bitte Alter je Kind angeben mit Komma getrennt):')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-md-3'
        self.helper.field_class = 'col-md-9'
        self.helper.layout = Layout(
            'languages', 'children',
            FormActions(
                Submit('submit', 'Weiter')
            )
        )


class CSCustomView(FormView):
    template_name = 'createsubscription/custom.html'
    form_class = CSCustomForm

    def __init__(self):
        super().__init__()
        self.cs_session = None

    def get_initial(self):
        lines = self.cs_session.main_member.notes.split('\n')
        return {
            'languages': lines[-2][10:] if len(lines) > 2 else '',
            'children': lines[-1][8:] if len(lines) > 2 else ''
        }

    @method_decorator(create_subscription_session)
    def dispatch(self, request, cs_session, *args, **kwargs):
        self.cs_session = cs_session
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        self.cs_session.main_member.notes = '\n' + 'Sprachen: ' + form.cleaned_data['languages'] + '\n'
        if form.cleaned_data['children']:
            self.cs_session.main_member.notes += 'Kinder: ' + form.cleaned_data['children']
        self.cs_session.co_members_done = True
        return redirect(self.cs_session.next_page())


@login_required
def subscription(request, subscription_id=None, *args, **kwargs):
    member = request.user.member
    if subscription_id is None:
        subscription_id = getattr(member.subscription_current, 'id', None)
        if subscription_id is None:
            subscription_id = getattr(member.subscription_future, 'id', None)
    return views_subscription.subscription(request, subscription_id)
