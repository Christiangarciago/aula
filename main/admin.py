from django.contrib import admin

# Register your models here.

from .models import *

admin.site.register(EducationCenter)
admin.site.register(Quiz)
admin.site.register(TakenQuiz)
admin.site.register(Question)
admin.site.register(GroupAnswer)