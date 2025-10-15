from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from .models import Usuario
import re

class RegistroForm(UserCreationForm):
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
        fields = ['username', 'email', 'telefono', 'password1', 'password2']
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