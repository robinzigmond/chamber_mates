from django.conf.urls import url, include
from ajax_select import urls as ajax_select_urls
import views

urlpatterns = [
    url(r"^ajax_select/", include(ajax_select_urls)),
    url(r"^$", views.my_groups, name="my_groups"),
    url(r"^new/$", views.new_group, name="new_group"),
    url(r"^invite/(?P<username>[\w@+-.]+)/$", views.new_group, name="invite")
]