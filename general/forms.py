from django import forms
from general.models import UserAccount, MessageCenter, JoinWaitingList
from service_provider.models import Subscriber
from django.forms import ModelForm, Textarea
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
# from captcha.fields import CaptchaField
from nocaptcha_recaptcha.fields import NoReCaptchaField
from general.modelfield_choices import HOW_DID_YOU_FIND_US, INDUSTRY, PAYMENT, TITLE
from shoppingCenter.models import AddInventory


class UserForm(forms.ModelForm):
    first_name = forms.CharField(help_text="First Name", required=True,
                                 widget=forms.TextInput(attrs={'placeholder': 'First Name', 'required': 'required'}))
    last_name = forms.CharField(help_text="Last Name", required=True,
                                widget=forms.TextInput(attrs={'placeholder': 'Last Name', 'required': 'required'}))
    username = forms.CharField(help_text="Username", required=True,
                               widget=forms.TextInput(attrs={'placeholder': 'Username', 'required': 'required'}))
    email = forms.EmailField(help_text="E-Mail", required=True,
                             widget=forms.TextInput(attrs={'placeholder': 'Email Address', 'required': 'required'}))
    password = forms.CharField(help_text="Password", required=True,
                               widget=forms.PasswordInput(attrs={'placeholder': 'Password', 'required': 'required'}))
    password1 = forms.CharField(help_text="Verify Password", required=True, widget=forms.PasswordInput(
        attrs={'placeholder': 'Verify Password', 'required': 'required'}))

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email', 'password', 'password1')

    def clean_username(self):
        username = self.cleaned_data['username']
        try:
            User.objects.get(username=username)
        except:  # User.DoesNotExist:
            return username
        raise forms.ValidationError('The username is already taken, please select another.')

    def clean_email(self):
        email = self.cleaned_data['email']
        try:
            User.objects.get(email=email)
        except:  # User.DoesNotExist:
            return email
        raise forms.ValidationError('The email address is already taken, please select another.')

    # if email and User.objects.filter(email=email).count() > 1:
    # 	raise forms.ValidationError('The email address is already taken, please select another.')
    # return email

    def clean_password1(self):
        if self.cleaned_data['password'] != self.cleaned_data['password1']:
            raise forms.ValidationError("The passwords did not match.  Please try again.")
        return self.cleaned_data['password1']

# def clean_password(self):
# 	first_name =  self.cleaned_data['first_name']
# 	last_name =  self.cleaned_data['last_name']
# 	password = self.cleaned_data['password']
# 	if 'password' in self.cleaned_data and 'password1' in self.cleaned_data:
# 		if self.cleaned_data['password'] != self.cleaned_data['password1']:
# 			raise forms.ValidationError('The passwords did not match. Please try again.')
# 		password = self.cleaned_data.get('password')
# 		if len(password) < 6:
# 			raise forms.ValidationError('Your password must be at least 6 characters long.')
# 		if not password.isalnum():
# 			raise forms.ValidationError('Your password must contain number')
# 		if self.cleaned_data['password'] == first_name:
# 			raise forms.ValidationError('Your password must not be the same with first name')
# 		if self.cleaned_data['password'] == last_name:
# 			raise forms.ValidationError('Your password must not be the same with last name')
# 	return self.cleaned_data


class SubscriberForm(forms.ModelForm):
    photo_id = forms.ImageField(help_text='Photo', required=True)
    address1 = forms.CharField(help_text="Address1",
                               widget=forms.TextInput(attrs={'placeholder': 'Address1', 'required': 'required'}))
    address2 = forms.CharField(help_text="Address2",
                               widget=forms.TextInput(attrs={'placeholder': 'Address2', 'required': 'required'}))
    city = forms.CharField(help_text="City",
                           widget=forms.TextInput(attrs={'placeholder': 'City', 'required': 'required'}))
    phone_number = forms.CharField(help_text="Phone Number", widget=forms.TextInput(
        attrs={'placeholder': 'Phone Number', 'required': 'required'}))
    zip_code = forms.CharField(help_text="Zip Code",
                               widget=forms.TextInput(attrs={'placeholder': 'Zip Code', 'required': 'required'}))
    state = forms.CharField(help_text="State",
                            widget=forms.TextInput(attrs={'placeholder': 'State', 'required': 'required'}))
    country = forms.CharField(help_text="Country",
                              widget=forms.TextInput(attrs={'placeholder': 'Country', 'required': 'required'}))

    class Meta:
        model = Subscriber
        fields = ('address1', 'address2', 'city', 'phone_number', 'zip_code', 'state', 'country', 'photo_id',)


class RegistrationInfo(forms.ModelForm):
    first_name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'First Name', 'class': 'form-control'}),
                                 error_messages={'required': 'Please provide your first name.'})
    last_name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Last Name', 'class': 'form-control'}),
                                error_messages={'required': 'Please provide your last name.'})
    # telephone       = forms.CharField(error_messages = {'required': 'Please provide your telephone.'})
    how_did_you_find_us = forms.ChoiceField(choices=HOW_DID_YOU_FIND_US, widget=forms.Select(
        attrs={'class': 'form-control', 'style': 'height: 36px;'}),
                                            error_messages={'required': 'Please how did you get to know about us.'})
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Username', 'class': 'form-control'}),
                               error_messages={'required': 'Please provide your username.'})
    email = forms.EmailField(label=(u'Email Address'),
                             widget=forms.TextInput(attrs={'placeholder': 'Email', 'class': 'form-control'}),
                             error_messages={'required': 'Please provide your email address.'})
    password = forms.CharField(label=(u'Password'),
                               widget=forms.PasswordInput(attrs={'placeholder': 'Password', 'class': 'form-control'}))
    password1 = forms.CharField(label=(u'Verify Password'), widget=forms.PasswordInput(
        attrs={'placeholder': 'Confirm Password', 'class': 'form-control'}))

    # how_did_you_find_us = forms.ChoiceField(choices = HOW_DID_YOU_FIND_US, error_messages = {'required': 'Please how did you get to know about us.'})
    # captcha         = CaptchaField()
    # captcha         = NoReCaptchaField()

    def __init__(self, *args, **kwargs):
        self.marketer = kwargs.pop('marketer', None)
        super(RegistrationInfo, self).__init__(*args, **kwargs)

    class Meta:
        abstract = True
        exclude = ('',)

    def clean_username(self):
        username = self.cleaned_data['username']
        # print 'self.markerter: ',self.marketer
        try:
            User.objects.get(username=username, useraccount__marketer=self.marketer)
        except:  # User.DoesNotExist:
            return username
        raise forms.ValidationError('The username is already taken, please select another.')

    def clean_email(self):
        email = self.cleaned_data['email']
        try:
            User.objects.get(email=email, useraccount__marketer=self.marketer)
        except:  # User.DoesNotExist:
            return email
        raise forms.ValidationError('The email address is already taken, please select another.')

    def clean(self):
        if 'password' in self.cleaned_data and 'password1' in self.cleaned_data:
            if self.cleaned_data['password'] != self.cleaned_data['password1']:
                raise forms.ValidationError('The passwords did not match. Please try again.')
            password = self.cleaned_data.get('password')
            if len(password) < 6:
                raise forms.ValidationError('Your password must be at least 6 characters long.')
        return self.cleaned_data


class UserAccountForm(RegistrationInfo):
    class Meta:
        model = UserAccount
        fields = ('how_did_you_find_us', 'username', 'email', 'password', 'password1',)  # 'captcha',)

    def clean_username(self):
        username = self.cleaned_data['username']
        try:
            User.objects.get(username=username)
        except:  # User.DoesNotExist:
            return username
        raise forms.ValidationError('The username is already taken, please select another.')


class BusinessAccountForm(RegistrationInfo):
    # first_name      = forms.CharField(error_messages = {'required': 'Please provide your first name.'})
    # last_name       = forms.CharField(error_messages = {'required': 'Please provide your last name.'})
    telephone = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Telephone'}),
                                error_messages={'required': 'Please provide your telephone.'})
    company_name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Company Name'}),
                                   error_messages={'required': 'Please provide your Company Name.'})
    industry = forms.ChoiceField(choices=INDUSTRY, error_messages={'required': 'Please select your Industry.'})
    enquiry = forms.CharField(widget=forms.Textarea(attrs={'rows': 3, 'placeholder': "Enquiry"}),
                              error_messages={'required': 'Please let us know your enquiry.'})
    # username        = forms.CharField(error_messages = {'required': 'Please provide your username.'})
    # email           = forms.EmailField(label=(u'Email Address'), error_messages={'required': 'Please provide your email address.'})
    # password        = forms.CharField(label=(u'Password'), widget=forms.PasswordInput)
    # password1       = forms.CharField(label=(u'Verify Password'), widget=forms.PasswordInput)
    captcha = NoReCaptchaField()

    class Meta:
        model = UserAccount
        # exclude = ('user','registration_time', 'activation_code', 'credit_amount', 'pending_amount',
        #            'title', 'address', 'city', 'state', 'country', 'suite_no', 'postal_code', 'address_activation',
        #            'assigned_rate_af', 'assigned_minimum_af','assigned_rate_sf', 'assigned_minimum_sf',
        #            'assigned_rate_af_percentage', 'assigned_rate_sf_percentage',)
        fields = ('how_did_you_find_us', 'company_name', 'industry', 'enquiry',
                  'telephone', 'username', 'email', 'password', 'password1', 'captcha',)


class LoginForm(forms.Form):
    username_email = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Username or Email address', 'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password', 'class': 'form-control'}))
# username_email          = forms.CharField(label=(u'E-mail'),widget=forms.TextInput(attrs={'size': '30', 'placeholder': 'Username or Email address', 'required': 'True'}))
# password                = forms.CharField(label=(u'Password'), widget=forms.PasswordInput(attrs={'placeholder': 'Password', 'required': 'True'}))


class EditProfileForm(forms.ModelForm):
    first_name = forms.CharField(widget=forms.TextInput(attrs={'readonly': 'True'}))
    last_name = forms.CharField(widget=forms.TextInput(attrs={'readonly': 'True'}))

    # country    = forms.CharField(widget=forms.TextInput(attrs={'readonly': 'True'}))

    class Meta:
        model = UserAccount
        fields = ('first_name', 'last_name', 'address', 'city', 'telephone', 'image')  # 'state',)


class EditSubscriberProfileForm(forms.ModelForm):
    first_name = forms.CharField(widget=forms.TextInput(attrs={'readonly': 'True'}))
    last_name = forms.CharField(widget=forms.TextInput(attrs={'readonly': 'True'}))
    address1 = forms.CharField(help_text="Address1", required=True,
                               widget=forms.TextInput(attrs={'placeholder': 'Address1', 'required': 'required'}))
    address2 = forms.CharField(help_text="Address2", required=True,
                               widget=forms.TextInput(attrs={'placeholder': 'Address2', 'required': 'required'}))
    city = forms.CharField(help_text="City", required=True,
                           widget=forms.TextInput(attrs={'placeholder': 'City', 'required': 'required'}))
    phone_number = forms.CharField(help_text="Phone Number", required=True, widget=forms.TextInput(
        attrs={'placeholder': 'Phone Number', 'required': 'required'}))
    zip_code = forms.CharField(help_text="Zip Code", required=True,
                               widget=forms.TextInput(attrs={'placeholder': 'Zip Code', 'required': 'required'}))
    state = forms.CharField(help_text="State", required=True,
                            widget=forms.TextInput(attrs={'placeholder': 'State', 'required': 'required'}))
    country = forms.CharField(help_text="Country", required=True,
                              widget=forms.TextInput(attrs={'placeholder': 'Country', 'required': 'required'}))
    photo_id = forms.ImageField(help_text='Photo', required=True)

    class Meta:
        model = Subscriber
        fields = (
        'first_name', 'last_name', 'address1', 'address2', 'city', 'phone_number', 'zip_code', 'state', 'country',
        'photo_id')


def validate_bank_account_no(value):
    len_value = len(value)
    if (len_value < 10 or len_value > 10) and value.isdigit():
        raise ValidationError('Please provide NUBAN 10 digits Bank Account Number. (It currently has %s)' % len_value)


def validate_bvn_no(value):
    len_value = len(value)
    if (len_value < 11 or len_value > 11) and value.isdigit():
        raise ValidationError('Please provide 11 digits BVN Number. (It currently has %s)' % len_value)


class AddressActivationForm(forms.ModelForm):
    bvn_no = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'BVN Number', 'class': 'form-control'}))
    first_name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'First Name', 'class': 'form-control'}),
                                 error_messages={'required': 'Please provide your first name.'})
    last_name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Last Name', 'class': 'form-control'}),
                                error_messages={'required': 'Please provide your last name.'})
    title = forms.ChoiceField(choices=TITLE, required=True, widget=forms.Select(
        attrs={'placeholder': 'Title', 'required': 'required', 'class': 'form-control'}))
    address = forms.CharField(required=True, widget=forms.TextInput(
        attrs={'placeholder': 'Address1', 'required': 'required', 'class': 'form-control'}))
    city = forms.CharField(required=True, widget=forms.TextInput(
        attrs={'placeholder': 'Address1', 'required': 'required', 'class': 'form-control'}))
    photo_id = forms.ImageField(required=True, widget=forms.FileInput(attrs={'class': 'form-control'}))
    image = forms.ImageField(required=True, widget=forms.FileInput(attrs={'class': 'form-control'}))
    utility_bill = forms.ImageField(required=True, widget=forms.FileInput(attrs={'class': 'form-control'}))

    # bank_account_no = forms.CharField(validators=[MinLengthValidator(10), MaxLengthValidator(10)])
    # bank_account_no = forms.CharField(validators=[validate_bank_account_no])
    # bvn_no = forms.CharField(validators=[validate_bvn_no])

    class Meta:
        model = UserAccount
        fields = (
        'title', 'first_name', 'last_name', 'address', 'city', 'country', 'image', 'state', 'bvn_no', 'photo_id',
        'utility_bill',)


# address activation form for Nigerians
class AddressActivationFormNG(AddressActivationForm):
    def __init__(self, *args, **kwargs):
        super(AddressActivationForm, self).__init__(*args, **kwargs)
        self.fields["photo_id"].required = False
        self.fields["utility_bill"].required = False


class AddressActivationForm1(AddressActivationFormNG):
    def __init__(self, *args, **kwargs):
        super(AddressActivationForm1, self).__init__(*args, **kwargs)
    # self.fields["bank"].required = False
    # self.fields["bank_account_no"].required = False


class AddressActivationForm2(AddressActivationFormNG):
    def __init__(self, *args, **kwargs):
        super(AddressActivationForm2, self).__init__(*args, **kwargs)
        self.fields["bvn_no"].required = False


# address activation form for Non-Nigerians
class AddressActivationForm3(AddressActivationForm):
    def __init__(self, *args, **kwargs):
        super(AddressActivationForm, self).__init__(*args, **kwargs)
        # self.fields["bank"].required = False
        # self.fields["bank_account_no"].required = False
        self.fields["bvn_no"].required = False


# class EditBusinessProfileForm(forms.ModelForm):
#     first_name = forms.CharField(widget=forms.TextInput(attrs={'readonly': 'True'}))
#     last_name  = forms.CharField(widget=forms.TextInput(attrs={'readonly': 'True'}))
#     country    = forms.CharField(widget=forms.TextInput(attrs={'readonly': 'True'}))
#
#     class Meta:
#         model = UserAccount
#         exclude = ('user', 'title', 'postal_code', 'username', 'suite_no', 'activation_code', 'registration_time', 'credit_amount', 'pending_amount',
#                    'enquiry','business_account', 'how_did_you_find_us','address_activation',)
#                     #'assigned_rate_af', 'assigned_minimum_af', 'assigned_rate_sf', 'assigned_minimum_sf', 'assigned_rate_af_percentage', 'assigned_rate_sf_percentage',)
#
# class EditBusinessProfileForm1(forms.ModelForm):
#     class Meta:
#         model = UserAccount
#         fields = ('assigned_rate_af', 'assigned_rate_sf', 'assigned_minimum_af', 'assigned_minimum_sf',)


class ComposeMessageForm(ModelForm):
    # booking_ref = forms.ChoiceField(choices = Shipment.objects.filter(user = request.user))
    class Meta:
        model = MessageCenter
        fields = ('related_to', 'booking_ref', 'message',)


class paymentTypeForm(forms.Form):
    payment_type = forms.ChoiceField(widget=forms.RadioSelect, choices=PAYMENT)
    accept_terms = forms.BooleanField(required=True)

    class Meta:
        # model = Shipment
        fields = ('payment_type', 'accept_terms',)


class JoinWaitingListForm(forms.ModelForm):
    class Meta:
        model = JoinWaitingList
        fields = ('joined_on', 'email',)


class SetPasswordForm(forms.Form):
    """
	A form that lets a user change set their password without entering the old
	password
	"""
    # error_messages = {
    # 	'password_mismatch': _("The two password fields didn't match."),
    # }
    new_password1 = forms.CharField(label=("New password"),
                                    widget=forms.PasswordInput)
    new_password2 = forms.CharField(label=("New password confirmation"),
                                    widget=forms.PasswordInput)

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(SetPasswordForm, self).__init__(*args, **kwargs)

    def clean_new_password2(self):
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError(
                    self.error_messages['password_mismatch'],
                    code='password_mismatch',
                )
        return password2


class CheckoutForm(forms.ModelForm):
    first_name = forms.CharField(help_text="First Name", required=True,
                                 widget=forms.TextInput(attrs={'placeholder': 'First Name', 'required': 'required'}))
    last_name = forms.CharField(help_text="Last Name", required=True,
                                widget=forms.TextInput(attrs={'placeholder': 'Last Name', 'required': 'required'}))
    address1 = forms.CharField(help_text="Address1", required=True,
                               widget=forms.TextInput(attrs={'placeholder': 'Address1', 'required': 'required'}))
    address2 = forms.CharField(help_text="Address2", required=True,
                               widget=forms.TextInput(attrs={'placeholder': 'Address2', 'required': 'required'}))
    city = forms.CharField(help_text="City", required=True,
                           widget=forms.TextInput(attrs={'placeholder': 'City', 'required': 'required'}))
    email = forms.CharField(help_text="Email", required=True,
                            widget=forms.TextInput(attrs={'placeholder': 'Email Address', 'required': 'required'}))
    zip_code = forms.CharField(help_text="Zip Code", required=True,
                               widget=forms.TextInput(attrs={'placeholder': 'Zip Code', 'required': 'required'}))
    state = forms.CharField(help_text="State", required=True,
                            widget=forms.TextInput(attrs={'placeholder': 'State', 'required': 'required'}))
    country = forms.CharField(help_text="Country", required=True,
                              widget=forms.TextInput(attrs={'placeholder': 'Country', 'required': 'required'}))

    class Meta:
        model = Subscriber
        fields = ('first_name', 'last_name', 'address1', 'address2', 'city', 'email', 'zip_code', 'state', 'country')


class InventoryForm(forms.ModelForm):
    title = forms.CharField(help_text="Title", required=True, widget=forms.TextInput(
        attrs={'placeholder': 'Title', 'required': 'required', 'style': "width:465;"}))
    description = forms.CharField(help_text="Description", required=True, widget=forms.Textarea(
        attrs={'placeholder': 'Description', 'required': 'required', 'cols': 10, 'rows': 3}))
    price = forms.CharField(help_text="Price", required=True, widget=forms.TextInput(
        attrs={'type': 'number', 'placeholder': 'Price', 'required': 'required'}))
    colour = forms.CharField(help_text="Colour", required=True, widget=forms.TextInput(
        attrs={'placeholder': 'Colour', 'required': 'required', 'style': "width:465;"}))
    brand = forms.CharField(help_text="Brand", required=True, widget=forms.TextInput(
        attrs={'placeholder': 'Brand', 'required': 'required', 'style': "width:465;"}))
    size = forms.CharField(help_text="Size", required=True, widget=forms.TextInput(
        attrs={'type': 'number', 'placeholder': 'Size', 'required': 'required'}))
    category = forms.CharField(help_text="Category", required=True, widget=forms.TextInput(
        attrs={'placeholder': 'Category', 'required': 'required', 'style': "width:465;"}))
    sub_sub_cat = forms.CharField(help_text="Sub Category", required=True, widget=forms.TextInput(
        attrs={'placeholder': 'SubCategory', 'required': 'required', 'style': "width:465;"}))
    quantity = forms.CharField(help_text="Quantity", required=True, widget=forms.TextInput(
        attrs={'type': 'number', 'placeholder': 'Quantity', 'required': 'required'}))
    sold = forms.CharField(help_text="Sold", required=True, widget=forms.TextInput(
        attrs={'type': 'number', 'placeholder': 'Sold', 'required': 'required'}))
    weight = forms.CharField(help_text="weight", required=True, widget=forms.TextInput(
        attrs={'type': 'number', 'placeholder': 'Weight', 'required': 'required', 'style': "width:465;"}))

    class Meta:
        model = AddInventory
        fields = ('colour', 'brand', 'size', 'quantity', 'price', 'sold', 'description', 'title', 'category', 'weight')
