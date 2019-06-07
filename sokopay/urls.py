from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView
#from views import add_funds, user_transactions, pay_with_zappay_credit, pay_by_bank_deposit
import views

from general.paystack import verify_transaction
from general import flutterwave_helpers

urlpatterns = [
            url(r'^$', TemplateView.as_view(template_name = 'soko_pay/soko_pay.html'), name="soko_pay"),
            url(r'^transactions/$', views.user_transactions, name="user_transactions"),
            url(r'^add-funds/$', views.add_funds, name="add_funds"),
            url(r'^add-funds-volk/$', views.add_funds_volk, name="add_funds_volk"),
            url(r'^funds-volk-card/$', views.add_funds_volk_card, name="add_funds_volk_card"),
            url(r'^add-funds-card/$', views.buy_jejepay_credit_card, name="buy_jejepay_credit_card"),
            url(r'^add-funds-page/$', TemplateView.as_view(template_name = 'soko_pay/add_funds_landing_page.html'), name="add_funds_landing_page"),
            url(r'^subscriber/card-payment/$', views.SubCardPayment, name="sub_card_payment"),
            url(r'^select-payment-option/$', views.select_payment_option, name="select_payment_option"),
            url(r'^pay-balance/$', views.pay_balance, name="pay_balance"),
            url(r'^pay_for_shipments/$', views.pay_for_shipments, name="pay_for_shipments"),
            url(r'^pay_for_package/$', views.pay_for_package, name="pay_for_package"),
            #flutterwave callback url
            url(r'^intl-card-verification/$', flutterwave_helpers.intl_card_verification, name='intl_card_verification'),
            url(r'^complete-intl-card/$', flutterwave_helpers.complete_intl_card, name='complete_intl_card'),

            #paystack callback url
            url(r'^paystack/(?P<jejepay_ref>\d+)/(?P<dest_namespace>.+)/$', verify_transaction, name="paystack_verify_transaction"),
            url(r'^pay-with-zappay-credit/(?P<shop_or_ship>.+)/(?P<id>.+)/$', views.pay_with_zappay_credit, name="pay_with_zappay_credit"),
            url(r'^pay-by-bank-deposit/(?P<id>.+)/$', views.pay_by_bank_deposit, name="pay_by_bank_deposit"),
            url(r'^subscriber/payment/$', views.subscriberPayment, name ="sub_payments"),
            
            #url(r'^select-payment-option/(?P<shop_or_ship>.+)/(?P<id>.+)/$', views.select_payment_option, name="select_payment_option"),

    ]
