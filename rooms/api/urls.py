from django.urls import path,include
from .views import RoomViewsets
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'room', RoomViewsets)

urlpatterns = [
    path('', include(router.urls)),
]