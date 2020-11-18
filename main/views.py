from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from main.forms import QuizForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from main.models import EducationCenter, Word
from main.forms import TeacherForm, SimplifiedTeacherForm, EducationCenterForm, TeacherUpdateForm, ChangePasswordForm, SimplifiedAlumForm, SimplifiedGroupForm, AlumUpdateForm
from django.contrib.gis.geos import GEOSGeometry
from rest_framework.decorators import api_view, permission_classes
from querystring_parser import parser
import json
import functools
from rest_framework.response import Response
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import operator
from main.serializers import EducationCenterSerializer, TeacherSerializer, UserSerializer, AlumSerializer, GroupSerializer, GroupSearchSerializer
from rest_framework import status,viewsets, generics
from django.db.models import Q
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import UpdateModelMixin
from rest_framework.viewsets import ModelViewSet
from rest_framework import serializers
from django import forms
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.urls import reverse
from random import randint
from django.http import JsonResponse
from django.core.files.uploadedfile import UploadedFile
from django.conf import settings
from django.core.files import File
from shutil import copy
import os


def get_order_clause(params_dict, translation_dict=None):
    order_clause = []
    try:
        order = params_dict['order']
        if len(order) > 0:
            for key in order:
                sort_dict = order[key]
                column_index_str = sort_dict['column']
                if translation_dict:
                    column_name = translation_dict[params_dict['columns'][int(column_index_str)]['data']]
                else:
                    column_name = params_dict['columns'][int(column_index_str)]['data']
                direction = sort_dict['dir']
                if direction != 'asc':
                    order_clause.append('-' + column_name)
                else:
                    order_clause.append(column_name)
    except KeyError:
        pass
    return order_clause


def get_filter_clause(params_dict, fields, translation_dict=None):
    filter_clause = []
    try:
        q = params_dict['search']['value']
        if q != '':
            for field in fields:
                if translation_dict:
                    translated_field_name = translation_dict[field]
                    filter_clause.append( Q(**{translated_field_name+'__icontains':q}) )
                else:
                    filter_clause.append(Q(**{field + '__icontains': q}))
    except KeyError:
        pass
    return filter_clause


def generic_datatable_list_endpoint(request,search_field_list,queryset, classSerializer, field_translation_dict=None, order_translation_dict=None):
    draw = request.query_params.get('draw', -1)
    start = request.query_params.get('start', 0)
    #length = request.query_params.get('length', 25)
    length = 25

    get_dict = parser.parse(request.GET.urlencode())

    order_clause = get_order_clause(get_dict, order_translation_dict)

    filter_clause = get_filter_clause(get_dict, search_field_list, field_translation_dict)

    if len(filter_clause) == 0:
        queryset = queryset.order_by(*order_clause)
    else:
        queryset = queryset.order_by(*order_clause).filter(functools.reduce(operator.or_, filter_clause))

    paginator = Paginator(queryset, length)

    recordsTotal = queryset.count()
    recordsFiltered = recordsTotal
    page = int(start) / int(length) + 1

    serializer = classSerializer(paginator.page(page), many=True)
    return Response({'draw': draw, 'recordsTotal': recordsTotal, 'recordsFiltered': recordsFiltered, 'data': serializer.data})

# Create your views here.
def index(request):
    #return HttpResponse("Hello, world. You're at the polls index.")
    return render(request, 'main/index.html', {})


def teacher_menu(request):
    return render(request, 'main/teacher_menu.html', {})


def admin_menu(request):
    return render(request, 'main/admin_menu.html', {})


@login_required
def quiz_new(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = QuizForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            pre_quiz = form.save(commit=False)
            pre_quiz.save()
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            return HttpResponseRedirect('/admin_menu')

    # if a GET (or any other method) we'll create a blank form
    else:
        form = QuizForm()

    return render(request, 'main/quiz_new.html', {'form': form})

@login_required
def group_new(request):
    # if this is a POST request we need to process the form data
    photo_path = None
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = SimplifiedGroupForm(request.POST)
        photo_path = request.POST.get('photo_path')
        # check whether it's valid:
        if form.is_valid():
            user = form.save()
            user.profile.is_group = True
            user.profile.group_password = form.cleaned_data.get('password1')
            user.profile.group_public_name = form.cleaned_data.get('group_public_name')
            if photo_path != '':
                copy( str(settings.BASE_DIR) + photo_path, settings.MEDIA_ROOT + "/group_pics/" )
                user.profile.group_picture = 'group_pics/' + os.path.basename(photo_path)
            user.save()
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            return HttpResponseRedirect('/admin_menu')

    # if a GET (or any other method) we'll create a blank form
    else:
        form = SimplifiedGroupForm()

    return render(request, 'main/group_new.html', {'form': form, 'photo_path': photo_path})


@login_required
def alum_update(request, pk=None):
    groups_data = None
    tutor = None
    if pk:
        alum = get_object_or_404(User, pk=pk)
        tutor = alum.profile.alum_teacher
        groups_data = alum.profile.alum_in_group.all().order_by('profile__group_public_name')
    else:
        raise forms.ValidationError("No existeix aquest alumne")
    form = AlumUpdateForm(request.POST or None, instance=alum)
    if request.POST and form.is_valid():
        user = form.save(commit=False)
        user.profile.alum_teacher = form.cleaned_data.get('teacher')
        group_ids = request.POST.get('group_ids', '')
        if group_ids == '':
            ids = []
        else:
            ids = group_ids.split(',')
        user.profile.alum_in_group.clear()
        for id in ids:
            group = User.objects.get(pk=int(id))
            user.profile.alum_in_group.add(group)
        user.save()
        return HttpResponseRedirect('/alum/list/')
    return render(request, 'main/alum_edit.html', {'form': form, 'alum_id' : pk, 'groups_data': groups_data, 'tutor': tutor})


@login_required
def alum_new(request):
    # if this is a POST request we need to process the form data
    groups_data = []
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = SimplifiedAlumForm(request.POST)
        # check whether it's valid:
        group_ids = request.POST.get('group_ids', '')
        ids = group_ids.split(',')
        for id in ids:
            group = User.objects.get(pk=int(id))
            groups_data.append(group)
        if form.is_valid():
            user = form.save()
            teacher = form.cleaned_data.get('teacher')
            user.profile.is_alum = True
            user.profile.alum_teacher = teacher
            for group in groups_data:
                user.profile.alum_in_group.add(group)
            user.save()
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            return HttpResponseRedirect('/admin_menu')

    # if a GET (or any other method) we'll create a blank form
    else:
        form = SimplifiedAlumForm()

    return render(request, 'main/alum_new.html', {'form': form, 'groups_data': groups_data})


@login_required
def teacher_new(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = SimplifiedTeacherForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            user = form.save()
            center = form.cleaned_data.get('belongs_to')
            user.profile.is_teacher=True
            user.profile.teacher_belongs_to = center
            user.save()
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            return HttpResponseRedirect('/admin_menu')

    # if a GET (or any other method) we'll create a blank form
    else:
        form = SimplifiedTeacherForm()

    return render(request, 'main/teacher_new.html', {'form': form})


@login_required
def change_password(request, user_id=None):
    this_user = get_object_or_404(User, pk=user_id)
    if request.method == 'POST':
        form = ChangePasswordForm(request.POST)
        if form.is_valid():
            password = form.cleaned_data['password_1']
            this_user.set_password(password)
            this_user.save()
            url = reverse('teacher_list')
            return HttpResponseRedirect(url)
    else:
        form = ChangePasswordForm()
    return render(request, 'main/change_password.html', {'form': form, 'edited_user': this_user})

@login_required
def center_new(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = EducationCenterForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            center = form.save(commit=False)
            geom_string = form.cleaned_data.get('location')
            if geom_string != '':
                geom_json = json.loads(geom_string)
                feature_geometry = GEOSGeometry(json.dumps(geom_json['features'][0]['geometry']))
                center.location = feature_geometry
            else:
                center.location = None
            center.save()
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            return HttpResponseRedirect('/admin_menu')

    # if a GET (or any other method) we'll create a blank form
    else:
        form = EducationCenterForm()

    return render(request, 'main/center_new.html', {'form': form})


def center_to_geojson(center):
    geos = []
    if center.location:
        geos.append({'type': 'Feature', 'properties': {}, 'geometry': json.loads(center.location.json)})
    features = {
        'type': 'FeatureCollection',
        'features': geos
    }
    return json.dumps(features)


@login_required
def center_update(request, pk=None):
    if pk:
        center = get_object_or_404(EducationCenter,pk=pk)
    else:
        raise forms.ValidationError("No existeix aquest centre")
    form = EducationCenterForm(request.POST or None, instance=center)
    geom_text = center_to_geojson(center)
    if request.POST and form.is_valid():
        center = form.save(commit=False)
        geom_string = form.cleaned_data.get('location')
        if geom_string != '':
            geom_json = json.loads(geom_string)
            if len(geom_json['features']) > 0:
                feature_geometry = GEOSGeometry(json.dumps(geom_json['features'][0]['geometry']))
                center.location = feature_geometry
        else:
            center.location = None
        center.save()
        return HttpResponseRedirect('/center/list/')
    return render(request, 'main/center_edit.html', {'form': form, 'center_id' : pk, 'geom': geom_text})


@login_required
def group_update(request, pk=None):
    photo_path = None
    group_password = None
    group_public_name = None
    username = None
    if pk:
        group = get_object_or_404(User,pk=pk)
        if group.profile and group.profile.group_picture:
            photo_path = group.profile.group_picture.url
        group_password = group.profile.group_password
        group_public_name = group.profile.group_public_name
        username = group.username
    else:
        raise forms.ValidationError("No existeix aquest grup")
    form = SimplifiedGroupForm(request.POST or None, instance=group)
    if request.POST and form.is_valid():
        user = form.save(commit=False)
        user.profile.group_password = form.cleaned_data.get('password1')
        user.profile.group_public_name = form.cleaned_data.get('group_public_name')
        photo_path = form.cleaned_data.get('photo_path')
        if photo_path and photo_path != '':
            if str(settings.BASE_DIR) + photo_path != settings.MEDIA_ROOT + "/group_pics/" + os.path.basename(photo_path):
                copy(str(settings.BASE_DIR) + photo_path, settings.MEDIA_ROOT + "/group_pics/")
                user.profile.group_picture = 'group_pics/' + os.path.basename(photo_path)
        else:
            user.profile.group_picture = None
        user.save()
        return HttpResponseRedirect('/group/list/')
    return render(request, 'main/group_edit.html', {'form': form, 'group_id' : pk, 'photo_path': photo_path, 'group_password': group_password, 'group_public_name': group_public_name, 'username': username})


@login_required
def teacher_update(request, pk=None):
    if pk:
        teacher = get_object_or_404(User,pk=pk)
        belongs_to = teacher.profile.teacher_belongs_to
    else:
        raise forms.ValidationError("No existeix aquest professor")
    form = TeacherUpdateForm(request.POST or None, instance=teacher)
    if request.POST and form.is_valid():
        user = form.save(commit=False)
        user.profile.teacher_belongs_to = form.cleaned_data.get('belongs_to')
        user.save()
        return HttpResponseRedirect('/teacher/list/')
    return render(request, 'main/teacher_edit.html', {'form': form, 'teacher_id' : pk, 'belongs_to': belongs_to})


@login_required
def group_list(request):
    return render(request, 'main/group_list.html')

@login_required
def center_list(request):
    return render(request, 'main/center_list.html')


@login_required
def teacher_list(request):
    return render(request, 'main/teacher_list.html')


@login_required
def alum_list(request):
    return render(request, 'main/alum_list.html')


@api_view(['GET'])
def teachers_datatable_list(request):
    if request.method == 'GET':
        search_field_list = ('username','center')
        queryset = User.objects.filter(profile__is_teacher=True)
        field_translation_list = {'username': 'username', 'center': 'profile__teacher_belongs_to__name'}
        sort_translation_list = {'username': 'username', 'center': 'profile__teacher_belongs_to__name'}
        response = generic_datatable_list_endpoint(request, search_field_list, queryset, TeacherSerializer, field_translation_list, sort_translation_list)
        return response


def get_random_row(qs):
    qs_count = qs.count()
    random_index = randint(0, qs_count - 1)
    return qs[random_index]


def generate_random_username_struct():
    color = get_random_row(Word.objects.filter(type='color').order_by('word'))
    adjective = get_random_row(Word.objects.filter(type='adjective').order_by('word'))
    animal = get_random_row(Word.objects.filter(type='animal').order_by('word'))
    group_name = " ".join([adjective.word, color.word, animal.word])
    group_slug = "_".join([adjective.word[0].lower() + color.word[0].lower(), animal.word.lower()])
    return {'group_name': group_name, 'group_slug': group_slug}

def get_max_index_plus_one(slug,numerals):
    nums = []
    for elem in numerals:
        num = elem.username.replace(slug,"")
        if num != '':
            nums.append(int(num))
    if len(nums) == 0:
        return 1
    else:
        return max(nums) + 1

@api_view(['GET'])
def get_random_group_name(request):
    if request.method == 'GET':
        name_struct = generate_random_username_struct()
        slug = name_struct['group_slug']
        if User.objects.filter(username=slug).exists():
            #check if there are already numerals
            numerals = User.objects.filter(username__startswith=slug)
            n = get_max_index_plus_one(slug,numerals)
            name_struct['group_slug'] = slug + str(n)
        return Response(name_struct)


@api_view(['GET'])
def centers_datatable_list(request):
    if request.method == 'GET':
        search_field_list = ('name',)
        queryset = EducationCenter.objects.all()
        response = generic_datatable_list_endpoint(request, search_field_list, queryset, EducationCenterSerializer)
        return response


@api_view(['GET'])
def alum_datatable_list(request):
    if request.method == 'GET':
        search_field_list = ('username','teacher','groups')
        queryset = User.objects.filter(profile__is_alum=True)
        field_translation_list = {'username': 'username', 'teacher': 'profile__alum_teacher__username', 'groups': 'profile__groups_string'}
        sort_translation_list = {'username': 'username', 'teacher': 'profile__alum_teacher__username', 'groups': 'profile__groups_string'}
        response = generic_datatable_list_endpoint(request, search_field_list, queryset, AlumSerializer, field_translation_list, sort_translation_list)
        return response


@api_view(['GET'])
def group_datatable_list(request):
    if request.method == 'GET':
        search_field_list = ('username','group_public_name')
        queryset = User.objects.filter(profile__is_group=True)
        field_translation_list = {'username': 'username', 'group_public_name':'profile__group_public_name'}
        sort_translation_list = {'username': 'username', 'group_public_name':'profile__group_public_name'}
        response = generic_datatable_list_endpoint(request, search_field_list, queryset, GroupSerializer, field_translation_list, sort_translation_list)
        return response


@api_view(['GET'])
def group_search(request):
    if request.method == 'GET':
        q = request.query_params.get('q','')
        if q != '':
            queryset = User.objects.filter(profile__is_group=True).filter(profile__group_public_name__icontains=q).order_by('profile__group_public_name')
        else:
            queryset = User.objects.filter(profile__is_group=True).order_by('profile__group_public_name')
        serializer = GroupSearchSerializer(queryset, many=True)
        return Response(serializer.data)


@login_required
def uploadpic(request):
    if request.method == 'POST':
        file = request.FILES
        f = request.FILES['camp_foto']
        with open(settings.MEDIA_ROOT + "/tempfiles/" + f.name, 'wb+') as destination:
            for chunk in f.chunks():
                destination.write(chunk)
        data = {'is_valid': True, 'id':1, 'url':'/media/tempfiles/'+f.name, 'path':settings.MEDIA_ROOT + "/tempfiles/" + f.name}
        return JsonResponse(data)
        # form = PhotoForm(request.POST, request.FILES)
        # if form.is_valid():
        #     foto = form.save(commit=False)
        #     foto.save()
        #     data = {'is_valid': True, 'id': foto.id, 'url': foto.camp_foto.url }
        # else:
        #     data = {'is_valid': False, 'errors': form.errors['foto']}
        # return JsonResponse(data)


class CentersViewSet(viewsets.ModelViewSet):
    queryset = EducationCenter.objects.all()
    serializer_class = EducationCenterSerializer


class UserPartialUpdateView(GenericAPIView, UpdateModelMixin):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def put(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)


class EducationCenterPartialUpdateView(GenericAPIView, UpdateModelMixin):
    '''
    You just need to provide the field which is to be modified.
    '''
    queryset = EducationCenter.objects.all()
    serializer_class = EducationCenterSerializer

    def put(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)