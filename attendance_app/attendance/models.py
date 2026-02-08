from django.db import models
from django.utils import timezone

class Student(models.Model):
    student_name = models.CharField(max_length=100)
    roll_number = models.CharField(max_length=20, unique=True)
    course_name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['roll_number']
    
    def __str__(self):
        return f"{self.roll_number} - {self.student_name}"

class Absence(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='absences')
    date_time = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-date_time']
    
    def __str__(self):
        return f"{self.student.student_name} - {self.date_time.strftime('%Y-%m-%d %H:%M')}"
