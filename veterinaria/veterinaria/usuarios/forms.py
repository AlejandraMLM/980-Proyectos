from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from .models import Usuario
import re

class RegistroForm(UserCreationForm):
    # NUEVO: Campos de nombre y apellido
    first_name = forms.CharField(
        max_length=150,
        required=True,
        label="Nombre",
        widget=forms.TextInput(attrs={'class': 'form-control form-control-lg'})
    )
    
    last_name = forms.CharField(
        max_length=150,
        required=True,
        label="Apellido",
        widget=forms.TextInput(attrs={'class': 'form-control form-control-lg'})
    )
    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control form-control-lg'})
    )
    
    telefono = forms.CharField(
        max_length=8,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control form-control-lg'})
    )
    
    class Meta:
        model = Usuario    
        fields = ['first_name', 'last_name', 'username', 'email', 'telefono', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control form-control-lg'}),
        }
    
    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')
        
        if password1:
            # Validar mayúscula
            if not re.search(r'[A-Z]', password1):
                raise ValidationError('La contraseña debe contener al menos una letra mayúscula.')
            
            # Validar dígito 
            if not re.search(r'\d', password1):
                raise ValidationError('La contraseña debe contener al menos un dígito.')
            
            # Validar símbolo 
            if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password1):
                raise ValidationError('La contraseña debe contener al menos un símbolo (!@#$%^&* etc.).')
        
        return password1

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        if Usuario.objects.filter(email__iexact=email).exists():
            raise ValidationError('Ya existe una cuenta con este correo.')
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email'].strip().lower()
        if commit:
            user.save()
        return user