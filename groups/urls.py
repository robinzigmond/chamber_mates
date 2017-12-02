from django.conf.urls import url, include
from ajax_select import urls as ajax_select_urls
import views

urlpatterns = [
    url(r"^ajax_select/", include(ajax_select_urls)),
    url(r"^$", views.my_groups, name="my_groups"),
    url(r"^(?P<id>\d+)/$", views.group_detail, name="group"),
    url(r"^(?P<id>\d+)/update/$", views.update_group, name="update"),
    url(r"^(?P<group_id>\d+)/thread/new/$", views.new_thread, name="new_thread"),
    url(r"^(?P<group_id>\d+)/thread/(?P<thread_id>\d+)/$", views.view_thread, name="view_thread"),
    url(r"^(?P<group_id>\d+)/thread/(?P<thread_id>\d+)/delete/(?P<msg_id>\d+)/$",
        views.delete, name="delete_from_thread"),
    url(r"^new/$", views.new_group, name="new_group"),
    url(r"^invite/(?P<username>[\w@+-.]+)/$", views.new_group, name="invite"),
    url(r"^invite/(?P<group_id>\d+)/instrument/(?P<instr_name>[\w@+-.]+)/$",
        views.specific_invite, name="invite_for_instrument"),
    url(r"^invite/(?P<group_id>\d+)/user/(?P<user_id>\d+)/$",
        views.specific_invite, name="invite_for_user"),
    url(r"^invite/auto/(?P<group_id>\d+)/user/(?P<user_id>\d+)/$",
        views.add_invitation, name="auto_invite")
]
