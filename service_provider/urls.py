from django.conf.urls import patterns, include, url
from django.conf import settings
import views

from django.contrib.auth.views import password_reset, password_reset_done, password_reset_confirm, password_reset_complete
from django.contrib.auth import views as auth_views


urlpatterns = [

            url(r'^country-settings/$', views.country_settings, name="country_settings"),
            url(r'^customisable-website/activate/$', views.configure_setup, name="configure_setup"),
            url(r'^add-fixed-weight-shipment/$', views.add_fixed_weight_shipment, name="add_fixed_weight_shipment"),
            url(r'^fixed-weight-shipment-items/$', views.fixed_weight_shipment_items, name="fixed_weight_shipment_items"),
            url(r'^view-delivery-routes-rates/$', views.view_delivery_routes_rates, name="view_delivery_routes_rates"),
            url(r'^select-service/$', views.select_service, name="select_service"),
            url(r'^member-info/$', views.get_member_info, name="get_member_info"),
            #url(r'^member-info/(?P<member_type>.+)/(?P<id>\d+)/$', views.get_member_info, name="get_member_info"),
            url(r'^service/shipping/$', views.setup, name="add_service"),
            url(r'^offer/services/$', views.offer_services, name="offer_services"),
            url(r'edit/cost-settings/$', views.edit_cost_settings, name="edit_cost_settings"),
            url(r'^marketing-member/terms-and-cond/$', views.editTermsConditions, name = "editTermsConditions"),
            url(r'^member/Email-template/$', views.emailtemplate, name = "emailtemplate_setup"),
            url(r'^member/Edit/email_template/$', views.edit_emailtemplate, name = "edit_emailform"),
            url(r'^Edit/FAQ/$', views.editFAQ, name = "editFaq"),
            # #change password urls for subscribers
            url(r'^password_reset/$', auth_views.password_reset, name='password_reset'),
            url(r'^password_reset/done/$', auth_views.password_reset_done, name='password_reset_done'),
            url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
                  auth_views.password_reset_confirm, name='password_reset_confirm'),
            url(r'^reset/done/$', auth_views.password_reset_complete, name='password_reset_complete'),
            url(r'^service-location/(?P<service_name>\w+?)/(?P<chain_id>\w+?)/$', views.add_warehouse_address, name ="service_location"),
            url(r'cost-settings/$', views.cost_settings, name="cost_settings"),
            url(r'dashboard/details/(?P<chain_id>\w+?)/$', views.dashboard_details, name="dashboard_details"),
            url(r'^loc-distr/$', views.create_local_dist, name='create_local_dist'),
            
]
