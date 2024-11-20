from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.core.paginator import Paginator
from .models import Blog
from .forms import BlogForm, UserRegisterForm


def signup(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'blog/signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
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
            blog = form.save(commit=False)
            blog.author = request.user
            blog.save()
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

