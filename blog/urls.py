from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.signup, name='signup'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('resend-otp/', views.resend_otp, name='resend_otp'),    
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('create/', views.create_blog, name='create_blog'),
    path('update/<int:blog_id>/', views.update_blog, name='update_blog'),
    path('delete/<int:blog_id>/', views.delete_blog, name='delete_blog'),
    path('blog/<int:blog_id>/', views.blog_details, name="blog_details"),
    path('tag/search/', views.tag_search, name='tag_search' ),
]
