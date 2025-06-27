from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import get_user_model
from apps.core_app.models import UserProfile, EmailVerification
from apps.core_app.services import EmailService
from .serializers import (
    UserSerializer, UserProfileSerializer, 
    LoginSerializer, TokenSerializer, RefreshTokenSerializer
)

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = UserSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Create user but mark as inactive until email verification
        user = serializer.save()
        user.is_active = False
        user.save()
        
        # Create email verification OTP
        verification = EmailVerification.create_verification(
            email=user.email,
            verification_type='signup',
            user=user
        )
        
        # Send OTP email
        success, message = EmailService.send_otp_email(
            email=user.email,
            otp_code=verification.otp_code,
            verification_type='signup'
        )
        
        if not success:
            # If email fails, delete the user and return error
            user.delete()
            return Response({
                'success': False,
                'error': f'Failed to send verification email: {message}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response({
            'success': True,
            'message': 'Registration initiated. Please check your email for verification code.',
            'email': user.email,
            'verification_required': True
        }, status=status.HTTP_201_CREATED)


class LoginView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'success': True,
                'user': UserSerializer(user).data,
                'tokens': {
                    'access': str(refresh.access_token),
                    'refresh': str(refresh),
                },
                'message': 'Login successful'
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'success': False,
                'error': 'Invalid credentials'
            }, status=status.HTTP_401_UNAUTHORIZED)


class LogoutView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        try:
            refresh_token = request.data.get('refresh_token')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            
            logout(request)
            return Response({
                'message': 'Logout successful'
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'error': 'Failed to logout'
            }, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserProfileSerializer
    
    def get_object(self):
        return UserProfile.objects.get_or_create(user=self.request.user)[0]


class RefreshTokenView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = RefreshTokenSerializer
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            refresh = RefreshToken(serializer.validated_data['refresh_token'])
            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'error': 'Invalid refresh token'
            }, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user(request):
    """Get current user information"""
    serializer = UserSerializer(request.user)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([AllowAny])
def verify_email(request):
    """Verify email using OTP code"""
    email = request.data.get('email')
    otp_code = request.data.get('otp_code')
    
    if not email or not otp_code:
        return Response({
            'success': False,
            'error': 'Email and OTP code are required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Find the most recent verification for this email
        verification = EmailVerification.objects.filter(
            email=email,
            verification_type='signup',
            is_verified=False
        ).order_by('-created_at').first()
        
        if not verification:
            return Response({
                'success': False,
                'error': 'No pending verification found for this email'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Verify the OTP
        success, message = verification.verify(otp_code)
        
        if success:
            # Activate the user account
            if verification.user:
                verification.user.is_active = True
                verification.user.save()
                
                # Send welcome email
                EmailService.send_welcome_email(verification.user)
                
                # Generate tokens for immediate login
                refresh = RefreshToken.for_user(verification.user)
                
                return Response({
                    'success': True,
                    'message': 'Email verified successfully! Welcome to SciTeX!',
                    'user': UserSerializer(verification.user).data,
                    'tokens': {
                        'access': str(refresh.access_token),
                        'refresh': str(refresh),
                    }
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'success': False,
                    'error': 'Associated user account not found'
                }, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({
                'success': False,
                'error': message
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        return Response({
            'success': False,
            'error': f'Verification failed: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def resend_otp(request):
    """Resend OTP code to email"""
    email = request.data.get('email')
    
    if not email:
        return Response({
            'success': False,
            'error': 'Email is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Find user by email
        user = User.objects.filter(email=email, is_active=False).first()
        
        if not user:
            return Response({
                'success': False,
                'error': 'No pending account found for this email'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Create new verification OTP
        verification = EmailVerification.create_verification(
            email=email,
            verification_type='signup',
            user=user
        )
        
        # Send OTP email
        success, message = EmailService.send_otp_email(
            email=email,
            otp_code=verification.otp_code,
            verification_type='signup'
        )
        
        if success:
            return Response({
                'success': True,
                'message': 'New verification code sent to your email'
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'success': False,
                'error': f'Failed to send email: {message}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    except Exception as e:
        return Response({
            'success': False,
            'error': f'Failed to resend OTP: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def delete_account(request):
    """Delete user account with 28-day grace period"""
    from datetime import timedelta
    from django.utils import timezone
    
    # Check if account is already scheduled for deletion
    user = request.user
    if hasattr(user, 'userprofile') and user.userprofile.deletion_scheduled_at:
        return Response({
            'success': False,
            'error': 'Account is already scheduled for deletion',
            'deletion_date': user.userprofile.deletion_scheduled_at + timedelta(days=28)
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Get or create user profile
        from apps.core_app.models import UserProfile
        profile, created = UserProfile.objects.get_or_create(user=user)
        
        # Schedule deletion for 28 days from now
        profile.deletion_scheduled_at = timezone.now()
        profile.save()
        
        # Send confirmation email
        deletion_date = profile.deletion_scheduled_at + timedelta(days=28)
        success, message = EmailService.send_deletion_confirmation_email(
            user=user,
            deletion_date=deletion_date
        )
        
        return Response({
            'success': True,
            'message': 'Account deletion scheduled. You have 28 days to cancel.',
            'deletion_date': deletion_date,
            'can_cancel': True
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'success': False,
            'error': f'Failed to schedule account deletion: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cancel_account_deletion(request):
    """Cancel scheduled account deletion"""
    user = request.user
    
    try:
        if not hasattr(user, 'userprofile') or not user.userprofile.deletion_scheduled_at:
            return Response({
                'success': False,
                'error': 'No account deletion is scheduled'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Cancel deletion
        user.userprofile.deletion_scheduled_at = None
        user.userprofile.save()
        
        return Response({
            'success': True,
            'message': 'Account deletion cancelled successfully'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'success': False,
            'error': f'Failed to cancel account deletion: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)