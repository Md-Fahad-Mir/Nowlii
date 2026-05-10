from .models import CustomUserModel, Profile, NowliiPredefinedOption
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from rest_framework import serializers


class NormalizedChoiceField(serializers.ChoiceField):
    def to_internal_value(self, data):
        if isinstance(data, str):
            data = data.replace('’', "'").strip()
        return super().to_internal_value(data)


class URLOrUploadedFileField(serializers.Field):
    def to_internal_value(self, data):
        if data is None or data == "":
            return None

        if hasattr(data, 'read'):
            filename = default_storage.save(
                f'profile_images/{data.name}',
                ContentFile(data.read())
            )
            try:
                return default_storage.url(filename)
            except Exception:
                return filename

        if isinstance(data, str):
            return data.strip() or None

        raise serializers.ValidationError('Invalid value for profile_image.')

    def to_representation(self, value):
        if not value:
            return None
            
        # Extract the string URL if it's an ImageFieldFile
        if hasattr(value, 'url'):
            try:
                value_str = value.url
            except ValueError:
                return None
        else:
            value_str = str(value)
        
        # If it's already a full URL, return as is
        if value_str.startswith(('http://', 'https://')):
            return value_str
        
        # Build full URL for relative paths
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(value_str)
        
        return value_str


# ------------------------------------------------------------------------------
# NOWLII PREDEFINED OPTIONS
# ------------------------------------------------------------------------------
class NowliiPredefinedOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = NowliiPredefinedOption
        fields = '__all__'
        extra_kwargs = {
            'name': {'help_text': "The unique name of the Nowlii character"},
            'avatar_logo': {'help_text': "The URL to the avatar image logo"}
        }


# ------------------------------------------------------------------------------
# PROFILE
# ------------------------------------------------------------------------------
class ProfileSerializer(serializers.ModelSerializer):
    profile_image = URLOrUploadedFileField(required=False, allow_null=True)
    gender = NormalizedChoiceField(choices=Profile.GENDER_CHOICES, required=False, allow_null=True, allow_blank=True)
    
    # Predefined option can be expanded or just ID
    predefined_option_detail = NowliiPredefinedOptionSerializer(source='predefined_option', read_only=True)

    class Meta:
        model = Profile
        fields = '__all__'
        read_only_fields = ['user', 'avatar_logo', 'nowlii_name']


# ------------------------------------------------------------------------------
# REGISTRATION
# ------------------------------------------------------------------------------
class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField(
        required=True,
        help_text="User's email address"
    )
    username = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=150,
        help_text="Optional username (if not provided, will be generated from email)"
    )
    password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'},
        help_text="User's password"
    )

    def validate_email(self, value):
        """Validate that email is not already registered"""
        User = get_user_model()
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("User with this email already exists.")
        return value


# ------------------------------------------------------------------------------
# VERIFY REGISTRATION OTP
# ------------------------------------------------------------------------------
class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField(
        required=True,
        help_text="Email address used during registration"
    )
    otp = serializers.CharField(
        required=True,
        max_length=6,
        min_length=6,
        help_text="6-digit OTP code sent to your email"
    )


# ------------------------------------------------------------------------------
# RESEND REGISTRATION OTP
# ------------------------------------------------------------------------------
class ResendOTPSerializer(serializers.Serializer):
    email = serializers.EmailField(
        required=True,
        help_text="Email address used during registration"
    )


# ------------------------------------------------------------------------------
# LOGIN
# ------------------------------------------------------------------------------
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(
        required=True,
        help_text="User's email address"
    )
    password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'},
        help_text="User's password"
    )


# ------------------------------------------------------------------------------
# LOGOUT
# ------------------------------------------------------------------------------
class LogoutSerializer(serializers.Serializer):
    refresh_token = serializers.CharField(
        required=True,
        help_text="JWT refresh token to blacklist"
    )


# ------------------------------------------------------------------------------
# FORGOT PASSWORD
# ------------------------------------------------------------------------------
class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(
        required=True,
        help_text="User's email address"
    )


# ------------------------------------------------------------------------------
# VERIFY FORGOT PASSWORD OTP
# ------------------------------------------------------------------------------
class VerifyForgotPasswordOTPSerializer(serializers.Serializer):
    email = serializers.EmailField(
        required=True,
        help_text="Email address used during forgot password request"
    )
    otp = serializers.CharField(
        required=True,
        max_length=6,
        min_length=6,
        help_text="6-digit OTP code sent to your email"
    )


# ------------------------------------------------------------------------------
# SET NEW PASSWORD (FORGOT PASSWORD)
# ------------------------------------------------------------------------------
class SetNewPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(
        required=True,
        help_text="User's email address"
    )
    new_password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'},
        help_text="New password for your account"
    )
    confirm_password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'},
        help_text="Confirm your new password"
    )

    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match."})
        return data


# ------------------------------------------------------------------------------
# RESET PASSWORD
# ------------------------------------------------------------------------------
class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(
        required=True,
        help_text="User's email address"
    )
    new_password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'},
        help_text="New password for your account"
    )
    confirm_password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'},
        help_text="Confirm your new password"
    )

    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match."})
        return data


