from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
app_name='accounts'
urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup, name='signup'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('create/', views.create_blog_post, name='create_blog_post'),
    path('my_posts/', views.my_blog_posts, name='my_blog_posts'),
    path('blog_posts/', views.blog_posts_by_category, name='blog_posts_by_category'),
]
