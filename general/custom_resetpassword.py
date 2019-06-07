from django.contrib.auth.forms import forms, force_bytes, urlsafe_base64_encode, default_token_generator,loader,EmailMultiAlternatives
from django.contrib.auth.views import HttpResponseRedirect, csrf_protect, reverse, _, TemplateResponse
#from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from general.custom_functions import marketing_member

class CustomPasswordResetForm(forms.Form):

    email = forms.EmailField(label=_("Email"), max_length=254)
    #
    def __init__(self, *args, **kwargs):
        self.marketer = kwargs.pop('marketer', None)
        self.subdomain_name = kwargs.pop('subdomain_name', None)
        self.storefront_name = kwargs.pop('storefront_name', None)
        super(CustomPasswordResetForm, self).__init__(*args, **kwargs)

    def send_mail(self, subject_template_name, email_template_name,
                  context, from_email, to_email, html_email_template_name=None):
        """
        Sends a django.core.mail.EmailMultiAlternatives to `to_email`.
        """
        subject = loader.render_to_string(subject_template_name, context)
        # Email subject *must not* contain newlines
        from_email = '{} <{}>'.format(self.marketer.storefront_name, self.marketer.email)
        subject = ''.join(subject.splitlines())
        body = loader.render_to_string(email_template_name, context)

        email_message = EmailMultiAlternatives(subject, body, from_email, [to_email])
        if html_email_template_name is not None:
            html_email = loader.render_to_string(html_email_template_name, context)
            email_message.attach_alternative(html_email, 'text/html')

        email_message.send()

    def get_users(self, email):
        """Given an email, return matching user(s) who should receive a reset.

        This allows subclasses to more easily customize the default policies
        that prevent inactive users and users with unusable passwords from
        resetting their password.

        """
        active_users = get_user_model()._default_manager.filter(
            email__iexact=email, is_active=True,
            useraccount__marketer = self.marketer)#added for marketer filter
        return (u for u in active_users if u.has_usable_password())

    def save(self, domain_override=None,
             subject_template_name='registration/password_reset_subject.txt',
             email_template_name='registration/password_reset_email.html',
             use_https=False, token_generator=default_token_generator,
             from_email=None, request=None, html_email_template_name=None):
        """
        Generates a one-use only link for resetting password and sends to the
        user.
        """
        email = self.cleaned_data["email"]
        #marketer = user.useraccount.marketer
        #user = get_object_or_404(User, email = email, useraccount__marketer = self.marketer)
        for user in self.get_users(email):
            context = {
                'email': user.email,
                'domain': self.subdomain_name,
                'site_name': self.storefront_name,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'user': user,
                'token': token_generator.make_token(user),
                'protocol': 'https' if use_https else 'http',
            }

            self.send_mail(subject_template_name, email_template_name,
                           context, from_email, user.email,
                           html_email_template_name=html_email_template_name)



@csrf_protect
def custom_password_reset(request,
                   template_name=None,
                   email_template_name = 'registration/password_reset_email.html',
                   subject_template_name='registration/password_reset_subject.txt',
                   password_reset_form=CustomPasswordResetForm,
                   token_generator=default_token_generator,
                   post_reset_redirect=None,
                   from_email=None,
                   extra_context=None,
                   html_email_template_name=None,
                   extra_email_context=None):
    # warnings.warn("The password_reset() view is superseded by the "
    #               "class-based PasswordResetView().",
    #               RemovedInDjango21Warning, stacklevel=2)
    marketer = marketing_member(request)
    if post_reset_redirect is None:
        post_reset_redirect = reverse('password_reset_done')
    else:
        post_reset_redirect = resolve_url(post_reset_redirect)
    if request.method == "POST":
        if marketer.storefront_name == "volkmannexpress":
            template_name = 'registration/password_reset_form_volk.html'
        else:
            template_name = 'registration/password_reset_form.html'
        kwargs = {'marketer': marketer, 'subdomain_name': marketer.subdomain_name,
                'storefront_name': marketer.storefront_name}
        form = password_reset_form(request.POST, **kwargs)
        if form.is_valid():
            opts = {
                'use_https': request.is_secure(),
                'token_generator': token_generator,
                'from_email': from_email,
                'email_template_name': email_template_name,
                'subject_template_name': subject_template_name,
                'request': request,
                'html_email_template_name': html_email_template_name,
                #'extra_email_context': extra_email_context,
            }
            form.save(**opts)
            return HttpResponseRedirect(post_reset_redirect)
    else:
        form = password_reset_form()
    context = {
        'form': form,
        'title': _('Password reset'),
    }
    if extra_context is not None:
        context.update(extra_context)

    if marketer.storefront_name == "volkmannexpress":
        template_name = 'registration/password_reset_form_volk.html'
    else:
        template_name = 'registration/password_reset_form.html'

    return TemplateResponse(request, template_name, context)


def custom_password_reset_done(request,
                        template_name=None,
                        current_app=None, extra_context=None):
    context = {
        'title': _('Password reset sent'),
    }

    marketer = marketing_member(request)

    if marketer.storefront_name == "volkmannexpress":
        template_name = 'registration/password_reset_done_volk.html'
    else:
        template_name = 'registration/password_reset_done.html'

    if extra_context is not None:
        context.update(extra_context)

    if current_app is not None:
        request.current_app = current_app

    return TemplateResponse(request, template_name, context)

