# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('mark_attendance/', views.mark_attendance, name='mark_attendance'),
    path('time_out/<int:attendance_id>/', views.time_out, name='time_out'),
    path('attendance_already_marked/', views.attendance_already_marked, name='attendance_already_marked'),
]
