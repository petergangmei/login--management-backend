from django.shortcuts import render
from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import authenticate
from django.db.models import Count
from .models import UserSession, UserSubscription
from .serializers import UserSessionSerializer
from rest_framework_simplejwt.tokens import RefreshToken

def home(request):
    return render(request, 'home.html')

@api_view(['POST'])
@permission_classes([AllowAny])
def login_user(request):
    username = request.data.get('username')
    password = request.data.get('password')
    device_info = request.data.get('device_info', 'Unknown Device')
    
    if not username or not password:
        return Response({
            'error': 'Please provide both username and password'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    user = authenticate(username=username, password=password)
    
    if not user:
        return Response({
            'error': 'Invalid credentials'
        }, status=status.HTTP_401_UNAUTHORIZED)
    
    # Check subscription and device limits
    try:
        subscription = user.subscription
        if not subscription.active:
            return Response({
                'error': 'Your subscription is not active'
            }, status=status.HTTP_403_FORBIDDEN)
        
        active_sessions = UserSession.objects.filter(
            user=user,
            is_active=True
        ).count()
        
        if active_sessions >= subscription.plan.max_devices:
            # Get current active sessions
            sessions = UserSession.objects.filter(
                user=user,
                is_active=True
            ).order_by('-last_activity')
            return Response({
                'error': 'Maximum device limit reached',
                'active_sessions': UserSessionSerializer(sessions, many=True).data
            }, status=status.HTTP_403_FORBIDDEN)
            
    except UserSubscription.DoesNotExist:
        return Response({
            'error': 'No active subscription found'
        }, status=status.HTTP_403_FORBIDDEN)
    
    # Generate JWT tokens
    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)
    
    # Create session
    session = UserSession.objects.create(
        user=user,
        token=access_token,
        device_info=device_info,
        ip_address=request.META.get('REMOTE_ADDR')
    )
    
    return Response({
        'access': access_token,
        'refresh': str(refresh),
        'session_id': session.id,
        'user_id': user.id,
        'username': user.username
    })

@api_view(['POST'])
@permission_classes([AllowAny])
def refresh_token(request):
    refresh_token = request.data.get('refresh')
    if not refresh_token:
        return Response({
            'error': 'Please provide refresh token'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        refresh = RefreshToken(refresh_token)
        access_token = str(refresh.access_token)
        
        return Response({
            'access': access_token,
        })
    except Exception as e:
        return Response({
            'error': 'Invalid refresh token'
        }, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_active_sessions(request):
    sessions = UserSession.objects.filter(
        user=request.user,
        is_active=True
    ).order_by('-last_activity')
    
    return Response({
        'sessions': UserSessionSerializer(sessions, many=True).data
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_session(request):
    session_id = request.data.get('session_id')
    
    if not session_id:
        return Response({
            'error': 'Please provide session_id'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Convert session_id to integer
        session_id = int(session_id)
    except (TypeError, ValueError):
        return Response({
            'error': 'Invalid session_id. Must be a number.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        session = UserSession.objects.get(
            id=session_id,
            user=request.user,
            is_active=True
        )
        session.is_active = False
        session.save()
        
        return Response({'message': 'Session terminated successfully'})
    
    except UserSession.DoesNotExist:
        return Response({
            'error': 'Session not found'
        }, status=status.HTTP_404_NOT_FOUND)
