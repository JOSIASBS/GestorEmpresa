import re

from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'phone', 'address', 'photo', 'role', 'position']
        read_only_fields = ['id']

        def validate_phone(self, value):
            if value:  # si hay un valor
                pattern = r'^\+?\d{9,15}$'
                if not re.match(pattern, value):
                    raise serializers.ValidationError(
                        "Número de teléfono inválido. Debe tener entre 9 y 15 dígitos y opcionalmente comenzar con +"
                    )
            return value



        def validate_email(self, value):
            if value:  # si hay un valor
                if '@' not in value or '.' not in value.split('@')[-1]:
                    raise serializers.ValidationError("Email inválido")
            return value