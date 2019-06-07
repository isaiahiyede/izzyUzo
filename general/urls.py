from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView
from django.contrib import admin
from django.conf import settings
import bvn_validation
import views, paystack_helpers
import sokohali_views, group_access
import user_profile
from django.views.generic import TemplateView

from general.models import *


user_account = [
                url(r'^user-account/profile/(?P<username>.+)/$', user_profile.profile, name='profile'),
                url(r'^user-account/edit-profile/(?P<username>.+)/$', user_profile.edit_profile, name='edit_profile'),
                url(r'^volk/user-account/profile/(?P<username>.+)/$', user_profile.profile_volk, name='profile_volk'),
                url(r'^volk/user-account/edit-profile/(?P<username>.+)/$', user_profile.edit_profile_volk, name='edit_profile_volk'),
                url(r'^user-account/address-activation/(?P<username>.+)/$', user_profile.address_activation, name='address_activation'),
                url(r'^volk/user-account/address-activation/(?P<username>.+)/$', user_profile.address_activation_new, name='address_activation_new'),
                url(r'^user-account/bvn/verification/$', bvn_validation.verify, name ="verify_bvn"),
                url(r'^user-account/otp/verification/$', bvn_validation.enter_otp, name ="enter_otp"),
                url(r'^user-account/otp/validation/$', bvn_validation.validation_result, name ="validate_otp"),
                url(r'^user-account/resend/otp/$',bvn_validation.resend_otp, name="resend_otp"),
]


sokohali_urls = [
                 url(r'^sokohali/logout/$', sokohali_views.sokohali_logout, name="sokohali-logout"),
                 url(r'^business-settings/$', sokohali_views.business_settings, name="business_settings"),
                 url(r'^about/$', sokohali_views.about, name="about"),
                 url(r'^demo/$', sokohali_views.demopage, name="demopage"),
                 url(r'^contact/$', sokohali_views.contact, name="contact"),
                 url(r'^legal/$', sokohali_views.legal, name="legal"),
                 url(r'^login/$', sokohali_views.LoginSubscriber.as_view(), name="subscriber_login"),
                 url(r'^register/$', sokohali_views.register, name="subscriber_register"),
                 url(r'^sokohali/subscriber-profile/(?P<username>.+)/$', sokohali_views.subscriber_profile, name='subscriber_profile'),
                 url(r'^sokohali/subscriber-edit-profile/(?P<username>.+)/$', sokohali_views.subscriber_edit_profile, name='subscriber_edit_profile'),
                 url(r'^password/$', sokohali_views.change_password, name='change_password'),
                 url(r'^passwordrequest/$', sokohali_views.passwordrequest, name='passwordrequest'),

]

urlpatterns = [

                url(r'^', include(user_account)),
                url(r'^', include(sokohali_urls)),


                url(r'^user/login/$', views.LoginRequest.as_view(), name="login"),
                url(r'^volk/login/$', views.LoginRequestNew.as_view(), name="volkLogin"),
                url(r'^user/logout/$', views.logoutRequest, name="logout"),
                url(r'^user/signup/$', views.userregistration_regular, name="signup_regular"),
                url(r'^user/suspension/$', views.suspension, name="suspension"),
                url(r'^marketer-home/$', views.homepage, name="marketer_home"),
                url(r'^domestic-shipping/$', views.domestic_shipping, name='domestic'),
                url(r'^contact-us-volk/$', views.contact_us_volk, name="contact_us_volk"),
                url(r'^contact-us/$', views.contact_us, name="contact_us"),
                url(r'^shopForMe/$', views.vei_shopper, name="vei_shopper"),
                
                url(r'^zeac/contact-us/$', views.zeac_contct_us, name="zeac_contct_us"),

                url(r'^shopping/(?P<action>.+)/(?P<item_id>[-\w]+)/(?P<amount>\d+\.\d{1})/$', views.crud_pay_for_shop, name="crud_pay_for_shop"),
                url(r'^get-dropoff-locations', views.get_dropoff_locations, name="get_dropoff_locations"),
                url(r'^get-location-address', views.get_location_address, name="get_location_address"),
                url(r'^get-country-regions', views.get_country_regions, name="get_country_regions"),
                url(r'^distributor_api_or_rates', views.distributor_api_or_rates, name="distributor_api_or_rates"),
                url(r'^warehouse-address', views.get_warehouse_address, name = "get_warehouse_address"),
                url(r'^my-account/$', views.user_account, name="my_account"),
                url(r'^dst-warehouse-address', views.get_destination_addresses, name = "get_destination_addresses"),
                url(r'^my-shipments/$', views.my_shipments, name="my_shipments"),
                url(r'^volk/shipments/$', views.my_shipments_volk, name="my_shipments_volk"),
                url(r'^my-orders/$', views.my_orders, name="my_orders"),
                url(r'^my-payments/$', views.my_soko_pay_info, name="my_payments"),
                url(r'^volk/payments/$', views.my_soko_pay_info_volk, name="my_payments_volk"),
                url(r'^my-messages/$', views.my_messages, name="my_messages"),
                url(r'^volk/messages/$', views.my_messages_volk, name="my_messages_volk"),
                url(r'^check-avaliable-routes/$', views.check_avaliable_routes, name="check_avaliable_routes"),
                url(r'^my-delivery-addresses/$', views.view_delivery_addresses, name="delivery-addresses"),
                url(r'^volk/delivery-addresses/$', views.view_delivery_addresses_volk, name="delivery_addresses_volk"),
                url(r'^my-mail-bag/$', views.my_mail_bag, name="my_mail_bag"),
                url(r'^volk/mail-bag/$', views.my_mail_bag_volk, name="my_mail_bag_volk"),
                url(r'^paystack/verifyPayment/$',paystack_helpers.verify_payment, name="verifyPayment"),
                url(r'^my-shipment/(\d+)/cancel/$', views.cancel_shipment, name="cancel_shipment"),
                url(r'^FAQ/$', views.marketerFAQ, name = "faq"),
                url(r'^terms-and-conditions/$', views.legal, name = "legal"),
                url(r'^auto-deals/$', views.iaai, name = "iaai"),
                url(r'^waitinglist/$', views.joinwaitinglist, name="joinwaitinglist"),
                url(r'^sendmail/(?P<username>.+)/(?P<subject>.+)/(?P<text>.+)$', views.sendmail, name="sendmail"),
                url(r'^marketer-addon/(?P<action>.+)/$',views.marketer_addons, name="marketer_addons"),
                url(r'^view_edit_shopping_item_order/$',views.view_edit_shopping_item_order, name="view_edit_shopping_item_order"),
                url(r'^edit_shop_request/$',views.edit_shop_request, name="edit_shop_request"),
                
                url(r'^product-view/$', views.product_view, name="product_view"),
                url(r'^detail-view/(?P<item_id>[-\w]+)/$', views.detail_view, name='detail_view'),
                url(r'^cart-view/$', views.cart_view, name="cart_view"),
                url(r'^delete-item/(?P<item_id>[-\w]+)/$', views.delete_item, name='delete_item'),
                url(r'^delete-inv-item/(?P<item_id>[-\w]+)/$', views.del_inv, name='del_inv'),
                url(r'^edit-inv-item/$', views.edit_inv, name='edit_inv'),
                url(r'^inv-edited/$', views.inv_edited, name='inv_edited'),
                url(r'^view-item/$', views.view_item, name='view_item'),
                url(r'^inv-sidebar-category/$', views.inv_sidebar_category, name='inv_sidebar_category'),
                url(r'^checkout/$', views.checkout, name="checkout"),
                url(r'^checking-out-page/$', views.checking_out, name="checking_out"),
                url(r'^order-summary/$', views.order_summary, name="order_summary"),
                url(r'^add-to-cart/$', views.add_to_cart, name="add_to_cart"),
                url(r'^add-inventory/$', views.add_inventory, name="add_inventory"),
                url(r'^inventory/history/(?P<item_id>[0-9]+)$', views.inv_history, name="inventory_history"),
                url(r'^pay-options/$', views.pay_options, name="pay_options"),
                url(r'^order-confirmation/$', views.order_confirmation, name="order_confirmation"),
                url(r'^track_shipments/$', views.track_shipments, name="track_shipments"),
                url(r'^volk/shipment-detail/$', views.shipment_detail_volk, name="shipment_detail_volk"),
                url(r'^volk/detail-shipment/$', views.shipment_detail_number_volk, name="shipment_detail_number_volk"),
                url(r'^volk/shipment-tracker/$', views.my_tracker_volk, name="my_tracker_volk"),
                

                # quick estimate
                url(r'^quick-estimate$', views.quickEstimate, name="quick-estimate"),

                # test label printing
                url(r'^print-label$', views.test_label_printing, name="test_label_printing"),

                # pay-pal
                url(r'^confirm_paypal_payment/$', views.confirm_paypal_payment, name="confirm_paypal_payment"),

                # ebiz
                url(r'^confirm_ebiz_payment/$', views.confirm_ebiz_payment, name="confirm_ebiz_payment"),

                # staff access 
                url(r'^admin-access/(?P<user_obj>.+)/$', group_access.admin_access, name="admin_access"),
                url(r'^zeac/estimate/$', views.get_estimate, name="get_estimate"),
                # url(r'^subscribers-password/$', sokohali_views.change_password, name='change_password'),

]
