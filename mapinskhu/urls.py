"""mapinskhu URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf import settings 
from django.conf.urls.static import static
import classApp.views, feedbackApp.views, baseApp.views

urlpatterns = [
    path('api/classrooms/', classApp.views.get_classroom_list, name='get_classroom_list'),
    path('api/classroom/<int:room_id>/', classApp.views.get_classroom_detail, name='get_classroom_detail'),

    path('skhu21it4/', admin.site.urls),

    path('', baseApp.views.index, name='index'),
    path('introduce/', baseApp.views.introduce, name='introduce'),
    path('search/', baseApp.views.search, name = 'search'),
    
    # path('dormitory/', classApp.views.dormitory, name='dormitory'),
    # path('gdin_gwan/', classApp.views.gdin_gwan, name='gdin_gwan'),
    # path('im_gwan/', classApp.views.im_gwan, name='im_gwan'),
    # path('jg_gwan/', classApp.views.jg_gwan, name='jg_gwan'),
    # path('library/', classApp.views.library, name='library'),
    # path('mgell_gwan/', classApp.views.mgell_gwan, name='mgell_gwan'),
    # path('nn_gwan/', classApp.views.nn_gwan, name='nn_gwan'),
    # path('pb_hall/', classApp.views.pb_hall, name='pb_hall'),
    # path('sbdr_school/', classApp.views.sbdr_school, name='sbdr_school'),
    # path('scn_gwan/', classApp.views.scn_gwan, name='scn_gwan'),
    # path('sy_gwan/', classApp.views.sy_gwan, name='sy_gwan'),
    # path('wd_gwan/', classApp.views.wd_gwan, name='wd_gwan'),
    # path('classroom/<str:room>/', classApp.views.classroom, name='classroom'),

    path('feedback/', feedbackApp.views.feedback, name='feedback'),
    path('feedback_cp/', feedbackApp.views.feedback_cp, name='feedback_cp'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
