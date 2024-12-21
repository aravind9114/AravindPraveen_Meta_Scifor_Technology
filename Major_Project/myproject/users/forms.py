from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'password', 'email']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])  # This hashes the password
        if commit:
            user.save()
        return user
# forms.py

from django import forms

class FitnessForm(forms.Form):
    name = forms.CharField(label='Name', max_length=100)
    age = forms.IntegerField(label='Age', min_value=0, max_value=150)
    gender = forms.ChoiceField(label='Gender', choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')])
    height = forms.FloatField(label='Height (cm)', min_value=50, max_value=250)
    weight = forms.FloatField(label='Weight (kg)', min_value=10, max_value=200)
    step_count = forms.IntegerField(label='Step Count (daily)', min_value=0, max_value=50000)
    sleep_duration = forms.FloatField(label='Sleep Duration (hours)', min_value=0, max_value=24)
    stress_level = forms.ChoiceField(label='Stress Level', choices=[('Low', 'Low'), ('Medium', 'Medium'), ('High', 'High')])
    hydration_level = forms.FloatField(label='Hydration Level (Liters)', min_value=0.0, max_value=10.0)
    activity_level = forms.ChoiceField(label='Activity Level', choices=[
        ('Sedentary', 'Sedentary'),
        ('Lightly Active', 'Lightly Active'),
        ('Moderately Active', 'Moderately Active'),
        ('Very Active', 'Very Active'),
        ('Super Active', 'Super Active'),
    ])

