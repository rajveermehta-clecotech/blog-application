from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, OTPVerification, Tag, Blog
from .utils import generate_otp, send_otp_email
from django.utils import timezone
from datetime import timedelta

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(
        required=True, 
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    name = forms.CharField(
        max_length=255, 
        required=True, 
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = CustomUser
        fields = ['email', 'name', 'password1', 'password2']
        widgets = {
            'password1': forms.PasswordInput(attrs={'class': 'form-control'}),
            'password2': forms.PasswordInput(attrs={'class': 'form-control'}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.name = self.cleaned_data['name']
        user.is_active = False  # User is not active until email is verified
        
        if commit:
            user.save()
        return user

class OTPVerificationForm(forms.Form):
    otp = forms.CharField(
        max_length=6, 
        min_length=6, 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter 6-digit OTP'})
    )

    def validate_otp(self, email, otp):
        """
        Validate the OTP for the given email
        """
        try:
            verification = OTPVerification.objects.get(
                email=email, 
                otp=otp, 
                is_verified=False
            )
            
            # Check if OTP is expired
            if verification.is_expired():
                verification.delete()
                return False
            
            # Mark OTP as verified
            verification.is_verified = True
            verification.save()
            return True
        
        except OTPVerification.DoesNotExist:
            return False

class BlogForm(forms.ModelForm):
    title = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    content = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 5})
    )
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = Blog
        fields = ['title', 'content', 'tags']