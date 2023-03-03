from rest_framework import serializers

from authentication.models import User


class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

    #делаем хеширование пароля
    def create(self, validated_data):
        user = super().create(validated_data)

        user.set_password(user.password)
        user.save()

        return user