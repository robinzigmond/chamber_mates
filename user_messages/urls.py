from django.conf.urls import url
import views

urlpatterns = [
    url(r"^$", views.inbox, name="inbox"),
    url(r"^sent/$", views.outbox, name="outbox")
]
