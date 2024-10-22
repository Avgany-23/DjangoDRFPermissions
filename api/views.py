from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.viewsets import ModelViewSet
from .models import Advertisement, AdvertisementStatusChoices
from .serializers import UserSerializer, AdvertisementSerializer, UserLoginPassworRegistrationdSerializer
from .fitlers import AdvertisementFilter
from rest_framework.response import Response
from rest_framework import status
from .permissions import AdvertisementPermissions
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from django.db.utils import IntegrityError


class AdvertisementViewSet(ModelViewSet):
    """
    ViewSet для объявлений.

    Основа аутентификации - JWT токен (описание во втором классе ниже)

    Пример базового запроса на получение всех записей
        Запрос:
        - GET http://127.0.0.1:8000/api/v1/advert/
            -H {
                "Content-Type": "application/json"
                "Authorization": "Bearer JWT_token"
                }
            -b {"username": "имя", "password": "пароль"}

    - Безопасные методы доступны всем пользователям.
    - Метод на создание доступные авторизированным пользователям
    - Метод на удаление, полное и частичное обновление ресурса доступны авторизированным владельцам ресурса
    - Админам доступны все методы всех записей

    Ограничение на запросы:
        - авторизированные пользователи: 20 в минуту
        - не авторизированные пользователи: 10 в минуту
    """

    queryset = Advertisement.objects.all()
    serializer_class = AdvertisementSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = AdvertisementFilter
    permission_classes = [AdvertisementPermissions]


    def create(self, request, *args, **kwargs):
        if Advertisement.objects.filter(creator=request.user, status=AdvertisementStatusChoices.OPEN).count() >= 10:
            return Response({'limit error': 'Превышено максимальное число записей (10).'},
                            status=status.HTTP_409_CONFLICT)
        return super().create(request, *args, **kwargs)


class RegistrationAPIView(APIView):
    """
    Для регистрации. Сразу же выдаётся JWT токен (access и refresh)
    Запрос:
        - POST http://127.0.0.1:8000/api/v1/registration
            -H {"Content-Type": "application/json"}
            -b {"username": "имя", "password": "пароль"}
    Ответ:
    {
    "refresh": "токен для замены",
    "access": "токен для запросов"
    }
    access - действует 10 минут.
    refresh - действует 1 день

    ---------- ЗАМЕНА ТОКЕНА ----------
    Поменять access токен можно по рефреш токену по запросу:
        - POST http://127.0.0.1:8000/api/v1/token/jwt/refresh
            -H {"Content-Type": "application/json"}
            -b {"refresh": "ваш refresh токен"}

    ---------- ПОЛУЧЕНИЕ ТОКЕНА ----------
    Если время refresh токена истекло, то новый access и refresh токен можно по запросу:
        - POST http://127.0.0.1:8000/api/v1/token/jwt
            -H {"Content-Type": "application/json"}
            -b {"username": "логин", "password": "пароль"}
    """

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserLoginPassworRegistrationdSerializer(data=request.data)

        if serializer.is_valid():
            status_user = serializer.data.pop('status', None)
            user = User(**serializer.data)
            if status_user and status_user == 'admin':
                user.is_staff = True
            if status_user and status_user == 'admin':
                user.is_superuser = True
            try:
                user.save()
            except IntegrityError:
                return Response({'error': 'Пользователь с таким именем уже существует'},
                                status=status.HTTP_400_BAD_REQUEST)

            refresh = RefreshToken.for_user(user)
            refresh.payload.update({
                'username': user.username
            })

            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token), # Отправка на клиент
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors)

