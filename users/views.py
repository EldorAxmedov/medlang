from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView

from .repositories import UserRepository
from .services import UserService
from .serializers import UserCreateSerializer, UserSerializer
from .permissions import IsAdminOrSelf
from .models import User


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action in ['create', 'login']:
            return [AllowAny()]
        if self.action in ['retrieve', 'update', 'partial_update', 'destroy']:
            return [IsAdminOrSelf()]
        return [IsAdminOrSelf()]

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer

    def get_service(self):
        repo = UserRepository(User)
        return UserService(repo)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        service = self.get_service()
        user = service.register(**serializer.validated_data)
        out = UserSerializer(user)
        return Response(out.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def login(self, request):
        # For token issuance, delegate to SimpleJWT view
        return TokenObtainPairView.as_view()(request._request)
