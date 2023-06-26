from django.contrib.auth.hashers import make_password
from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import User
from phonenumber_field.modelfields import PhoneNumberField


class TelephonyProvider(models.Model):
    """
    Модель для хранения информации о поставщике телефонии.
    """
    sip_gateway_address = models.CharField(max_length=255)
    username = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def save(self, *args, **kwargs) -> None:
        """
        Переопределение метода save для шифрования пароля перед сохранением.
        """
        self.password = make_password(self.password)
        super(TelephonyProvider, self).save(*args, **kwargs)

    def clean(self) -> None:
        """
        Переопределение метода clean для проверки обязательных полей.
        """
        super().clean()
        if not self.sip_gateway_address:
            raise ValidationError('SIP gateway address is required.')
        if not self.username:
            raise ValidationError('Username is required.')
        if not self.password:
            raise ValidationError('Password is required.')

    def __str__(self) -> str:
        return f'{self.sip_gateway_address}'


class AudioFile(models.Model):
    """
    Модель для хранения информации о звуковых файлах.
    """
    file = models.FileField(upload_to='audio_files/')
    name = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def clean(self) -> None:
        """
        Переопределение метода clean для проверки обязательных полей.
        """
        super().clean()
        if not self.file:
            raise ValidationError('File is required.')

    def __str__(self) -> str:
        return f'{self.name}'


class Subscriber(models.Model):
    """
    Модель для хранения информации об абонентах.
    """
    phone_number = PhoneNumberField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def clean(self) -> None:
        """
        Переопределение метода clean для проверки обязательных полей.
        """
        super().clean()
        if not self.phone_number:
            raise ValidationError('Phone number is required.')

    def __str__(self) -> str:
        return f'{self.phone_number}'


class UserSettings(models.Model):
    """
    Модель для хранения настроек пользователя.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='settings')
    tele_provider = models.ForeignKey(TelephonyProvider, on_delete=models.CASCADE)
    audio_file = models.ForeignKey(AudioFile, on_delete=models.CASCADE)
    subscribers = models.ManyToManyField(Subscriber)

    def clean(self) -> None:
        """
        Переопределение метода clean для проверки обязательных полей.
        """
        super().clean()
        if not self.tele_provider:
            raise ValidationError('Telephony provider is required.')
        if not self.audio_file:
            raise ValidationError('Audio file is required.')
        if not self.subscribers:
            raise ValidationError('Subscriber is required.')

    def __str__(self) -> str:
        return f'{self.user.username} settings'

