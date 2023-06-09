from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import transaction
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.generic import ListView
from rest_framework import status as status_codes
from rest_framework.parsers import JSONParser
from rest_framework.permissions import BasePermission
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from . import config
from .forms import AddFundsForm, AppointmentForm, RegistrationForm
from .models import Appointment, Client, Doctor, Service
from .serializers import DoctorSerializer, ServiceSerializer


# registration
def register(request):
    form_errors = None
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            try:
                Client.objects.create(user=user, client_name=request.POST['first_name'],
                                      client_surname=request.POST['last_name'],
                                      date_of_birth=request.POST['date_of_birth'],
                                      email=request.POST['email'],
                                      phone=request.POST['phone'])
            except Exception as err:
                print('Нет пользователя: ', err)
            return redirect('/')
        form_errors = form.errors

    return render(
        request,
        config.TEMPLATE_REGISTER,
        context={
            'form': RegistrationForm(),
            'form_errors': form_errors,
        }
    )


# main page info
def custom_main(request):
    return render(request,
                  'index.html',
                  context={
                      'doctors': Doctor.objects.all(),
                      'services': Service.objects.all(),
                  }
                  )


@login_required
def booking_page(request):
    client = Client.objects.get(user=request.user)
    if request.method == "POST":
        app_form = AppointmentForm(client, request.POST)
        if app_form.is_valid():
            app_form.save()
            if 'doctor' in app_form.errors:
                messages.add_message(request, messages.INFO,
                                     'Выбранный вами доктор, не выполняет эту услугу. Попробуйте еще раз.')
                return redirect('/booking')
            if 'service' in app_form.errors:
                messages.add_message(request, messages.INFO,
                                     'Недостаточное количество средств. Пополните баланс.')
            if 'appointment' in app_form.errors:
                messages.add_message(request, messages.INFO,
                                     'Текущее время уже занято, выберите другое.')
            if 'app_date' in app_form.errors:
                messages.add_message(request, messages.INFO,
                                     'Нельзя выбрать время в прошлом. Попробуйте еще раз.')
            if not app_form.errors:
                if app_form.cleaned_data.get('status_payment') == 'P':
                    service_id = app_form.cleaned_data.get('service')
                    service = Service.objects.get(pk=service_id)
                    if client.money >= service.price:
                        with transaction.atomic():
                            client.money -= service.price
                            client.save()
                            messages.add_message(request, messages.INFO,
                                                 'Вы успешно записаны.')
                return redirect('/booking')
        else:
            print(app_form.errors)
    else:
        app_form = AppointmentForm(client)
    return render(request, '/Users/valentinai/semestr2/programming/beauty_salon/beauty_salon/templates/pages/booking.html',
                  {'app_form': app_form})


# profile page
@login_required
def profile_page(request):
    user = request.user
    client = Client.objects.get(user=user)
    form_errors = []

    if request.method == 'POST':
        form = AddFundsForm(request.POST)
        if form.is_valid():
            funds_to_add = form.cleaned_data.get('money')
            digits = len(str(client.money + funds_to_add)) - 1
            if funds_to_add > 0 and digits <= config.DECIMAL_MAX_DIGITS:
                with transaction.atomic():
                    client.money += funds_to_add
                    client.save()
                return HttpResponseRedirect(reverse('profile'))
            form_errors.append(f'Значение должно быть больше 0 и \
                                число символов не может быть больше чем {config.DECIMAL_MAX_DIGITS}')
        else:
            form_errors.extend(form.errors.get('money'))

    user_data = {
        'Псевдоним': user.username,
        'Имя': client.client_name,
        'Фамилия': client.client_surname,
        'Пол': client.sex,
        'Дата рождения': client.date_of_birth,
        'Email': user.email,
        'Номер телефона': client.phone,
        'Баланс': client.money,
        'appointments': Appointment.objects.filter(client=client),
    }

    return render(
        request,
        config.TEMPLATE_PROFILE,
        context={
            'form': AddFundsForm(),
            'user_data': user_data,
            'form_errors': '; '.join(form_errors),
        },
    )


# page with doctors/services
def catalog_view(cls_model, context_name, template):
    class CustomListView(ListView):
        model = cls_model
        template_name = template
        paginate_by = config.PAGINATOR_THRESHOLD
        context_object_name = context_name

        def get_context_data(self, **kwargs):
            context = super().get_context_data(**kwargs)
            if 'q' in self.request.GET:
                q = self.request.GET.get('q')
                if cls_model == Service:
                    objects = Service.objects.filter(title__icontains=q)
                elif cls_model == Doctor:
                    objects = Doctor.objects.all()
            else:
                objects = cls_model.objects.all()
            paginator = Paginator(objects, config.PAGINATOR_THRESHOLD)
            page = self.request.GET.get('page')
            page_obj = paginator.get_page(page)
            context[f'{context_name}_list'] = page_obj
            return context

    return CustomListView


ServiceListView = catalog_view(Service, 'services', config.SERVICES_CATALOG)
DoctorListView = catalog_view(Doctor, 'doctors', config.DOCTORS_CATALOG)


# REST, ModelViewSet
class Permission(BasePermission):
    safe_methods = ('GET', 'HEAD', 'OPTIONS', 'PATCH')
    unsafe_methods = ('POST', 'PUT', 'DELETE')

    def has_permission(self, request, _):
        if request.method in self.safe_methods:
            return bool(request.user and request.user.is_authenticated)
        elif request.method in self.unsafe_methods:
            return bool(request.user and request.user.is_superuser)
        return False


def query_from_request(cls_serializer, request) -> dict:
    """Gets query from request according to fields of the serializer class. 
    Returns empty dict if didn't find any."""
    query = {}
    for field in cls_serializer.Meta.fields:
        value = request.GET.get(field, '')
        if value:
            query[field] = value
    return query


def create_viewset(cls_model, serializer, order_field):
    class CustomViewSet(ModelViewSet):
        queryset = cls_model.objects.all()
        serializer_class = serializer
        permission_classes = [Permission]

        def get_queryset(self):
            query = query_from_request(serializer, self.request)
            queryset = cls_model.objects.filter(
                **query) if query else cls_model.objects.all()
            return queryset.order_by(order_field)

        def delete(self, request):
            def response_from_objects(num):
                if not num:
                    content = f'DELETE for model {cls_model.__name__}: query did not match any objects'
                    return Response(content, status=status_codes.HTTP_404_NOT_FOUND)
                status = status_codes.HTTP_204_NO_CONTENT if num == 1 else status_codes.HTTP_200_OK
                return Response(f'DELETED {num} instances of {cls_model.__name__}', status=status)

            query = query_from_request(serializer, request)
            if query:
                objects = cls_model.objects.all().filter(**query)
                num_objects = len(objects)
                try:
                    objects.delete()
                except Exception as error:
                    return Response(error, status=status_codes.HTTP_500_INTERNAL_SERVER_ERROR)
                return response_from_objects(num_objects)
            return Response('DELETE has got no query', status=status_codes.HTTP_400_BAD_REQUEST)

        def put(self, request):
            """gets id from query and updates instance with this ID, creates new if doesnt find any."""
            def serialize(target):
                content = JSONParser().parse(request)
                model_name = cls_model.__name__
                if target:
                    serialized = serializer(target, data=content, partial=True)
                    status = status_codes.HTTP_200_OK
                    body = f'PUT has updated {model_name} instance'
                else:
                    serialized = serializer(data=content, partial=True)
                    status = status_codes.HTTP_201_CREATED
                    body = f'PUT has created new {model_name} instance'
                if not serialized.is_valid():
                    return (
                        f'PUT could not serialize query {query} into {model_name}',
                        status_codes.HTTP_400_BAD_REQUEST
                    )
                try:
                    model_obj = serialized.save()
                except Exception as error:
                    return error, status_codes.HTTP_500_INTERNAL_SERVER_ERROR
                body = f'{body} with id={model_obj.id}'
                return body, status

            query = query_from_request(serializer, request)
            target_id = query.get('id', '')
            if not target_id:
                return Response('PUT has got no id', status=status_codes.HTTP_400_BAD_REQUEST)
            try:
                target_object = cls_model.objects.get(id=target_id)
            except Exception:
                target_object = None
            content, status = serialize(target_object)
            return Response(content, status=status)

    return CustomViewSet


ServiceViewSet = create_viewset(Service, ServiceSerializer, 'title')
DoctorViewSet = create_viewset(Doctor, DoctorSerializer, 'name')
