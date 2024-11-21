from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.db.models import Q

from .models import Blog, Tag, CustomUser
from .forms import BlogForm, UserRegisterForm


User = get_user_model()


#-----------------------------------------------------------------------------------------


from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import login

from .models import CustomUser, OTPVerification
from .forms import UserRegisterForm, OTPVerificationForm
from .utils import generate_otp, send_otp_email
from django.contrib.auth import authenticate, login, logout  # Add logout to the import


def signup(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            # Check if email already exists
            email = form.cleaned_data['email']
            if CustomUser.objects.filter(email=email).exists():
                messages.error(request, 'Email already registered')
                return render(request, 'blog/signup.html', {'form': form})
            
            # Create user (but not activate)
            user = form.save()
            
            # Generate and send OTP
            otp = generate_otp()
            
            # Delete any existing OTP for this email
            OTPVerification.objects.filter(email=email).delete()
            
            # Create new OTP verification
            OTPVerification.objects.create(
                email=email,
                otp=otp,
                expires_at=timezone.now() + timedelta(minutes=10)
            )
            
            # Send OTP email
            if send_otp_email(email, otp):
                # Redirect to OTP verification page
                request.session['signup_email'] = email
                return redirect('verify_otp')
            else:
                # If email sending fails, delete the user
                user.delete()
                messages.error(request, 'Failed to send OTP. Please try again.')
    else:
        form = UserRegisterForm()
    
    return render(request, 'blog/signup.html', {'form': form})

def verify_otp(request):
    email = request.session.get('signup_email')
    
    if not email:
        return redirect('signup')
    
    if request.method == 'POST':
        form = OTPVerificationForm(request.POST)
        if form.is_valid():
            otp = request.POST.get('otp')
            
            # Validate OTP
            verification = OTPVerification.objects.filter(
                email=email, 
                otp=otp, 
                is_verified=False
            ).first()
            
            if verification and not verification.is_expired():
                # Activate user
                user = CustomUser.objects.get(email=email)
                user.is_active = True
                user.email_verified = True
                user.save()
                
                # Delete OTP verification
                verification.delete()
                
                # Log the user in
                login(request, user)
                
                # Clear session
                del request.session['signup_email']
                
                messages.success(request, 'Email verified successfully. You are now logged in.')
                return redirect('home')
            else:
                messages.error(request, 'Invalid or expired OTP')
    else:
        form = OTPVerificationForm()
    
    return render(request, 'blog/verify_otp.html', {'form': form, 'email': email})

def resend_otp(request):
    email = request.session.get('signup_email')
    
    if not email:
        return redirect('signup')
    
    # Delete existing OTP
    OTPVerification.objects.filter(email=email).delete()
    
    # Generate new OTP
    otp = generate_otp()
    
    # Create new OTP verification
    OTPVerification.objects.create(
        email=email,
        otp=otp,
        expires_at=timezone.now() + timedelta(minutes=10)
    )
    
    # Send new OTP
    if send_otp_email(email, otp):
        messages.success(request, 'New OTP sent to your email')
    else:
        messages.error(request, 'Failed to send OTP. Please try again.')
    
    return redirect('verify_otp')


# def signup(request):
#     if request.method == 'POST':
#         form = UserRegisterForm(request.POST)
#         if form.is_valid():
#             user = form.save(commit=False)
#             user.is_active = True  # Activate the user
#             user.save()
#             return redirect('login')
#     else:
#         form = UserRegisterForm()
#     return render(request, 'blog/signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        email = request.POST['email']  # Changed from username to email
        password = request.POST['password']
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            # Add error message for failed login
            return render(request, 'blog/login.html', {'error': 'Invalid login credentials'})
    return render(request, 'blog/login.html')

def logout_view(request):
    logout(request)
    return redirect('home')

def home(request):
    blogs = Blog.objects.all().order_by('-created_at')
    paginator = Paginator(blogs, 5)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'blog/home.html', {'page_obj': page_obj})

@login_required
def blog_details(request, blog_id):
    blog = get_object_or_404(Blog, id = blog_id)
    return render(request,'blog/blog_details.html',{'blog':blog})


@login_required
def create_blog(request):
    if request.method == 'POST':
        form = BlogForm(request.POST)
        if form.is_valid():
            print (form.cleaned_data)
            blog = form.save(commit=False)
            blog.author = request.user
            blog.save()
            form.save_m2m()
            return redirect('home')
    else:
        form = BlogForm()
    return render(request, 'blog/blog_form.html', {'form': form})

@login_required
def update_blog(request, blog_id):
    blog = get_object_or_404(Blog, id=blog_id, author=request.user)
    if request.method == 'POST':
        form = BlogForm(request.POST, instance=blog)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = BlogForm(instance=blog)
    return render(request, 'blog/blog_form.html', {'form': form})

@login_required
def delete_blog(request, blog_id):
    blog = get_object_or_404(Blog, id=blog_id, author=request.user)
    if request.method == 'POST':
        blog.delete()
        return redirect('home')
    return render(request, 'blog/delete_confirm.html', {'blog': blog})

def tag_search(request):
    if request.method == 'POST':
        search_input = request.POST.get('query')
        # tag = Tag.objects.get(name=search_input)
        # blogs = tag.blogs.all() 
        try:
            tag = Tag.objects.get(name=search_input)
            blogs = tag.blogs.all()
        except Tag.DoesNotExist:
            blogs = Blog.objects.filter(
                Q(title__icontains=search_input)   # Search title for the query
                # Q(content__icontains=search_input)  # Search content for the query
            )
    return render(request, 'blog/search_blogs.html', {"blogs":blogs})

