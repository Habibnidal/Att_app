from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from .models import Student, Absence
import pandas as pd
from datetime import datetime

def home(request):
    return render(request, 'attendance/home.html')

def import_students(request):
    if request.method == 'POST' and request.FILES.get('excel_file'):
        try:
            excel_file = request.FILES['excel_file']
            
            # Determine file extension and use appropriate engine
            file_extension = excel_file.name.split('.')[-1].lower()
            if file_extension == 'csv':
                df = pd.read_csv(excel_file)
            elif file_extension in ['xlsx', 'xls']:
                df = pd.read_excel(excel_file, engine='openpyxl')
            else:
                messages.error(request, 'Unsupported file format. Please use .xlsx, .xls, or .csv files')
                return redirect('import_students')
            
            required_columns = ['Student Name', 'Roll Number', 'Course Name']
            if not all(col in df.columns for col in required_columns):
                messages.error(request, 'Excel file must contain columns: Student Name, Roll Number, Course Name')
                return redirect('import_students')
            
            students_created = 0
            for index, row in df.iterrows():
                student, created = Student.objects.get_or_create(
                    roll_number=str(row['Roll Number']).strip(),
                    defaults={
                        'student_name': str(row['Student Name']).strip(),
                        'course_name': str(row['Course Name']).strip()
                    }
                )
                if created:
                    students_created += 1
            
            messages.success(request, f'Successfully imported {students_created} students')
            return redirect('attendance_list')
            
        except Exception as e:
            messages.error(request, f'Error importing file: {str(e)}')
            return redirect('import_students')
    
    return render(request, 'attendance/import_students.html')

def attendance_list(request):
    students = Student.objects.all().order_by('roll_number')
    
    # Get today's absences
    today = timezone.now().date()
    today_absences = Absence.objects.filter(
        date_time__date=today
    ).values_list('student_id', flat=True)
    
    # Add attendance status to each student
    students_with_status = []
    for student in students:
        students_with_status.append({
            'student': student,
            'is_absent': student.id in today_absences,
            'sl_no': len(students_with_status) + 1
        })
    
    return render(request, 'attendance/attendance_list.html', {
        'students_with_status': students_with_status
    })

def take_attendance(request):
    students = Student.objects.all().order_by('roll_number')
    current_index = int(request.GET.get('index', 0))
    
    if current_index >= len(students):
        return redirect('attendance_complete')
    
    current_student = students[current_index]
    
    # Get today's absence status for current student
    today = timezone.now().date()
    is_absent_today = Absence.objects.filter(
        student=current_student,
        date_time__date=today
    ).exists()
    
    return render(request, 'attendance/take_attendance.html', {
        'current_student': current_student,
        'current_index': current_index,
        'total_students': len(students),
        'progress': ((current_index + 1) / len(students)) * 100,
        'is_absent_today': is_absent_today
    })

def mark_attendance(request):
    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        action = request.POST.get('action')  # 'present' or 'absent'
        current_index = int(request.POST.get('current_index', 0))
        
        student = get_object_or_404(Student, id=student_id)
        today = timezone.now().date()
        
        if action == 'absent':
            # Create or update absence record
            absence, created = Absence.objects.get_or_create(
                student=student,
                date_time__date=today,
                defaults={'date_time': timezone.now()}
            )
        else:
            # Remove absence record if exists
            Absence.objects.filter(
                student=student,
                date_time__date=today
            ).delete()
        
        # Move to next student
        next_index = current_index + 1
        return redirect(f'/take-attendance/?index={next_index}')
    
    return redirect('take_attendance')

def attendance_complete(request):
    today = timezone.now().date()
    absent_students = Absence.objects.filter(
        date_time__date=today
    ).select_related('student')
    
    return render(request, 'attendance/attendance_complete.html', {
        'absent_students': absent_students,
        'total_absent': absent_students.count()
    })

def print_absentees(request):
    today = timezone.now().date()
    absent_students = Absence.objects.filter(
        date_time__date=today
    ).select_related('student').order_by('student__roll_number')
    
    total_students = Student.objects.count()
    total_present = total_students - absent_students.count()
    attendance_percentage = round((total_present / total_students * 100) if total_students > 0 else 0, 2)
    
    return render(request, 'attendance/print_absentees.html', {
        'absent_students': absent_students,
        'date': today.strftime('%Y-%m-%d'),
        'total_absent': absent_students.count(),
        'total_present': total_present,
        'attendance_percentage': attendance_percentage
    })

def absentees_list(request):
    date_filter = request.GET.get('date')
    if date_filter:
        try:
            filter_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
            absent_students = Absence.objects.filter(
                date_time__date=filter_date
            ).select_related('student').order_by('student__roll_number')
        except ValueError:
            absent_students = Absence.objects.none()
    else:
        today = timezone.now().date()
        absent_students = Absence.objects.filter(
            date_time__date=today
        ).select_related('student').order_by('student__roll_number')
        filter_date = today
    
    return render(request, 'attendance/absentees_list.html', {
        'absent_students': absent_students,
        'filter_date': filter_date,
        'total_absent': absent_students.count()
    })
