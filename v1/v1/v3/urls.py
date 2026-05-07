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
    
    path('login', views.login, name='login'),

    path('password', password, name='password'),

    path('register', register, name='register'),
    path('check_username/', check_username, name='check_username'),
     path('lunge', lunge, name='lunge'),
     path('flank', flank, name='flank'),
     path('squat', squat, name='squat'),
     path('pullup', pullup, name='pullup'),

    

    path('main', views.main,name ='main'),
    
 
   
    path('events', views.events, name='events'),
    path('result', views.result, name='result'),

    path('lunge_video', views.lunge_video, name='lunge_video'),
    path('lunge_tool', views.lunge_tool, name='lunge_tool'),

    path('video_list', views.video_list, name='video_list'),

    path('pullup_video', views.pullup_video, name='pullup_video'),
    path('pullup_tool', views.pullup_tool, name='pullup_tool'),

    path('flank_video', views.flank_video, name='flank_video'),
    path('squat_video', views.squat_video, name='squat_video'),

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
