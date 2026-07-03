from debug_toolbar.toolbar import debug_toolbar_urls
from django.urls import path

from home.views import index

urlpatterns = [
    path("", index, name="home"),
] + debug_toolbar_urls()
