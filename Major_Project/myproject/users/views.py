from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import JsonResponse
from django.core.serializers.json import DjangoJSONEncoder
from django.contrib.auth.decorators import login_required
from .forms import UserRegistrationForm, FitnessForm
from .models import FitnessData
import joblib
import json


# User Registration View
# Handles user registration using a custom form. 
# If the form is valid, the user is saved to the database and redirected to the login page.
def register(request):
    form = UserRegistrationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()  # Save the new user to the database
        return redirect('login')  # Redirect to login page after successful registration
    return render(request, 'users/register.html', {'form': form})  # Render the registration form


# User Login View
# Authenticates the user and redirects them to the fitness form page if successful.
# Displays an error message for invalid login attempts.
def login_user(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)  # Authenticate the user
        if user:
            login(request, user)  # Log the user in
            return redirect('fitness_form')  # Redirect to the fitness form page
        else:
            messages.error(request, "Invalid username or password.")  # Show error message
    return render(request, 'users/login.html')  # Render the login form


# User Logout View
# Logs out the current user and redirects to the home page.
def logout_user(request):
    logout(request)  # Log the user out
    return redirect('home')  # Redirect to the home page


# Home Page View
# Renders the home page of the application.
def home(request):
    return render(request, 'users/home.html')  # Render the home template


# Helper Function: Calculate BMR
# Calculates Basal Metabolic Rate (BMR) based on gender, weight, height, and age.
def calculate_bmr(gender, weight, height, age):
    if gender == "Male":
        return 10 * weight + 6.25 * height - 5 * age + 5
    return 10 * weight + 6.25 * height - 5 * age - 161


# Helper Function: Calculate TDEE
# Calculates Total Daily Energy Expenditure (TDEE) based on BMR and activity level.
def calculate_tdee(bmr, activity_level):
    activity_factors = {
        "Sedentary": 1.2,
        "Lightly Active": 1.375,
        "Moderately Active": 1.55,
        "Very Active": 1.725,
        "Super Active": 1.9
    }
    return bmr * activity_factors.get(activity_level, 1.2)


# Helper Function: Calculate Distance from Steps
# Converts the number of steps to the distance covered in meters.
def calculate_distance_from_steps(step_count):
    stride_length = 0.762  # Average stride length in meters
    return step_count * stride_length


# Fitness Form View
# Allows users to input their fitness data and receive a health status prediction.
# Saves the input and calculated fitness data to the database.
@login_required
def fitness_view(request):
    # Load pre-trained Random Forest model and scaler for input normalization
    model = joblib.load(r'models/Random_forest_Fitness_correct.pkl')
    scaler = joblib.load(r'models/Fitness_scaler_correct.pkl')

    if request.method == 'POST':
        form = FitnessForm(request.POST)  # Bind the form data
        if form.is_valid():
            # Extract and clean data from the form
            data = form.cleaned_data
            height, weight, step_count = data['height'], data['weight'], data['step_count']
            sleep_duration, hydration_level = data['sleep_duration'], data['hydration_level']
            activity_level, age, gender = data['activity_level'], data['age'], data['gender']
            stress_level = {'Low': 2, 'Medium': 1, 'High': 0}[data['stress_level']]  # Map stress level to numeric values

            # Calculate additional health metrics
            bmi = weight / (height / 100) ** 2  # Body Mass Index
            calculated_distance = calculate_distance_from_steps(step_count)  # Distance from steps
            bmr = calculate_bmr(gender, weight, height, age)  # Basal Metabolic Rate
            tdee = calculate_tdee(bmr, activity_level)  # Total Daily Energy Expenditure

            # Normalize input data and make prediction using the ML model
            input_data = scaler.transform([[height, weight, bmi, step_count, calculated_distance, sleep_duration, stress_level, hydration_level]])
            prediction = model.predict(input_data)

            # Determine fitness status and corresponding message
            status, message = ("Fit", "🎉 You are Healthy!") if prediction == 0 else ("Not Fit", "🛑 You may need to improve your health routine.")

            # Save the fitness data and prediction to the database
            FitnessData.objects.create(
                user=request.user, height=height, weight=weight, bmi=bmi, step_count=step_count,
                calculated_distance=calculated_distance, sleep_duration=sleep_duration,
                stress_level=stress_level, hydration_level=hydration_level, activity_level=activity_level,
                bmr=bmr, tdee=tdee, status=status, message=message
            )

            # Render the result page with calculated metrics and prediction
            return render(request, 'users/fitness_result.html', {
                'form': form, 'message': message, 'status': status, 'bmi': bmi,
                'calculated_distance': calculated_distance, 'bmr': bmr, 'tdee': tdee
            })
    else:
        form = FitnessForm()  # Render an empty form for GET requests

    return render(request, 'users/fitness_form.html', {'form': form})  # Render the fitness form


def fitness_history(request):
    # Fetch fitness data for the current logged-in user only
    fitness_data = FitnessData.objects.filter(user=request.user).order_by('created_at')  

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



