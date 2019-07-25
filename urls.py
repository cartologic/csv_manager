from django.conf.urls import url, include
from django.views.generic import TemplateView
from . import views, APP_NAME
from tastypie.api import Api
from .api import CSVUploadResource

v1_api = Api(api_name='v1')
v1_api.register(CSVUploadResource())

urlpatterns = [
   url(r'^$', views.index, name='%s.index' % APP_NAME),
   url(r'^upload/', views.upload, name='%s.upload' % APP_NAME),
   url(r'^publish/', views.publish, name='%s.upload' % APP_NAME),
   url(r'^api/', include(v1_api.urls)),
]
