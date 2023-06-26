from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views
from .views import UserRegisterView, make_calls, make_calls_done, save_provider, save_audio_file, save_subscriber_list

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', UserRegisterView.as_view(), name='register'),
    path('make_calls/', make_calls, name='make_calls'),
    path('save_provider/', save_provider, name='save_provider'),
    path('save_audio_file/', save_audio_file, name='save_audio_file'),
    path('save_subscriber_list/', save_subscriber_list, name='save_subscriber_list'),
    path('make_calls_done/', make_calls_done, name='make_calls_done'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)