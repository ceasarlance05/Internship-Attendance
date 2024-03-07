
from django.shortcuts import render, redirect
from django.utils import timezone
from .models import Department, Intern, Attendance
from pytz import timezone as pytz_timezone 

def home(request):
    departments = Department.objects.all()
    interns = Intern.objects.all()
    return render(request, 'attendance/home.html', {'departments': departments, 'interns': interns})

def mark_attendance(request):
    if request.method == 'POST':
        intern_id = request.POST.get('intern')
        intern = Intern.objects.get(pk=intern_id)

        # Get the current date
        current_date = timezone.now().date()

        # Check if the intern has already timed in for today
        if Attendance.objects.filter(intern=intern, time_in__date=current_date).exists():
            # Intern has already timed in for today, redirect them with a message
            return redirect('attendance_already_marked')

        time_in = timezone.now()
        attendance = Attendance.objects.create(intern=intern, time_in=time_in)
        attendance.save()

        # Convert time_in to desired timezone (GMT+8)
        gmt_plus_eight = pytz_timezone('Asia/Shanghai')
        time_in = time_in.astimezone(gmt_plus_eight)

        return render(request, 'attendance/mark_attendance.html', {'attendance': attendance})
    else:
        # Handle GET request if needed
        pass

def time_out(request, attendance_id):
    attendance = Attendance.objects.get(pk=attendance_id)
    attendance.time_out = timezone.now()
    attendance.save()
    return redirect('home')

def attendance_already_marked(request):
    return render(request, 'attendance/attendance_already_marked.html')