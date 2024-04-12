from django.contrib import admin
from django.urls import path
import v3
from v3.views import *
from. import views
from . import views
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
app_name = 'v3'

urlpatterns = [
    path('', login, name='login'),
    path('index', main, name='index'),

    path('401', four01, name='four01'),

    path('404', four04,  name='four04'),

    path('500', five00, name='five00'),

    path('charts', charts, name='charts'),

    path('layout-sidenav-light', layout_sidenav_light, name='layout_sidenav_light'),

    path('layout-static', layout_static, name='layout_static'),

    path('login', login, name='login'),

    path('password', password, name='password'),

    path('register', register, name='register'),

    path('tables', tables, name='tables'),

    path('fileUp', fileUp, name='fileUp'),
    path("uploadFile", views.uploadFile, name="uploadFile"),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
