from django import forms
from .models import Cita

class CitaForm(forms.ModelForm):
    class Meta:
        model = Cita
        fields = ['fecha', 'notas']  # ← SOLO estos campos existen en tu modelo
        widgets = {
            'fecha': forms.DateTimeInput(attrs={
                'type': 'datetime-local',  # ← Usa datetime-local para fecha y hora juntas
                'class': 'form-control'
            }),
            'notas': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 3,
                'placeholder': 'Describe cualquier síntoma o información relevante...'
            }),
        }