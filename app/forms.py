from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from app.models import Profile
from django.contrib.auth.hashers import check_password

class UserForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter Password'}),
        label="Password"
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm Password'}),
        label="Confirm Password"
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Username'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter Email'}),
        }
        labels = {
            'username': 'Username',
            'email': 'Email Address',
            'password': 'Password',
        }
        help_texts = {
            'username': '',  # Removes default Django help text
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            raise ValidationError("Passwords do not match. Please enter both fields correctly.")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])  # Hash password before saving
        if commit:
            user.save()
        return user


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['profile_pic', 'address']
        widgets = {
            'profile_pic': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        labels = {
            'profile_pic': 'Profile Picture',
            'address': 'Address',
        }


class ChangePasswordForm(forms.Form):
    old_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter Old Password'}),
        required=True,
        label="Old Password"
    )
    new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter New Password'}),
        min_length=8,
        max_length=20,
        required=True,
        label="New Password"
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm New Password'}),
        required=True,
        label="Confirm Password"
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)  # Get the user instance for password validation
        super(ChangePasswordForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        old_password = cleaned_data.get("old_password")
        new_password = cleaned_data.get("new_password")
        confirm_password = cleaned_data.get("confirm_password")

        # Validate old password against the database
        if self.user and not check_password(old_password, self.user.password):
            self.add_error("old_password", "Old password is incorrect.")

        if new_password and confirm_password and new_password != confirm_password:
            self.add_error("confirm_password", "New password and confirm password must match.")

        if new_password and not any(char.isalpha() for char in new_password):
            self.add_error("new_password", "Password must contain at least one letter.")

        if new_password and not any(char.isdigit() for char in new_password):
            self.add_error("new_password", "Password must contain at least one number.")

        if new_password and not any(char in "@$!%*?&" for char in new_password):
            self.add_error("new_password", "Password must contain at least one special character (@, $, !, %, *, ?, &).")

        return cleaned_data
