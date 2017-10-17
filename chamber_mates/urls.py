"""chamber_mates URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from home import views as home_views
from accounts import views as accounts_views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r"^$", home_views.home, name="home"),
    url(r"^why/$", home_views.why, name="why"),
    url(r"^register/$", accounts_views.register, name="register"),
    url(r"^logout/$", accounts_views.logout, name="logout"),
    url(r"^dashboard/$", accounts_views.dashboard, name="dashboard"),
    url(r"^profile/edit/$", accounts_views.edit_profile, name="edit profile"),
    url(r"^login/$", accounts_views.login, name="login")
]
