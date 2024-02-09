"""demo URL Configuration
The `urlpatterns` list routes URLs to views. 
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
from django.conf.urls import include
from django.urls import re_path, path
from django.contrib import admin
import juntagrico

from begegnungsallmende import overrides

urlpatterns = [
    re_path(r'^admin/', admin.site.urls),

    # override
    path('my/signup/', overrides.MySignupView.as_view(), name='signup'),
    path('my/create/subscription/selectdepot/', overrides.set_defaults, name='cs-depot'),
    path('my/create/subscription/start/', overrides.set_defaults, name='cs-start'),
    path('my/create/subscription/addmembers/', overrides.CSCustomView.as_view(), name='cs-co-members'),

    path('my/subscription/detail/', overrides.subscription, name='sub-detail'),

    re_path(r'^', include('juntagrico.urls')),
    re_path(r'^$', juntagrico.views.home),
    re_path(r'^impersonate/', include('impersonate.urls')),
    path('i18n/', include('django.conf.urls.i18n')),
]
