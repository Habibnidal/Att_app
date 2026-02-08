from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('import-students/', views.import_students, name='import_students'),
    path('attendance-list/', views.attendance_list, name='attendance_list'),
    path('take-attendance/', views.take_attendance, name='take_attendance'),
    path('mark-attendance/', views.mark_attendance, name='mark_attendance'),
    path('attendance-complete/', views.attendance_complete, name='attendance_complete'),
    path('print-absentees/', views.print_absentees, name='print_absentees'),
    path('absentees-list/', views.absentees_list, name='absentees_list'),
]
