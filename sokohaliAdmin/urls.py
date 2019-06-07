from django.conf.urls import patterns, include, url
from django.conf import settings
from sokohaliAdmin.views import *
import views


urlpatterns = [
                url(r'^dashboard/$', views.dashboardView, name="dashboard"),
                url(r'^orders/$', views.Shopping_orders, name="orders"),
                url(r'^shipment-manager/$', views.shipments, name="shipment_manager"),
                url(r'^assign_to_batch/$', views.assign_batch, name="assign_to_batch"),
                url(r'^undo/assign_to_batch/(?P<tracking_number>.*)$', views.undo_batchassigned, name="undo_batchassigned"),
                url(r'^batch-manager/$', views.Batch_manager, name="batch-manager"),
                url(r'^batch/create/$', views.create_batch, name="create-batch"),
                url(r'^batch/update/$', views.update_batch, name="update-batch"),
                url(r'^getbatchitem/$', views.getbatchitem, name="getbatchitem"),
                url(r'^user-manager/$', views.user_manager, name="user-manager"),
                url(r'^user-manager/specialrate/$', views.apply_specialRate, name = "specialrate"),
                url(r'^staff-login-access/$', views.staff_login_access, name="staff_login_access"),
                url(r'^user-manager/createuser/$', views.adminCreateuser, name="admin_createuser"),
                url(r'^(?P<payment_type>.+)/(?P<status>.+)/log/$', views.payments_log, name="payments_log"),
                url(r'^user/history/(?P<user_id>[0-9]+)$', views.user_history, name="userhistory"),
                url(r'^user-manager/search/$', views.searchbar, name="search"),
                url(r'^batch/process/$', views.process_batches, name="process-batches"),
                url(r'^user-manager/(?P<action>.+)/$', views.sidebar, name="sidebar"),
                url(r'^truck-manager/(?P<action>.+)/$', views.sidebarTruck, name="sidebarTruck"),
                url(r'^notify-manager/(?P<action>.+)/$', views.sidebarNotify, name="sidebarNotify"),
                
                url(r'^batch/search/$', views.search_batch, name="search-batch"),
                url(r'^batch/manifest/(?P<pk>[\w]+)/$', views.print_manifest, name="print-manifest"),
                url(r'^warehouses/$', views.get_warehouse_addresses, name = "get_warehouse_addresses"),
                
                url(r'^user-manager/(?P<user_id>[0-9]+)/(?P<action>.+)$', views.usertype, name="usertype"),
                url(r'^batch/type/(?P<action>.+)$', views.bmgr_actions, name="bmgr-actions"),
                url(r'^batch/action/(?P<action>.+)/(?P<batch_id>[\w]+)$', views.batch_actions, name="batch-actions"),

                url(r'^batches/awb/$', views.awb, name="awb"),
                url(r'^batches/dockreceipts/$', views.dockreceipts, name="dockreceipts"),
                url(r'^batches/form_edit/$', views.form_edit, name="form_edit"),
                url(r'^batches/form_update/$', views.form_update, name="form_update"),
                # url(r'^batches/dock_form_edit/$', views.dock_form_edit, name="dock_form_edit"),
                # url(r'^batches/dock_edit/$', views.dock_edit, name="dock_edit"),
                url(r'^batch-manager/awb_template/(?P<batch_number>.+)/$', views.awb_template, name="awb_template"),
                # url(r'^shipment-manager/dock_template/(?P<tracking_number>.+)/$', views.dock_template, name="dock_template"),
                # url(r'^item-deleted/$',views.admin_delete_item, name="admin_delete_item"),
                url(r'^item-details/$', views.item_details, name="item_details"),
                url(r'^change-item-status/$', views.change_item_status, name="change_item_status"),
                url(r'^shipment-manager/process_package/(?P<tracking_number>.+)/$', views.process_package, name="process_package"),
                url(r'^shipment-manager/pkg-shipping-label/(?P<tracking_number>.+)/$', views.pkg_shipping_label, name="pkg_shipping_label"),
                url(r'^shipment-manager/notification-label/(?P<notify_id>.+)/$', views.notification_label, name="notification_label"),

                url(r'^shipment-manager/find_user/$', views.find_user, name="find_user"),
                url(r'^shipment-manager/user_info/$', views.cb_user_info, name="user_info"),

                url(r'^shipment-manager/fixedWeight/$', views.fixed_weight_info, name="fixed_weight_info"),
                url(r'^shipment-manager/getCost/$', views.get_cost, name="get_cost"),
                url(r'^shoppingManager/$', views.shoppingManager, name="shoppingManager"),
                url(r'^shipment-manager/exportitem_categories/$', views.subCategory, name="sub_category"),
                url(r'^shipment-manager/add_item/$', views.cb_add_item, name="add_item"),
                url(r'^shipment-manager/admin_add_item/$', views.show_admin_added_items, name="admin_add_item"),
                url(r'^shipment-manager/create_package/$', views.admin_create_package, name="create_package"),
                url(r'^shipment-manager/updates/$', views.pkg_final_updates, name="pkg_final_updates"),
                url(r'^shipment-manager/del_cancel_pkg/(?P<item_id>[-\w]+)/(?P<action>[-\w]+)/$', views.del_cncl_package, name="del_cncl_package"),

                url(r'^shipment-manager/invoice/(?P<tracking_number>.+)/$', views.view_invoice, name="invoice"),
                url(r'^shipment-manager/discount/$', views.apply_discount, name = "apply_discount"),
                url(r'^shipment-manager/revoke-order/$', views.revoke_order, name = "revoke_order"),
                url(r'^shipment-manager/truckingService/$', views.trucking_service, name = "trucking_service"),
                url(r'^shipment-manager/archive_delete_truck/(?P<item_id>[-\w]+)/(?P<action>[-\w]+)/$', views.archive_delete_truck, name = "archive_delete_truck"),
                url(r'^shopping-manager/(?P<action>.+)/$', views.sidebarShopper, name="sidebarShopper"),      
                url(r'^shipment-manager/edit_process_trucking_form/$', views.edit_process_trucking_form, name = "edit_process_trucking_form"),
                url(r'^shipment-manager/edit_process_shopping_form/$', views.edit_process_shopping_form, name = "edit_process_shopping_form"),
                url(r'^shipment-manager/trucking_edit/$', views.trucking_edit, name="trucking_edit"),
                url(r'^shipment-manager/shopping_edit/$', views.shopping_edit, name="shopping_edit"),
                url(r'^client-dashboard/$', views.client_dashboard, name = "client_dashboard"),

                url(r'^shipment-manager/notify_user/$', views.notify_user, name = "notify_user"),
                url(r'^shipment-manager/edit/package/$', views.edit_package, name="edit_package"),
                url(r'^message-center/$', views.message_center, name = "message-center"),
                url(r'^get-package-dimensions/$', views.get_dimensions_of_package, name = "get_dimensions_of_package"),

                url(r'^admin-added-items/$', views.delete_admin_added_items, name = "delete_admin_added_items"),

                url(r'^message-status/(?P<status>[-\w]+)/$', views.message_status, name = "message-status"),
                url(r'^archv-msg/(?P<item_id>[-\w]+)/(?P<status>.+)/$', views.msg_cntr_archv, name = "msg-cntr-archv"),
                url(r'^user-notification/$', views.user_item_received, name = "user_item_received"),


                url(r'^shipment-manager/batch-promo/(?P<action>[-\w]+)/$', views.batch_promo, name="batch_promo"),
                url(r'^paySearch/$', views.paySearch, name="paySearch"),

                url(r'^shipment-manager/package-filter/(?P<route_id>[-\w]+)/$', views.package_filter, name="package_filter"),

                url(r'^payment/decision/$', views.approve_veipayment, name="approve_veipayment"),
                url(r'^payment/decision/$', views.approve_sokopayment, name="approve_sokopayment"),
                
                url(r'^sokopay/payment-history/$', views.payment_history, name ="payment_history"),
                url(r'^check-user-access/$', views.check_user_access, name="check_user_access"),
                url(r'^get-fixed-weight-cat/$', views.get_fixed_weight_cat, name="get_fixed_weight_cat"),
                url(r'^override-payment/$', views.override_payment, name="override_payment"),
                url(r'^admin-edit-item/$', views.admin_edit_item, name="admin-edit-item"),
                url(r'^editSpecial/$', views.editSpecial, name="editSpecial"),
                url(r'^staff-dashboard/$', views.superuser_dasboard, name='superuser_dasboard'),
                url(r'^edit-fixed-weight-shipment/(?P<tracking_number>[-\w]+)/$', views.edit_fxd_package, name="edit_fxd_package"),
                url(r'^bank-payment/$', views.approve_bankpayment,name="approve_bankpayment"),
                url(r'^get-delivery-time/$', views.get_delivery_time,name="get_delivery_time"),
                url(r'^ams-add-item/$', views.ams_add_item,name="ams_add_item"),
                url(r'^crud_shopping_manager/(?P<item_id>[-\w]+)/(?P<action>.+)/$', views.crud_shopping_manager, name='crud_shopping_manager'),

                url(r'^local-distribution-member/$', views.local_dist_member, name='local_dist_member'),
                url(r'^local-distribution-member-edit/$', views.local_dist_member_edit, name='local_dist_member_edit'),
                url(r'^edit-local-distribution-member/$', views.edit_local_dist_member, name='edit_local_dist_member'),

                url(r'^view-region/$', views.view_region, name='view_region'), #View each region tied to a marketer
                url(r'^view-location/$', views.view_location, name='view_location'), #View each location tied to a region

                url(r'^local-distribution-region/$', views.local_dist_region, name='local_dist_region'),
                url(r'^local-distribution-region-edit/$', views.local_dist_region_edit, name='local_dist_region_edit'),
                url(r'^edith-local-distribution-region/$', views.edit_local_dist_region, name='edit_local_dist_region'),
                url(r'^local-distribution-location/$', views.local_dist_location, name='local_dist_location'),
                url(r'^local-distribution-price/$', views.local_dist_price, name='local_dist_price'),
                url(r'^local-distribution-location-edit/$', views.local_dist_location_edit, name='local_dist_location_edit'),
                url(r'^edit-local-distribution-location/$', views.edit_local_dist_location, name='edit_local_dist_location'),

                url(r'^get-pkg-dimens/$', views.get_pkg_dimens, name = "get_pkg_dimens"),
                url(r'^help/$', views.help, name = "help"),

                url(r'^security-question/$', views.security_question, name="security_question"),
                url(r'^get-user-account/$', views.get_user_account, name="get_user_account"),
                # url(r'^get-security-answer/$', views.get_security_answer, name="get_security_answer"),


        ]
