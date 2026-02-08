from django.contrib import admin
from .models import Student, Absence

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['roll_number', 'student_name', 'course_name', 'created_at']
    list_filter = ['course_name', 'created_at']
    search_fields = ['student_name', 'roll_number', 'course_name']
    ordering = ['roll_number']

@admin.register(Absence)
class AbsenceAdmin(admin.ModelAdmin):
    list_display = ['student', 'date_time']
    list_filter = ['date_time']
    search_fields = ['student__student_name', 'student__roll_number']
    ordering = ['-date_time']
    date_hierarchy = 'date_time'
