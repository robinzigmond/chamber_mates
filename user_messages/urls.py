from django.conf.urls import url
import views

urlpatterns = [
    url(r"^$", views.inbox, name="inbox"),
    url(r"^sent/$", views.outbox, name="outbox"),
    url(r"^delete/(?P<view>\w+)/(?P<to_delete>[\d+][-\d+]*)$", views.delete, name="delete"),
]
