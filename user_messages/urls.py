from django.conf.urls import url
import views

urlpatterns = [
    url(r"^$", views.inbox, name="inbox"),
    url(r"^sent/$", views.outbox, name="sent"),
    url(r"^delete/(?P<view>\w+)/(?P<to_delete>(\d+)(-\d+)*)/$", views.delete, name="delete"),
    url(r"^(?P<view>\w+)/(?P<msg_id>\d+)/$", views.view_msg, name="view_msg"),
    url(r"^new/to/(?P<to>[\w@+-.]+)/$", views.new_msg, name="new_msg_to"),
    url(r"^new/$", views.new_msg, name="new_msg"),
]
