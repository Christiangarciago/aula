from rest_framework import serializers
from main.models import EducationCenter
from django.contrib.auth.models import User


class EducationCenterSerializer(serializers.ModelSerializer):
    pos_x = serializers.SerializerMethodField()
    pos_y = serializers.SerializerMethodField()

    class Meta:
        model = EducationCenter
        fields = '__all__'

    def get_pos_x(self, obj):
        geom = obj.location
        if geom is None:
            return None
        else:
            return geom.y

    def get_pos_y(self, obj):
        geom = obj.location
        if geom is None:
            return None
        else:
            return geom.x


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class AlumSerializer(serializers.ModelSerializer):
    teacher = serializers.SerializerMethodField('get_teacher')
    groups = serializers.SerializerMethodField('get_groups')

    class Meta:
        model = User
        fields = '__all__'

    def get_teacher(self,obj):
        if obj.profile and obj.profile.alum_teacher:
            return obj.profile.alum_teacher.username
        else:
            return ''

    def get_groups(self, obj):
        return obj.profile.groups_string


class GroupSearchSerializer(serializers.ModelSerializer):
    text = serializers.SerializerMethodField('get_text')
    class Meta:
        model = User
        fields = ['id','text']

    def get_text(self, obj):
        return obj.profile.group_public_name


class GroupSerializer(serializers.ModelSerializer):
    group_password = serializers.SerializerMethodField('get_group_password')
    group_public_name = serializers.SerializerMethodField('get_group_public_name')
    group_center = serializers.SerializerMethodField('get_group_center')
    group_alums = serializers.SerializerMethodField('get_group_alums')
    group_picture = serializers.SerializerMethodField('get_group_picture')

    class Meta:
        model = User
        fields = '__all__'

    def get_group_password(self,obj):
        return obj.profile.group_password

    def get_group_public_name(self, obj):
        return obj.profile.group_public_name

    def get_group_center(self,obj):
        return 'to_do'

    def get_group_alums(self,obj):
        return 'to_do_also'

    def get_group_picture(self,obj):
        if obj.profile:
            if obj.profile.group_picture:
                return obj.profile.group_picture.url
        return ''


class TeacherSerializer(serializers.ModelSerializer):
    center = serializers.SerializerMethodField('get_center')

    class Meta:
        model = User
        fields = '__all__'

    def get_center(self,obj):
        if obj.profile:
            return obj.profile.teacher_belongs_to.name
        else:
            return ''