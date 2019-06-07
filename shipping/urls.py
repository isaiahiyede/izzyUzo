from django.conf.urls import patterns, include, url
import views
from sokohaliAdmin.views import *

urlpatterns = [

        #url(r'^$', shipping, name="shipping"),

        #Shippyme Tracking
        #url(r'^tracking/$', fedex_tracking, name="shippyme_tracking"),
        url(r'save-item-data/$', views.save_item_data),
        url(r'del-item-data/$', views.del_item_data),
        url(r'get-user-items/$', views.get_user_items),

        url(r'^retrieve_modal_values', views.retrieve_modal_values, name="retrieve_modal_values"),

        url(r'get-local-freight-price', views.get_local_freight_cost, name='get_local_freight_cost'),

        #Quick Estimate
        #url(r'quick-estimate/$', views.select_package_size, name="quick_estimate"),#select_package)
        #url(r'quick-estimate/clearcart/$', views.quick_estimate_clear_cart, name="quick_estimate_clear_cart"),

        url(r'select-warehouse/$', views.select_warehouse, name="select_warehouse"),

        url(r'select-package-size/$', views.select_package_size, name="select_package"),

        url(r'package-information/$', views.package_information, name="add_item_page"),

        # get item is a package
        # url(r'get-items-in-package/$', views.get_items_in_package, name="get_items_in_package"),

        url(r'^select-shipping-address/$', views.select_shipping_address, name="shipping_address"),
        url(r'^shipping/del-user-item/$', views.user_del_item, name="user_del_item"),

        url(r'payment/$', views.payment_page, name="shipping_payment"),

        url(r'confirmation/$', views.confirmation_page, name="confirmation_page"),

        url(r'invoice/(?P<tracking_id>.+)/$', views.package_invoice_page, name="package_invoice"),

        url(r'courier-label/(?P<tracking_id>.+)/$', views.fetchPackageLabel, name="package_label"),
        # url(r'my-shipment/(?P<pkg_id>[\w+]+)/package-label/$', views.fetchPackageLabel, name="package_label"),

        # #url(r'^shipping-address/send-to/$', add_address, name="select_address"),
        #
        # url(r'^shipping-address/send-to/$', views.shipping_address, name="shipping_address"),
        # url(r'^shipping-address/edit-address/$', views.edit_address),
        #
        url(r'^shipment-manager/dockreceipts/$', views.dockreceipts, name="dockreceipts"),
        url(r'^shipment-manager/dock_form_edit/$', views.dock_form_edit, name="dock_form_edit"),
        url(r'^shipment-manager/dock_edit/$', views.dock_edit, name="dock_edit"),
        url(r'^shipment-manager/dock_template/(?P<tracking_number>.+)/$', views.dock_template, name="dock_template"),
        url(r'^postal-locations/$', views.get_local_distributor_locations, name="local_locations"),
        url(r'^local-pricing/$', views.get_local_distributor_prices, name="local_prices"),
        url(r'^domestic/package/$', views.domestic_package, name="domestic_package"),


]
