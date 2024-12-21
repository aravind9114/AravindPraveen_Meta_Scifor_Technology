from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import UserRegistrationForm, FitnessForm
import pickle
from django.contrib.auth.decorators import login_required


# Registration View
def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            
            return redirect('login')  # Redirect to the login page
    else:
        form = UserRegistrationForm()
    return render(request, 'users/register.html', {'form': form})

from django.contrib.auth import authenticate, login
from django.shortcuts import redirect, render
from django.contrib import messages

# Login View
def login_user(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        
        # Authenticate user
        user = authenticate(request, username=username, password=password)
        
        # Check if authentication was successful
        if user is not None:
            login(request, user)  # Log the user in
            return redirect('fitness_form')  # Redirect to the fitness form or home page
        else:
            messages.error(request, "Invalid username or password.")  # Error message if login fails

    return render(request, 'users/login.html')

# Logout View
def logout_user(request):
    logout(request)
    return redirect('home')  # Redirect to the home page

# Home View
def home(request):
    return render(request, 'users/home.html')




# views.py

import joblib
from django.shortcuts import render
from .forms import FitnessForm

# Load the pre-trained model and scaler


# Functions for calculations
def calculate_bmr(gender, weight, height, age):
    if gender == "Male":
        return 10 * weight + 6.25 * height - 5 * age + 5
    elif gender == "Female":
        return 10 * weight + 6.25 * height - 5 * age - 161
    else:
        return 10 * weight + 6.25 * height - 5 * age

def calculate_tdee(bmr, activity_level):
    activity_factors = {
        "Sedentary": 1.2,
        "Lightly Active": 1.375,
        "Moderately Active": 1.55,
        "Very Active": 1.725,
        "Super Active": 1.9
    }
    return bmr * activity_factors.get(activity_level, 1.2)

def calculate_distance_from_steps(step_count):
    stride_length = 0.762  # in meters (average stride length)
    return step_count * stride_length
from django.shortcuts import render
from django.http import HttpResponse
from .forms import FitnessForm  # Import your form
import joblib

# Assuming the models and scaler have been trained and saved previously
from .models import FitnessData

def fitness_view(request):
    # Load model and scaler
    model = joblib.load(r'C:\Users\ASUS\OneDrive\Desktop\Major_Project\myproject\Random_forest_Fitness_correct.pkl')
    scaler = joblib.load(r'C:\Users\ASUS\OneDrive\Desktop\Major_Project\myproject\Fitness_scaler_correct.pkl')

    if request.method == 'POST':
        form = FitnessForm(request.POST)
        if form.is_valid():
            # Get data from form
            data = form.cleaned_data
            height = data['height']
            weight = data['weight']
            bmi = weight / (height / 100) ** 2  # Calculate BMI if not provided
            step_count = data['step_count']
            sleep_duration = data['sleep_duration']
            stress_level = {'Low': 2, 'Medium': 1, 'High': 0}[data['stress_level']]  # Convert stress level to numerical value
            hydration_level = data['hydration_level']
            activity_level = data['activity_level']
            
            # Perform additional calculations
            calculated_distance = calculate_distance_from_steps(step_count)  # Calculate distance from step count
            bmr = calculate_bmr(data['gender'], weight, height, data['age'])  # Implement this function
            tdee = calculate_tdee(bmr, activity_level)  # Implement this function
            
            # Determine fitness status and message
            prediction_input = [[height, weight, bmi, step_count, calculated_distance, sleep_duration, stress_level, hydration_level]]
            input_data = scaler.transform(prediction_input)  # Scale the input data
            prediction = model.predict(input_data)
            
            if prediction == 0:  # Fit
                message = "🎉 You are Healthy!"
                status = "Fit"
            else:  # Not Fit
                message = "🛑 You may need to improve your health routine."
                status = "Not Fit"
            
            # Save the data to the database for the logged-in user
            fitness_data = FitnessData(
                user=request.user,  # Assuming the user is logged in
                height=height,
                weight=weight,
                bmi=bmi,
                step_count=step_count,
                calculated_distance=calculated_distance,
                sleep_duration=sleep_duration,
                stress_level=stress_level,
                hydration_level=hydration_level,
                activity_level=activity_level,
                bmr=bmr,
                tdee=tdee,
                status=status,
                message=message
            )
            fitness_data.save()  # Save to the database

            # Render the result page after saving
            return render(request, 'users/fitness_result.html', {
                'form': form,
                'message': message,
                'status': status,
                'bmi': bmi,
                'calculated_distance': calculated_distance,
                'bmr': bmr,
                'tdee': tdee
            })
    else:
        form = FitnessForm()

    # If the method is GET, display the form
    return render(request, 'users/fitness_form.html', {'form': form})
from django.shortcuts import render
from .models import FitnessData

# def fitness_history(request):
#     # Get the logged-in user
#     user = request.user
    
#     # Fetch the historical fitness data for the logged-in user
#     fitness_data = FitnessData.objects.filter(user=user).order_by('-id')  # Most recent first
    
#     # Render the results to a template
#     return render(request, 'users/fitness_history.html', {'fitness_data': fitness_data})
from django.http import JsonResponse
from django.shortcuts import render
from .models import FitnessData  # Replace with your actual model name
from django.core.serializers.json import DjangoJSONEncoder
import json

def fitness_history(request):
    # Fetch fitness data for the current logged-in user only
    fitness_data = FitnessData.objects.filter(user=request.user).order_by('created_at')  # Adjust query as needed

    # Serialize data into JSON
    fitness_data_list = [
        {
            "created_at": data.created_at.strftime("%Y-%m-%d"),  # Format datetime for JSON
            "bmi": data.bmi,
            "step_count": data.step_count,
            "calculated_distance": data.calculated_distance,
            "sleep_duration": data.sleep_duration,
            "stress_level": data.stress_level,
            "hydration_level": data.hydration_level,
            "activity_level": data.activity_level,
            "bmr": data.bmr,
            "tdee": data.tdee,
            "status": data.status,
        }
        for data in fitness_data
    ]

    # Pass serialized data to template
    context = {
        "fitness_data_json": json.dumps(fitness_data_list, cls=DjangoJSONEncoder),
    }
    return render(request, "users/fitness_history.html", context)



