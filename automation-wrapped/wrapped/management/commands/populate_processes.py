from django.core.management.base import BaseCommand
from django.utils import timezone
from wrapped.models import Processes
from datetime import datetime, timedelta
import random


class Command(BaseCommand):
    help = 'Populates the database with 1000 sample process records'

    def handle(self, *args, **kwargs):
        # Clears all the data first, comment out if you just want to add.
        Processes.objects.all().delete()
        self.stdout.write('Cleared existing process data')

        # Generate 20 different users with random names
        first_names = ['Alice', 'Bob', 'Charlie', 'Diana', 'Eve', 'Frank', 'Grace', 'Henry', 
                       'Iris', 'Jack', 'Kate', 'Liam', 'Maya', 'Noah', 'Olivia', 'Peter', 
                       'Quinn', 'Ruby', 'Sam', 'Tara']
        last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 
                      'Davis', 'Rodriguez', 'Martinez', 'Hernandez', 'Lopez', 'Gonzalez', 
                      'Wilson', 'Anderson', 'Thomas', 'Taylor', 'Moore', 'Jackson', 'Martin']
        
        # Create 20 unique full names
        users = [f'{first} {last}' for first, last in zip(first_names, last_names)]
        
        # Get process choices from the model
        process_choices = [choice[0] for choice in Processes.PROCESSES]
        process_type_choices = [choice[0] for choice in Processes.PROCESSES_TYPE]
        
        # Generate 1000 records
        processes_to_create = []
        
        # Date range for 2025 data
        start_date = timezone.make_aware(datetime(2025, 1, 1))
        end_date = timezone.make_aware(datetime(2025, 12, 31))
        total_days = (end_date - start_date).days
        
        for i in range(1000):
            # Generate random start time within 2025
            random_days = random.randint(0, total_days)
            random_seconds = random.randint(180, 86400)
            datetime_started = start_date + timedelta(days=random_days, seconds=random_seconds)
            
            # Generate end time after start time (1-120 minutes later)
            duration_minutes = random.randint(1, 120)
            datetime_ended = datetime_started + timedelta(minutes=duration_minutes)
            
            # Randomly select user, process, and process type
            submitted_user = random.choice(users)
            submitted_process = random.choice(process_choices)
            process_type = random.choice(process_type_choices)
            
            # 15% chance to have a queued datetime (5-60 minutes before started)
            datetime_queued = None
            if random.random() < 0.15:
                queue_minutes = random.randint(100, 1200)
                datetime_queued = datetime_started - timedelta(minutes=queue_minutes)
            
            # Create Processes object and append to list
            process = Processes(
                datetime_started=datetime_started,
                datetime_ended=datetime_ended,
                submitted_user=submitted_user,
                submitted_process=submitted_process,
                process_type=process_type,
                datetime_queued=datetime_queued
            )
            processes_to_create.append(process)
        
        # Bulk create all processes at once
        Processes.objects.bulk_create(processes_to_create)
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created 1000 process records')
        )
