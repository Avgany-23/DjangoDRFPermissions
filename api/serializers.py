from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Advertisement, AdvertisementStatusChoices


class UserStatusChoises(serializers.ChoiceField):
    ADMIN = 'admin', 'админ'
    SUPERUSER = 'super', 'супер-пользователь'

class UserLoginPassworRegistrationdSerializer(serializers.Serializer):
    username = serializers.CharField(min_length=5, max_length=30)
    password = serializers.CharField(min_length=4)
    status = serializers.ChoiceField(required=False, choices=['admin', 'super'])


class UserSerializer(serializers.ModelSerializer):
    """Serializer для пользователя."""

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name',
                  'last_name',)


class AdvertisementSerializer(serializers.ModelSerializer):
    """Serializer для объявления."""

    creator = UserSerializer(
        read_only=True,
    )

    class Meta:
        model = Advertisement
        fields = ('id', 'title', 'description', 'creator',
                  'status', 'created_at', )

    def create(self, validated_data):
        """Метод для создания"""
        validated_data["creator"] = self.context["request"].user
        return super().create(validated_data)

    def validate(self, data):
        """Метод для валидации. Вызывается при создании и обновлении."""
        user = self.context.get('request').user
        result = Advertisement.objects.filter(creator=user, status=AdvertisementStatusChoices.OPEN).count() >= 10
        if result:
            return {}
        return data
