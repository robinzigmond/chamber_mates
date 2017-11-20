from django.conf.urls import url
import views

urlpatterns = [
    url(r"^$", views.my_groups, name="my_groups")
]
