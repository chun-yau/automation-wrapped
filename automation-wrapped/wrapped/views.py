from django.db.models import Count, DurationField, ExpressionWrapper, F, Sum, Q
from django.shortcuts import render
from .models import Processes

from datetime import time



def wrapped(request):

    if request.method == "POST":
        user_name = request.POST.get('user_name', 'anonymous')
        user_processes = Processes.objects.filter(submitted_user = user_name)

        if user_processes.count() == 0:
            context = {
                'user_name': user_name,
                'no_data': True,
            }
            return render(request, "wrapped/wrapped.html", context)

        count_of_user_processes = user_processes.count()
        top_processes = user_processes.values('submitted_process').annotate(total=Count('id')).order_by('-total')[:5]

        # Calculate total duration of all processes for the user
        ## Use ExpressionWrapper to calculate duration for each process (database calculation)
        processes_duration = user_processes.annotate(
            duration=ExpressionWrapper(
                F('datetime_ended') - F('datetime_started'),
                output_field=DurationField()
            )
        )
        ## Aggregate to get the total duration
        processes_duration = processes_duration.aggregate(
            total_time=Sum('duration')
        )

        ## Convert total duration to hours and days
        total_hours = processes_duration['total_time'].total_seconds() // 3600
        total_days = round((total_hours / 24), 2)
    
        # Calculate numhber of processes queued and ratio
        processes_queued = user_processes.filter(datetime_queued__isnull=False).count()
        processes_not_queued = user_processes.exclude(datetime_queued__isnull=False).count()
        if count_of_user_processes > 0:
            processes_queued_ratio = round((processes_queued / count_of_user_processes) * 100, 2)
        else:
            processes_queued_ratio = 0

        if processes_queued > processes_not_queued:
            queued_message = "Great job! You queue most of your processes before starting them. This helps to optimise automation performance."
        else:
            queued_message = "You don't queue the majority of your processes but that's not a problem! If you can, consider queuing more processes before starting them to help optimise automation performance."

        # Processes started outside of office hours (08:00 - 17:30)
        outside_office_hours = user_processes.filter(
            Q(datetime_started__hour__lt = 8) |
            Q(datetime_started__hour = 17) & Q(datetime_started__minute__gte = 30) |
            Q(datetime_started__hour__gte = 18)
        ).count()

        # Processes started inside of office hours (08:00 - 17:30)
        # Wrote it this way to be explicit and made sure it matches the total count
        inside_office_hours = user_processes.filter(
            Q(datetime_started__hour__gte = 8) &
            Q(datetime_started__hour__lt = 17) |
            Q(datetime_started__hour = 17) & Q(datetime_started__minute__lt = 30)
        ).count()

        if outside_office_hours > inside_office_hours:
            office_hours_message = "You run processes more often outside of office hours. Great job on maximising automation!"
        else:
            office_hours_message = "You run processes more often inside of office hours. Consider scheduling more outside of office hours to maximise automation!"

        # Get their longest 5 processes by duration
        longest_processes = user_processes.annotate(
            duration=ExpressionWrapper(
                F('datetime_ended') - F('datetime_started'),
                output_field=DurationField()
            )
        ).order_by('-duration')[:5]


    else:
        return render(request, "wrapped/wrapped.html")
        

    context = {
        'user_name': user_name,
        'count_of_user_processes': count_of_user_processes,
        'top_processes': top_processes,
        'total_days': total_days,
        'total_hours': total_hours,
        'processes_queued_ratio': processes_queued_ratio,
        'processes_not_queued': processes_not_queued,
        'processes_queued': processes_queued,
        'outside_office_hours': outside_office_hours,
        'inside_office_hours': inside_office_hours,
        'longest_processes': longest_processes,
        'office_hours_message': office_hours_message,
        'queued_message': queued_message,
    }
    return render(request, "wrapped/wrapped_tailwind_report.html", context)
