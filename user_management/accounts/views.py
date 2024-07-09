from django.shortcuts import render, redirect,get_object_or_404,reverse
from django.contrib.auth import login, authenticate
from .forms import UserSignupForm,BlogPostForm
from .models import Patient, Doctor, Profile, User,Appointment
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from .forms import UserLoginForm,AppointmentForm
from django.contrib.auth.decorators import login_required
from .models import BlogPost,Category
from google.oauth2 import service_account
from googleapiclient.discovery import build
import datetime
import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

SCOPES = ['https://www.googleapis.com/auth/calendar']

def get_google_calendar_credentials():
    creds = None
    CLIENT_SECRET_FILE = r'C:\Users\ismail\user_managemnet\user_management\accounts\CREDENTIALS\client_secret.json'

    if os.path.exists(r'C:\Users\ismail\user_managemnet\user_management\accounts\CREDENTIALS\token.json'):
        creds = Credentials.from_authorized_user_file(r'C:\Users\ismail\user_managemnet\user_management\accounts\CREDENTIALS\token.json', SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
            creds = flow.run_local_server(port=0)

        with open(r'C:\Users\ismail\user_managemnet\user_management\accounts\CREDENTIALS\token.json', 'w') as token:
            token.write(creds.to_json())
    return creds
credentials=get_google_calendar_credentials()
service = build('calendar', 'v3', credentials=credentials)

def doctor_list(request):
    doctors = Doctor.objects.all()
    return render(request, 'doctor_list.html', {'doctors': doctors})

def book_appointment(request, doctor_id):
    doctor = get_object_or_404(Doctor, id=doctor_id)
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.doctor = doctor
            appointment.patient = request.user
            appointment.save()
            create_google_calendar_event(appointment)
            return redirect(reverse('accounts:appointment_confirmation',args=[appointment.id]))
    else:
        form = AppointmentForm()
    return render(request, 'book_appointment.html', {'form': form, 'doctor': doctor})

def appointment_confirmation(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    return render(request, 'appointment_confirmation.html', {'appointment': appointment})

def create_google_calendar_event(appointment):
    
        start_time = datetime.datetime.combine(appointment.date, appointment.start_time)
        end_time = start_time + datetime.timedelta(minutes=45)
        event = {
            'summary': f'Appointment scheduled with patient name: {appointment.patient.first_name}',
            'start': {
                'dateTime': start_time.isoformat(),
                'timeZone': 'IST',
            },
            'end': {
                'dateTime': end_time.isoformat(),
                'timeZone': 'IST',
            },
        }
        created_event=service.events().insert(calendarId='primary', body=event).execute()
        print(f'{created_event.get("htmlLink")}')
def login_view(request):
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user.is_patient:
                    login(request, user)
                    return redirect('accounts:doctor_list')  # Redirect to blog posts page after login
            else:
                login(request, user)
                return redirect('accounts:create_blog_post')
    else:
        form = UserLoginForm()

    return render(request, 'login.html', {'form': form})



def dashboard(request):
    if request.user.is_patient:
        patient_user = Profile.objects.get(user=request.user)
        doctor_user=User.objects.filter(is_doctor=True)
        return render(request,'patient_dashboard.html',context={'patient_user':patient_user,'doctor_user':doctor_user})
    elif request.user.is_doctor:
        profile = Profile.objects.get(user=request.user)
        return render(request,'doctor_dashboard,html',{'profile':profile})
    return redirect('login')

def signup(request):
    if request.method == "POST":
        form = UserSignupForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            if user.is_patient:
                Patient.objects.create(user=user)
            elif user.is_doctor:
                Doctor.objects.create(
                user=user,
                profile_picture=form.cleaned_data.get('profile_picture'),
                speciality=form.cleaned_data.get('speciality'),
                )
            login(request, user)
            return redirect('accounts:doctor_list')
    else:
        form = UserSignupForm()
    return render(request, 'signup.html', {'form': form})


def create_blog_post(request):
    category_id = None
    if request.method == 'POST':
        form = BlogPostForm(request.POST, request.FILES)
        if form.is_valid():
            category_id=form.cleaned_data['category'].id
            blog_post = form.save(commit=False)
            blog_post.author = request.user
            blog_post.save()

    else:
        form = BlogPostForm()

    return render(request, 'create_blog_post.html', {'category_id':category_id,'form': form})


def my_blog_posts(request):
    blog_posts = BlogPost.objects.filter(author=request.user)
    return render(request, 'my_blog_posts.html', {'blog_posts': blog_posts})

def blog_posts_by_category(request):
    if request.user.is_patient:
        categories = Category.objects.all()
        blog_posts = BlogPost.objects.filter(is_draft=False).select_related('category')
    else:
        categories = Category.objects.all()
        blog_posts = BlogPost.objects.all().select_related('category')

    # Organize blog posts by category
    category_dict = {category: [] for category in categories}
    for post in blog_posts:
        category_dict[post.category].append(post)

    context = {
        'category_dict': category_dict
    }

    return render(request, 'blog_posts_by_category.html', context)