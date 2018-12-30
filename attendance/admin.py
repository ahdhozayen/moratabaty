from django.contrib import admin
from attendance.models import Attendance, DayOffRule, DayOff

# Inlines
class DayOffInline(admin.TabularInline):
    model = DayOff


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    fields = (
        'employee_id',
        'is_final',
        'department',
        'section',
        'sub_section',
        'degree',
        'year',
        'month',
        'overtime_hours',
        'total_working_days_in_month',
        'total_attended_days',
    )
    
    readonly_fields = (
        'department',
        'section',
        'sub_section',
        'degree',
        'total_attended_days',
        )
    inlines = [
        DayOffInline,
    ]

admin.site.register([DayOffRule, DayOff])
    