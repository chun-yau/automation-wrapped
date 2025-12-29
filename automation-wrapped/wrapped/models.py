from django.db import models

class Processes(models.Model):

    PROCESSES = [
        ('Process_A', 'Process A'),
        ('Process_B', 'Process B'),
        ('Process_C', 'Process C'),
        ('Process_D', 'Process D'),
        ('Process_E', 'Process E'),
        ('Process_F', 'Process F'),
    ]

    PROCESSES_TYPE = [
        ('Type_1', 'Type 1'),
        ('Type_2', 'Type 2'),
        ('Type_3', 'Type 3'),
    ]

    datetime_started = models.DateTimeField()
    datetime_ended = models.DateTimeField()
    submitted_user = models.CharField(max_length=100)
    submitted_process = models.CharField(max_length=100, choices=PROCESSES)
    process_type = models.CharField(max_length=100, choices=PROCESSES_TYPE)
    datetime_queued = models.DateTimeField(null=True, blank=True)
    customer = models.CharField(max_length=255, null=True, blank=True)
