from rest_framework import serializers, viewsets, routers
from .models import TelephonyProvider, AudioFile, Subscriber, UserSettings


class TelephonyProviderSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели TelephonyProvider.
    """
    class Meta:
        model = TelephonyProvider
        fields = '__all__'


class AudioFileSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели AudioFile.
    """
    class Meta:
        model = AudioFile
        fields = '__all__'


class SubscriberSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Subscriber.
    """
    class Meta:
        model = Subscriber
        fields = '__all__'


class UserSettingsSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели UserSettings.
    """
    class Meta:
        model = UserSettings
        fields = '__all__'

