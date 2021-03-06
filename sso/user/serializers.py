from django.contrib.auth import password_validation
from django.db import transaction
from rest_framework import serializers

from sso.user import utils
from sso.user.models import User, UserProfile
from sso.verification.models import VerificationCode


class VerificationCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = VerificationCode
        fields = (
            'code',
            'expiration_date',
        )


class LastLoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id',
            'last_login',
        )


class PasswordCheckSerializer(serializers.Serializer):
    password = serializers.CharField(style={'input_type': 'password'})
    session_key = serializers.CharField(style={'input_type': 'password'})


class CreateUserSerializer(serializers.ModelSerializer):
    verification_code = VerificationCodeSerializer(read_only=True)

    class Meta:
        model = User
        fields = (
            'email',
            'password',
            'verification_code',
        )
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def validate_password(self, value):
        password_validation.validate_password(value)
        return value

    @transaction.atomic
    def create(self, validated_data):
        instance = User.objects.create_user(**validated_data)
        VerificationCode.objects.create(user=instance)
        return instance


class UserProfileSerializer(serializers.ModelSerializer):
    profile_image = serializers.SerializerMethodField()
    social_account = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = (
            'first_name',
            'last_name',
            'job_title',
            'mobile_phone_number',
            'profile_image',
            'social_account',
        )

    def get_profile_image(self, obj):
        account = obj.user.socialaccount_set.first()
        if account:
            return utils.get_social_account_image(account)

    def get_social_account(self, obj):
        account = obj.user.socialaccount_set.first()
        return account.provider if account else 'email'

    def to_internal_value(self, data):
        return {**data, 'user_id': self.context['request'].user.pk}


class UserSerializer(serializers.ModelSerializer):

    user_profile = UserProfileSerializer()

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'hashed_uuid',
            'user_profile',
        )
