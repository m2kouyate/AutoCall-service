from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import TelephonyProvider, AudioFile, Subscriber


class UserRegisterForm(UserCreationForm):
    """
    Форма для регистрации нового пользователя.
    """
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

        help_texts = {
            "username": "",
            "password1": "",
            "password2": "",
        }


class TelephonyProviderForm(forms.ModelForm):
    """
    Форма для сохранения информации о поставщике телефонии.
    """
    class Meta:
        model = TelephonyProvider
        fields = ['sip_gateway_address', 'username', 'password']


class AudioFileForm(forms.ModelForm):
    """
    Форма для загрузки звукового файла.
    """
    class Meta:
        model = AudioFile
        fields = ['file', 'name']

    def clean_file(self) -> forms.FileField:
        """
        Проверка формата загружаемого файла.
        """
        file = self.cleaned_data.get('file')
        if file:
            ext = file.name.split('.')[-1]
            if ext.lower() != 'mp3':
                raise forms.ValidationError('Unsupported file format. Please upload an MP3 file.')
        return file


class SubscriberForm(forms.ModelForm):
    """
    Форма для сохранения информации об абоненте.
    """
    class Meta:
        model = Subscriber
        fields = ['phone_number']


class SubscriberUploadForm(forms.Form):
    """
    Форма для загрузки списка абонентов.
    """
    file = forms.FileField(label='Select a file')
    clear_subscribers = forms.BooleanField(label='Clear subscribers', required=False)

    def clean_file(self) -> forms.FileField:
        """
        Проверка формата загружаемого файла.
        """
        file = self.cleaned_data.get('file')
        if file:
            ext = file.name.split('.')[-1]
            if ext not in ['csv', 'txt']:
                raise forms.ValidationError('Unsupported file format. Please upload a CSV or TXT file.')
        return file