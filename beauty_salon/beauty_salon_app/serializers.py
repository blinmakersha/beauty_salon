from rest_framework.serializers import HyperlinkedModelSerializer
from .models import Service, Doctor


class ServiceSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = Service
        fields = ('id', 'title', 'description', 'duration', 'price',)


class DoctorSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = Doctor
        fields = ('id', 'name', 'surname', 'speciality', 'description', 'sex', 'date_of_birth', 'email', 'phone', 'office',)
