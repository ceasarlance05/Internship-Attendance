from django.contrib import admin
from django.utils import timezone
from pytz import timezone as pytz_timezone
from .models import Department, Intern, Attendance
from django.http import HttpResponse
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from .models import Attendance
from datetime import timedelta
import pytz
from django.urls import path

admin.site.register(Department)
admin.site.register(Intern)

class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['intern', 'get_time_in_gmt8', 'get_time_out_gmt8']
    actions = ['generate_attendance_report']

    def get_time_in_gmt8(self, obj):
        gmt_plus_eight = pytz.timezone('Asia/Shanghai')
        time_in_gmt8 = obj.time_in.astimezone(gmt_plus_eight)
        return time_in_gmt8.strftime("%Y-%m-%d %H:%M:%S")

    def get_time_out_gmt8(self, obj):
        if obj.time_out:
            gmt_plus_eight = pytz.timezone('Asia/Shanghai')
            time_out_gmt8 = obj.time_out.astimezone(gmt_plus_eight)
            return time_out_gmt8.strftime("%Y-%m-%d %H:%M:%S")
        else:
            return None

    def generate_attendance_report(self, request, queryset):
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="attendance_report.pdf"'

        # Retrieve the intern name and department name from the first attendance record in queryset
        first_record = queryset.first()
        intern_name = first_record.intern.name
        department_name = first_record.intern.department.name

        # Filter attendance records for the selected intern
        attendance_records = Attendance.objects.filter(intern__name=intern_name)

        # Create a PDF document
        doc = SimpleDocTemplate(response, pagesize=letter)
        elements = []

        # Add heading with intern name and department name
        styles = getSampleStyleSheet()
        elements.append(Paragraph(f"<b>Attendance Report for {intern_name} in {department_name}</b>", styles['Heading1']))
        elements.append(Spacer(1, 12))  # Add space after heading

        # Initialize table data and intern total hours
        table_data = [['Time In (GMT+8)', 'Time Out (GMT+8)', 'Total Hours']]
        intern_total_hours = timedelta()

        # Calculate total hours for each attendance record and add to table data
        for attendance in attendance_records:
            time_in = attendance.time_in
            time_out = attendance.time_out

            # Calculate total hours
            total_hours = None
            if time_in and time_out:
                total_hours = time_out - time_in
                # Subtract one hour for each day
                total_hours -= timedelta(days=total_hours.days)
                intern_total_hours += total_hours

            # Add attendance record to table data
            table_data.append([self.get_time_in_gmt8(attendance), self.get_time_out_gmt8(attendance), total_hours])

        # Create a table and style
        table = Table(table_data)
        style = TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                            ('GRID', (0, 0), (-1, -1), 1, colors.black)])

        table.setStyle(style)
        elements.append(table)
        elements.append(Spacer(1, 12))  # Add space between table and total hours

        # Add grand total hours in hours only
        total_hours_str = f"Total Hours: {intern_total_hours.days * 24 + intern_total_hours.seconds // 3600} Hours"
        elements.append(Paragraph(total_hours_str, styles['Normal']))

        # Add elements to the PDF document
        doc.build(elements)
        return response

    generate_attendance_report.short_description = "Generate Attendance Report"

admin.site.register(Attendance, AttendanceAdmin)