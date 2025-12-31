from django.db.models import Count, DurationField, ExpressionWrapper, F, Sum, Q
from django.shortcuts import render
from .models import Processes

def wrapped(request):

    if request.method == "POST":
        user_name = request.POST.get('user_name', 'anonymous')
        
        # Single query with all annotations
        user_processes = Processes.objects.filter(submitted_user=user_name).annotate(
            duration=ExpressionWrapper(
                F('datetime_ended') - F('datetime_started'),
                output_field=DurationField()
            )
        )

        count_of_user_processes = user_processes.count()
        
        if count_of_user_processes == 0:
            context = {
                'user_name': user_name,
                'no_data': True,
            }
            return render(request, "wrapped/wrapped.html", context)
        
        # Top processes - force evaluation with list()
        top_processes = list(user_processes.values('submitted_process').annotate(total=Count('id')).order_by('-total')[:5])

        # Total duration
        total_duration = user_processes.aggregate(total_time=Sum('duration'))['total_time']
        total_hours = total_duration.total_seconds() // 3600
        total_days = round((total_hours / 24), 2)
    
        # Queued processes + office hours in ONE query
        combined_stats = user_processes.aggregate(
            queued=Count('id', filter=Q(datetime_queued__isnull=False)),
            not_queued=Count('id', filter=Q(datetime_queued__isnull=True)),
            outside=Count('id', filter=Q(
                Q(datetime_started__hour__lt=8) |
                Q(datetime_started__hour=17, datetime_started__minute__gte=30) |
                Q(datetime_started__hour__gte=18)
            )),
            inside=Count('id', filter=Q(
                Q(datetime_started__hour__gte=8, datetime_started__hour__lt=17) |
                Q(datetime_started__hour=17, datetime_started__minute__lt=30)
            ))
        )
        
        processes_queued = combined_stats['queued']
        processes_not_queued = combined_stats['not_queued']
        outside_office_hours = combined_stats['outside']
        inside_office_hours = combined_stats['inside']
        
        processes_queued_ratio = round((processes_queued / count_of_user_processes) * 100, 2) if count_of_user_processes > 0 else 0

        if processes_queued > processes_not_queued:
            queued_message = "Great job! You queue most of your processes before starting them. This helps to optimise automation performance."
        else:
            queued_message = "You don't queue the majority of your processes but that's not a problem! If you can, consider queuing more processes before starting them to help optimise automation performance."

        if outside_office_hours > inside_office_hours:
            office_hours_message = "You run processes more often outside of office hours. Great job on maximising automation!"
        else:
            office_hours_message = "You run processes more often inside of office hours. Consider scheduling more outside of office hours to maximise automation!"

        # Longest processes - force evaluation with list()
        longest_processes_raw = list(user_processes.order_by('-duration')[:5])
        longest_processes_data = []
        for process in longest_processes_raw:
            minutes = process.duration.total_seconds() / 60
            longest_processes_data.append({
                'label': f"{process.customer} - {process.submitted_process}",
                'minutes': round(minutes, 1),
                'duration': process.duration
            })

        # Process B rankings
        specific_process = 'Process_B'
        process_b_rankings = list(
            Processes.objects.filter(submitted_process=specific_process)
            .values('submitted_user')
            .annotate(submitted_count=Count('id'))
            .order_by('-submitted_count')
        )

        user_rank = None
        user_count = 0
        total_process_b = sum(entry['submitted_count'] for entry in process_b_rankings)

        for index, entry in enumerate(process_b_rankings):
            if entry['submitted_user'] == user_name:
                user_rank = index + 1
                user_count = entry['submitted_count']
                break

        user_percentage = round((user_count / total_process_b) * 100, 2) if total_process_b > 0 else 0

        # User's top process rankings
        user_top_process = top_processes[0]['submitted_process']
        top_process_rankings = list(
            Processes.objects.filter(submitted_process=user_top_process)
            .values('submitted_user')
            .annotate(submitted_count=Count('id'))
            .order_by('-submitted_count')
        )

        top_process_user_rank = None
        top_process_user_count = 0
        total_top_process = sum(entry['submitted_count'] for entry in top_process_rankings)

        for index, entry in enumerate(top_process_rankings):
            if entry['submitted_user'] == user_name:
                top_process_user_rank = index + 1
                top_process_user_count = entry['submitted_count']
                break

        top_process_user_percentage = round((top_process_user_count / total_top_process) * 100, 2) if total_top_process > 0 else 0

        # Top customers - force evaluation with list()
        top_customers = list(user_processes.values('customer').annotate(customer_count=Count('id')).order_by('-customer_count')[:10])
        user_top_customer = top_customers[0]['customer']
        user_top_customer_count = top_customers[0]['customer_count']
        user_top_customer_percentage = round((user_top_customer_count / count_of_user_processes) * 100, 2) if count_of_user_processes > 0 else 0

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
        'longest_processes': longest_processes_raw,
        'longest_processes_data': longest_processes_data,
        'office_hours_message': office_hours_message,
        'queued_message': queued_message,
        'user_rank': user_rank,
        'user_count': user_count,
        'user_percentage': user_percentage,
        'top_process_user_rank': top_process_user_rank,
        'user_top_process': user_top_process,
        'top_process_user_percentage': top_process_user_percentage,
        'top_process_user_count': top_process_user_count,
        'top_customers': top_customers,
        'user_top_customer': user_top_customer,
        'user_top_customer_count': user_top_customer_count,
        'user_top_customer_percentage': user_top_customer_percentage,
    }
    return render(request, "wrapped/wrapped_tailwind_report.html", context)