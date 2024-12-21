from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

class FitnessData(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    height = models.FloatField(default=170)  # Set default value for height
    weight = models.FloatField()
    bmi = models.FloatField()
    step_count = models.IntegerField()
    calculated_distance = models.FloatField()
    sleep_duration = models.FloatField()
    stress_level = models.IntegerField()  # Store stress level as a number (0, 1, or 2)
    hydration_level = models.FloatField()
    activity_level = models.CharField(max_length=20)
    bmr = models.FloatField()
    tdee = models.FloatField()
    status = models.CharField(max_length=10)
    message = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)  # Provide default value for created_at
    
    def __str__(self):
        return f"Fitness Data for {self.user.username} - {self.status}"



