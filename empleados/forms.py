from django import forms
from django.core.validators import RegexValidator
from .models import Solicitud
from empleados.models import Empleado, Evento

TIPO_CHOICES = (
    ('grupo', 'Grupo'),
    ('privado', 'Privado'),
)

class MessageForm(forms.Form):
    content = forms.CharField(widget=forms.Textarea(attrs={'rows':3, 'cols':40}), label='Mensaje')



class PerfilForm(forms.ModelForm):
    telefono = forms.CharField(
        required=False,
        validators=[RegexValidator(regex=r'^\+?\d{9,15}$',
                                   message="Número de teléfono inválido. Debe tener entre 9 y 15 dígitos.")],
        widget=forms.TextInput(attrs={'placeholder': '+34123456789'})
    )
    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={'placeholder': 'example@gmail.com'})
    )
    class Meta:
        model = Empleado
        fields = ['telefono', 'direccion', 'fecha_ingreso', 'foto']
        widgets = {
            'fecha_ingreso': forms.DateInput(attrs={'type': 'date'}),
        }

class EventoForm(forms.ModelForm):
    para_todos = forms.BooleanField(required=False, label="Asignar a todos los empleados")

    class Meta:
        model = Evento
        fields = ['titulo', 'descripcion', 'fecha_inicio', 'fecha_fin', 'tipo', 'asignados', 'para_todos']
        widgets = {
            'fecha_inicio': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'fecha_fin': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def __init__(self, *args, **kwargs):
        empleado = kwargs.pop('empleado', None)
        super().__init__(*args, **kwargs)
        self.empleado = empleado

        # No forzar fecha_fin en el form (dejamos que el save() la gestione)
        self.fields['fecha_fin'].required = False

        if empleado:
            if empleado.role == 'manager':
                if empleado.posicion and empleado.posicion.departamento:
                    self.fields['asignados'].queryset = Empleado.objects.filter(
                        posicion__departamento=empleado.posicion.departamento
                    )
            elif empleado.role == 'admin':
                self.fields['asignados'].queryset = Empleado.objects.all()
            else:
                self.fields['asignados'].queryset = Empleado.objects.none()
                self.fields['tipo'].widget = forms.HiddenInput()

    def save(self, commit=True):
        evento = super().save(commit=False)

        # 👇 lógica para la fecha fin automática
        if not evento.fecha_fin or evento.tipo.lower() == 'reunión':
            evento.fecha_fin = evento.fecha_inicio

        if commit:
            evento.save()

            # Si se marca "para todos", asignamos a todos los empleados
            if self.cleaned_data.get('para_todos'):
                todos = Empleado.objects.all()
                evento.asignados.set(todos)
            else:
                self.save_m2m()

        return evento

class CrearChatForm(forms.Form):
    tipo = forms.ChoiceField(choices=TIPO_CHOICES)
    nombre = forms.CharField(max_length=150, required=False)
    miembros = forms.ModelMultipleChoiceField(
        queryset=Empleado.objects.none(),
        widget=forms.CheckboxSelectMultiple
    )


class SolicitudForm(forms.ModelForm):
    class Meta:
        model = Solicitud
        fields = ['tipo', 'fecha_inicio', 'fecha_fin', 'motivo']
        widgets = {
            'fecha_inicio': forms.DateInput(attrs={'type': 'date'}),
            'fecha_fin': forms.DateInput(attrs={'type': 'date'}),
        }