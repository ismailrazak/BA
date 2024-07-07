from django.shortcuts import render, redirect,get_object_or_404,reverse
from django.contrib.auth import login, authenticate
from .forms import UserSignupForm,BlogPostForm
from .models import Patient, Doctor, Profile
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from .forms import UserLoginForm
from django.contrib.auth.decorators import login_required
from .models import BlogPost,Category
def login_view(request):
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user.is_patient:
                    login(request, user)
                    return redirect('accounts:blog_posts_by_category')  # Redirect to blog posts page after login
            else:
                login(request, user)
                return redirect('accounts:create_blog_post')
    else:
        form = UserLoginForm()

    return render(request, 'login.html', {'form': form})



def dashboard(request):
    if request.user.is_patient:
        profile = Profile.objects.get(user=request.user)
        return redirect('accounts:blog_posts_by_category id')
    elif request.user.is_doctor:
        profile = Profile.objects.get(user=request.user)
        return redirect('accounts:create_blog_post')
    return redirect('login')

def signup(request):
    if request.method == "POST":
        form = UserSignupForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            if user.is_patient:
                Patient.objects.create(user=user)
            elif user.is_doctor:
                Doctor.objects.create(user=user)
            Profile.objects.create(
                user=user,
                profile_picture=form.cleaned_data.get('profile_picture'),
                address_line1=form.cleaned_data.get('address_line1'),
                city=form.cleaned_data.get('city'),
                state=form.cleaned_data.get('state'),
                pincode=form.cleaned_data.get('pincode')
            )
            login(request, user)
            return redirect('accounts:my_blog_posts')
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