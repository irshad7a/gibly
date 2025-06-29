from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile, Post
from .models import Comment

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, help_text='Required. Enter a valid email address.')
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
        
class PostForm(forms.ModelForm):
    class Meta:
        model= Post
        fields = ('image', 'caption')
        
class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields= ('content',)
        exclude = []
        widgets = {
            'content': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Add your comment here...'}),
        }
        
class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('bio', 'profile_picture')
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Tell us about yourself...'}),
            'profile_picture': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
        } 
    
class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, help_text='Required. Enter a valid email address.')
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
        
    widgets = {
        'username': forms.TextInput(attrs={'placeholder': 'Enter username'}),
        'email': forms.EmailInput(attrs={'placeholder': 'Enter email'}),
        'password1': forms.PasswordInput(attrs={'placeholder': 'Enter password'}),
        'password2': forms.PasswordInput(attrs={'placeholder': 'Confirm password'}),
    }