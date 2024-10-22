from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import AdvertisementViewSet
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import RegistrationAPIView


router = DefaultRouter()
router.register('advert', AdvertisementViewSet, basename='advert')

urlpatterns = [
    path('token/jwt', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/jwt/refresh', TokenRefreshView.as_view(), name='token_refresh'),
    path('registration', RegistrationAPIView.as_view())
] + router.urls

