import csv
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView
import logging
from .forms import UserRegisterForm, TelephonyProviderForm, AudioFileForm, SubscriberUploadForm

from .serializers import *

from pydub import AudioSegment
from pydub.playback import play
from pyVoIP.VoIP import VoIPPhone, InvalidStateError
import socket

logger = logging.getLogger(__name__)


class TelephonyProviderViewSet(viewsets.ModelViewSet):
    """
    ViewSet для работы с моделью TelephonyProvider.
    """
    queryset = TelephonyProvider.objects.all()
    serializer_class = TelephonyProviderSerializer


class SubscriberViewSet(viewsets.ModelViewSet):
    """
    ViewSet для работы с моделью Subscriber.
    """
    queryset = Subscriber.objects.all()
    serializer_class = SubscriberSerializer


class UserSettingsViewSet(viewsets.ModelViewSet):
    """
    ViewSet для работы с моделью UserSettings.
    """
    queryset = UserSettings.objects.all()
    serializer_class = UserSettingsSerializer


class AudioFileViewSet(viewsets.ModelViewSet):
    """
    ViewSet для работы с моделью AudioFile.
    """
    queryset = AudioFile.objects.all()
    serializer_class = AudioFileSerializer


def home(request: HttpRequest) -> HttpResponse:
    """
    Представление для отображения домашней страницы.
    """
    return render(request, 'registration/home.html')


class UserRegisterView(CreateView):
    """
    Представление для регистрации нового пользователя.
    """
    model = User
    form_class = UserRegisterForm
    template_name = "registration/register.html"
    success_url = reverse_lazy("home")


def save_provider(request: HttpRequest) -> HttpResponse:
    """
    Представление для сохранения информации о поставщике телефонии.
    """
    provider_form = TelephonyProviderForm(request.POST or None)
    if request.method == 'POST':
        if provider_form.is_valid():
            try:
                provider = provider_form.save(commit=False)
                provider.user = request.user  # Set user field to current user
                provider.save()
                messages.success(request, 'Telephony provider created successfully.')
            except Exception as e:
                messages.error(request, f'Error saving telephony provider: {e}')
            return redirect('save_audio_file')
    return render(request, 'calls/save_provider.html', {
        'provider_form': provider_form,
    })


def save_audio_file(request: HttpRequest) -> HttpResponse:
    """
    Представление для загрузки звукового файла.
    """
    audio_file_form = AudioFileForm(request.POST or None, request.FILES or None)
    if request.method == 'POST':
        if audio_file_form.is_valid():
            try:
                audio_file = audio_file_form.save(commit=False)
                audio_file.user = request.user  # Set user field to current user
                audio_file.save()
                messages.success(request, 'Audio file uploaded successfully.')
            except Exception as e:
                messages.error(request, f'Error uploading audio file: {e}')
            return redirect('save_subscriber_list')
    return render(request, 'calls/save_audio_file.html', {
        'audio_file_form': audio_file_form,
    })


def save_subscriber_list(request: HttpRequest) -> HttpResponse:
    """
    Представление для загрузки списка абонентов.
    """
    subscriber_upload_form = SubscriberUploadForm(request.POST or None, request.FILES or None)
    if request.method == 'POST':
        if subscriber_upload_form.is_valid():
            try:
                if subscriber_upload_form.cleaned_data['clear_subscribers']:
                    Subscriber.objects.filter(user=request.user).delete()
                file = request.FILES['file']
                decoded_file = file.read().decode('utf-8').splitlines()
                reader = csv.DictReader(decoded_file)
                for row in reader:
                    if 'phone_number' not in row:
                        raise Exception('Invalid file format. File must contain "phone_number" column.')
                    phone_number = row['phone_number']
                    if not phone_number.startswith('+') and not phone_number.startswith('00'):
                        phone_number = f'+{phone_number}'
                    subscriber = Subscriber.objects.create(phone_number=phone_number, user=request.user)
                messages.success(request, 'Subscriber list uploaded successfully.')
                try:
                    tele_provider = TelephonyProvider.objects.filter(user=request.user).last()
                    audio_file = AudioFile.objects.filter(user=request.user).last()
                    print(f'Last created AudioFile instance for current user: {audio_file}')
                    user_settings, created = UserSettings.objects.get_or_create(
                        user=request.user,
                        audio_file=audio_file,
                        tele_provider=tele_provider
                    )
                    print(f'UserSettings instance created: {user_settings}')
                    user_settings.tele_provider = tele_provider
                    user_settings.audio_file = audio_file
                    user_settings.save()
                except Exception as e:
                    print(f'Error creating UserSettings instance: {e}')
            except Exception as e:
                messages.error(request, f'Error uploading subscriber list: {e}')
            return redirect('make_calls')
    return render(request, 'calls/save_subscriber_list.html', {
        'subscriber_upload_form': subscriber_upload_form,
    })


def make_calls(request):
    print('make_calls called')
    if request.method == 'POST':
        print('POST request')
        try:
            user_settings = UserSettings.objects.get(user=request.user)
            provider = user_settings.tele_provider
            audio_file = user_settings.audio_file
            subscriber_phone_numbers = Subscriber.objects.values_list('phone_number', flat=True)
            for subscriber_phone_number in subscriber_phone_numbers:
                print(f'{subscriber_phone_number} called')
                make_call(subscriber_phone_number, audio_file.file.path, provider)
            messages.success(request, 'Calls made successfully.')
        except UserSettings.DoesNotExist:
            print('UserSettings.DoesNotExist')
            messages.error(request, 'You must configure your settings before making calls.')
        except Exception as e:
            print(f'Exception: {e}')
        return redirect('make_calls_done')
    else:
        print('Not a POST request')
        return render(request, 'calls/make_calls.html')


def make_calls_done(request):
    return render(request, 'calls/make_calls_done.html')


def play_audio_file(file_path):
    audio = AudioSegment.from_mp3(file_path)
    play(audio)


def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        local_ip = s.getsockname()[0]
    except Exception:
        local_ip = '127.0.0.1'
    finally:
        s.close()
    return local_ip


def make_call(subscriber_phone_number, audio_file_path, provider):
    try:
        if not provider:
            logger.warning(f'Provider is not set for call to {subscriber_phone_number}')
            raise Exception('Provider is not set')

        # Log SIP connection parameters
        print(f'SIP gateway address: {provider.sip_gateway_address}')
        print(f'Username: {provider.username}')
        print(f'Password: {provider.password}')

        phone = VoIPPhone(
            provider.sip_gateway_address, 5060, provider.username, provider.password, myIP=get_local_ip()
        )
        phone.start()
        call = phone.call(subscriber_phone_number)
        if not call:
            logger.warning(f'Failed to make call to {subscriber_phone_number}')
            return
        play_audio_file(audio_file_path)
        call.hangup()
        phone.stop()
    except Exception as e:
        logger.error(f'Error making call to {subscriber_phone_number}: {e}')

