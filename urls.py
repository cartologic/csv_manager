from django.conf.urls import url, include
from django.views.generic import TemplateView
from . import views, APP_NAME

urlpatterns = [
   url(r'^$', views.index, name='%s.index' % APP_NAME),
]
