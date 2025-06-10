from django.shortcuts import render
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .models import User, UserProfile
from .serializers import UserSerializer, UserProfileSerializer, LoginSerializer

# Create your views here.

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.action in ['create', 'login', 'get_users_by_role']:
            return [permissions.AllowAny()]
        return super().get_permissions()

    @action(detail=False, methods=['post'])
    def login(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = authenticate(
                email=serializer.validated_data['email'],
                password=serializer.validated_data['password']
            )
            if user:
                refresh = RefreshToken.for_user(user)
                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                    'user': UserSerializer(user).data
                })
            return Response(
                {'error': 'Invalid credentials'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def me(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def logout(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], url_path='get_users_by_role')
    def get_users_by_role(self, request):
        """
        Lấy danh sách users theo role
        Query parameter: role (PATIENT, DOCTOR, NURSE, ADMIN, PHARMACIST, INSURANCE, LAB_TECHNICIAN)
        """
        role = request.query_params.get('role')
        
        if not role:
            return Response(
                {'error': 'Role parameter is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Kiểm tra role có hợp lệ không
        valid_roles = [choice[0] for choice in User.Role.choices]
        if role not in valid_roles:
            return Response(
                {
                    'error': f'Invalid role. Valid roles are: {", ".join(valid_roles)}'
                }, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Lọc users theo role
        users = User.objects.filter(role=role, is_active=True)
        serializer = UserSerializer(users, many=True)
        
        return Response({
            'role': role,
            'count': users.count(),
            'users': serializer.data
        })
