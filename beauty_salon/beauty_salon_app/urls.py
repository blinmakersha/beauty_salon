from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r'Service', views.ServiceViewSet)
router.register(r'Doctor', views.DoctorViewSet)


urlpatterns = [
    path('', views.custom_main, name='home'),
    path('profile/', views.profile_page, name='profile'),
    path('booking/', views.booking_page, name='booking'),
    path('services/', views.ServiceListView.as_view(), name='services'),
    path('doctors/', views.DoctorListView.as_view(), name='doctors'),
    # auth
    path('users/', include('django.contrib.auth.urls')),
    path('register/', views.register, name='register'),
    # REST
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('rest/', include(router.urls)),
]
