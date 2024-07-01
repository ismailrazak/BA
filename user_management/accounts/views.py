from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm
from .models import CustomUser

def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/signup.html', {'form': form})

@login_required
def dashboard(request):
    if request.user.user_type == 'patient':
        return render(request, 'accounts/patient_dashboard.html', {'user': request.user})
    elif request.user.user_type == 'doctor':
        return render(request, 'accounts/doctor_dashboard.html', {'user': request.user})
