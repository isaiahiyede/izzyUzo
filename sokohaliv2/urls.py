from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from django.shortcuts import render, render_to_response

from django.template import RequestContext
from django.views.static import serve
from django.contrib.sitemaps.views import sitemap

from django.contrib.auth.views import password_reset, password_reset_done, password_reset_confirm, password_reset_complete

from general.user_profile import redirect_to_address_activation, redirect_to_address_activation_new
from general.custom_resetpassword import custom_password_reset, custom_password_reset_done
from general.views import homepage

from general.barcode_generator import create_test_barcode


#server error
def server_error(request):
    response = render(request, "500.html")
    response.status_code = 500
    return response

#page not found
def custom_404(request):
    response = render(request, "404.html")
    response.status_code = 404
    return response

#access denied
def access_denied(request):
    return render_to_response("access_denied.html", {},
                              context_instance=RequestContext(request))

handler404 = custom_404

handler500 = server_error


urlpatterns = [

    # url(r'^$', TemplateView.as_view(template_name = 'index.html'), name='homepage'),
    url(r'^$', homepage, name='homepage'),

    #temporary measure
    url(r'^marketer/$', homepage, name='marketer_homepage'),

    url(r'^', include("general.urls", namespace="general")),

    url(r'^adminVolkmann/', include(admin.site.urls)),

    url(r'^paypal/', include('paypal.standard.ipn.urls')),

    url(r'^payment/', include("payment.urls", namespace="payment")),

    url(r'^', include("veiwallet.urls", namespace="wallet")),

    url(r'^access-denied/$', access_denied, name='access_denied'),

    url(r'session_security/', include('session_security.urls')),

    url(r'^registration/successful/$', TemplateView.as_view(template_name = 'general_client/regsuccessful.html'), name="reg_successful"),

    url(r'^successful/reg/$', TemplateView.as_view(template_name = 'volkmann/registration_successful.html'), name="successful_reg"),

    #Address Activation
    url(r'^redirect_to_address_activation/', redirect_to_address_activation),

    url(r'^redirect_to_address_activation_new/', redirect_to_address_activation_new),

    #import shipping
    url(r'^shipping/', include('shipping.urls', namespace="shipping")),

    #pkg-processor
    url(r'^pkg-processor-api/', include('pkg_processor.urls')),

    url(r'^setup/', include("service_provider.urls", namespace="service_provider")),

    #SokohaliAdmin
    url(r'^backend/', include("sokohaliAdmin.urls", namespace="sokohaliAdmin")),

    url(r'^pay/', include('sokopay.urls', namespace = "soko_pay")),

    url(r'^shopping/', include('shoppingCenter.urls', namespace = "shoppingCenter")),

    url(r'^create-test-barcode/(?P<barcode_id>.+)/', create_test_barcode),

    #change password urls
    url(r'^reset/form/$', TemplateView.as_view(template_name = 'registration/password_reset_email.html')),
    url(r'^resetpassword/passwordsent/$', custom_password_reset_done, name="password_reset_done"),
    #url(r'^resetpassword/$', password_reset, name="password_reset"), custom_password_reset
    url(r'^resetpassword/$', custom_password_reset, name="password_reset"),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$', password_reset_confirm, name="password_reset_confirm"),
    url(r'^reset/done/$', password_reset_complete, name="password_reset_complete"),




]

urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
