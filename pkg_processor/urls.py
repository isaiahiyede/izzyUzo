#from django.conf.urls.defaults import *
from django.conf.urls import patterns, include, url


import views


urlpatterns = [
        url(r'login/$', views.login),
        url(r'find_user_obj/$', views.find_user_obj),
        url(r'user-notify/$', views.user_notify),
        url(r'getPackages/$', views.get_packages),
        url(r'getTrucking/$', views.get_trucking),
        url(r'create-job/$', views.create_job),
        url(r'accept-job/$', views.accept_job),
        url(r'decline-job/$', views.decline_job),
        url(r'complete-job/$', views.complete_job),
        url(r'process-packages/$', views.mobile_packages_process),


        # url(r'packages/synchronization/$', views.appDBSynchroization),

          
]
 
