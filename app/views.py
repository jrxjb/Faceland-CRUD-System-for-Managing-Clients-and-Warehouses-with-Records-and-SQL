from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework import viewsets, status,mixins
from rest_framework.response import Response
from utils.views import BaseView
from .models import Client, Warehouse,RecordsModel
from .serializers import ( ClientSerializer, WarehouseSerializer,LoginRequestSerializer,LoginResponseSerializer,
RegisterRequestSerializer,RegisterResponseSerializer, RecordsSerializer)
from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema, OpenApiExample

CustomUser = get_user_model()

###login

class LoginView(TokenObtainPairView, BaseView):
    serializer_class = LoginRequestSerializer

    def post(self, request, *args, **kwargs):
        request_serializer = self.serializer_class(data=request.data)
        if not request_serializer.is_valid():
            return self.error_response(request_serializer.errors)
        try:
            user = CustomUser.objects.get(username=request.data['username'])
            if user.is_superuser or (user.is_active and hasattr(user, 'client') and user.client.is_active):
                token_serializer = TokenObtainPairSerializer(data=request.data)
                token_serializer.is_valid(raise_exception=True)
            else:
                return self.error_response("This account is inactive.", status_code=status.HTTP_403_FORBIDDEN)
        except CustomUser.DoesNotExist:
            return self.error_response("Invalid credentials.", status_code=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return self.error_response(str(e))

        response_data = {
            'access': token_serializer.validated_data['access'],
            'refresh': token_serializer.validated_data['refresh'],
            'user_id': str(user.id),
            'username': user.username
        }
        response_serializer = LoginResponseSerializer(data=response_data)
        if response_serializer.is_valid():
            return Response(response_serializer.data, status=status.HTTP_200_OK)
        else:
            return self.error_response(response_serializer.errors)

### logout

class LogoutView(BaseView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return self.error_response(str(e))


#### Client
@extend_schema(tags=['Clients'])
class ClientViewSet(BaseView, mixins.RetrieveModelMixin, mixins.UpdateModelMixin,
                    mixins.ListModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet):
    queryset = Client.objects.all() 
    serializer_class = ClientSerializer
    authentication_classes = [JWTAuthentication]

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Client.objects.filter(is_active=True, user__is_active=True)
        return Client.objects.filter(user=user, is_active=True, user__is_active=True)

    @extend_schema(
        request=ClientSerializer,
        examples=[
            OpenApiExample(
                'Example de PUT',
                value={
                    "user": {
                        "username": "new_username",
                        "password": "new_password"
                    }
                },
                request_only=True,
                response_only=False,
            )
        ],
    )
    def update(self, request, *args, **kwargs):
        try:
            return super().update(request, *args, **kwargs)
        except Exception as e:
            return self.error_response(str(e)) 

    @extend_schema(
        request=ClientSerializer,
        examples=[
            OpenApiExample(
                'Example PATCH',
                value={
                    "user": {
                        "username": "new_username"
                    }
                },
                request_only=True,
                response_only=False,
            )
        ],
    )
    def partial_update(self, request, *args, **kwargs):
        try:
            return super().partial_update(request, *args, **kwargs)
        except Exception as e:
            return self.error_response(str(e))

    def perform_update(self, serializer):
        if self.request.user.is_staff:
            try:
                user_data = self.request.data.get('user')
                if user_data and isinstance(user_data, dict):
                    user_instance = self.get_object().user
                    if 'username' in user_data and user_instance.username != user_data['username']:
                        if CustomUser.objects.filter(username=user_data['username']).exclude(id=user_instance.id).exists():
                            return self.error_response({"user": {"username": "A user with that username already exists."}})
                        user_instance.username = user_data['username']
                    if 'password' in user_data:
                        user_instance.set_password(user_data['password'])
                    user_instance.save()
                serializer.save(user=user_instance)
            except Exception as e:
                return self.error_response(str(e))
        else:
                return self.error_response("You do not have permission to update this client.", status_code=status.HTTP_403_FORBIDDEN)

    def destroy(self, request, *args, **kwargs):
        if self.request.user.is_staff:
            try:
                instance = self.get_object()
                if instance.is_active:
                    refresh_token = request.data.get("refresh")
                    if refresh_token:
                        token = RefreshToken(refresh_token)
                        token.blacklist()
                    instance.is_active = False
                    instance.save()
                    return Response(status=status.HTTP_204_NO_CONTENT)
                else:
                    return self.error_response("The client is already inactive.", status_code=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return self.error_response(str(e))
        else:
            return self.error_response("You do not have permission to delete this client.", status_code=status.HTTP_403_FORBIDDEN)

### Register (client)

class RegisterUserView(BaseView, viewsets.ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = RegisterRequestSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUser]

    def perform_create(self, serializer):
        try:
            client = serializer.save()
        except Exception as e:
            return self.error_response(str(e))
        response_serializer = RegisterResponseSerializer(client)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

### Warehouse
@extend_schema(tags=['Warehouse'])
class WarehouseViewSet(BaseView, viewsets.ModelViewSet):
    queryset = Warehouse.objects.all()
    serializer_class = WarehouseSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Warehouse.objects.filter(is_active=True) 
        return Warehouse.objects.filter(client__user=user, is_active=True)
    
    @extend_schema(
        request=WarehouseSerializer,
        examples=[
            OpenApiExample(
                'Example de Warehouse',
                value={
                    "name": "name",
                    "address": "Direction",
                    "id_client": "3fa85f64-5717-4562-b3fc-2c963f66afa6"
                },
                request_only=True,
                response_only=False,
            ),
        ],
    )

    def create(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return self.error_response("You do not have permission to create a warehouse.", status_code=status.HTTP_403_FORBIDDEN)
        
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            return self.perform_create(serializer)

        return self.error_response(serializer.errors)


    def perform_create(self, serializer):
        id_client = self.request.data.get('id_client')
        try:
            client = Client.objects.get(user__id=id_client)
            if not client.is_active:  
              return self.error_response("Client not found.", status_code=status.HTTP_404_NOT_FOUND)
            serializer.save(client=client)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        except Client.DoesNotExist:
            return self.error_response("Client not found.", status_code=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return self.error_response(str(e))

    @extend_schema(
    request=WarehouseSerializer,
    examples=[
        OpenApiExample(
            'Example ',
            value={
                "id_warehouse": "your-warehouse-id",
                "name": "new-name",
                "address": "new-address",
                "id_client":"your-client-id"
            },
            request_only=True,
            response_only=False,
        )
    ],
)
    def update(self, request, *args, **kwargs):
        warehouse_id = self.request.data.get('id_warehouse')
        if not request.user.is_staff:
            return self.error_response("You do not have permission to update this warehouse.", status_code=status.HTTP_403_FORBIDDEN)
        if not warehouse_id:
            return self.error_response("Warehouse ID is required.", status_code=status.HTTP_400_BAD_REQUEST)
        if len(warehouse_id) != 36:
            return self.error_response("Invalid Warehouse ID.", status_code=status.HTTP_400_BAD_REQUEST)
        try:
            warehouse = Warehouse.objects.get(id=warehouse_id)
        except Warehouse.DoesNotExist:
            return self.error_response("Warehouse not found.", status_code=status.HTTP_404_NOT_FOUND)
        if not warehouse.is_active:
            return self.error_response("Warehouse is inactive.", status_code=status.HTTP_403_FORBIDDEN)
        serializer = self.get_serializer(instance=warehouse, data=request.data)  
        if serializer.is_valid():
            return self.perform_update(serializer)
        return self.error_response(serializer.errors)

    def perform_update(self, serializer):
        if self.request.user.is_staff:
            try:
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Exception as e:
                return self.error_response(str(e))
        else:
            return self.error_response("You do not have permission to update this warehouse.", status_code=status.HTTP_403_FORBIDDEN)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if self.request.user.is_staff and instance.is_active: 
            try:
                instance.is_active = False
                instance.save()
                return Response(status=status.HTTP_204_NO_CONTENT)
            except Exception as e:
                return self.error_response(str(e))
        else:
            return self.error_response("You do not have permission to delete this warehouse or the warehouse is inactive.", status_code=status.HTTP_403_FORBIDDEN)

### Records

@extend_schema(
        request=RecordsSerializer,
        examples=[
            OpenApiExample(
                'Example IN',
                value={
                    "id_warehouse":"3fa85f64-5717-4562-b3fc-2c963f66afa6",
                    "type_record":"IN" ,
                    "quantity" : 100
                },
            request_only=True,
            response_only=False,
            ),
            OpenApiExample(
                'Example OUT',
                value={
                    "id_warehouse":"3fa85f64-5717-4562-b3fc-2c963f66afa6",
                    "type_record":"OUT" , 
                    "quantity" : 100
                },
            request_only=True,
            response_only=False,
            )
        ]

)
@extend_schema(tags=['Records'])
class RecordsViewSet(BaseView, viewsets.ModelViewSet):
    queryset = RecordsModel.objects.filter(is_active=True)
    serializer_class = RecordsSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return RecordsModel.objects.filter(is_active=True)
        return RecordsModel.objects.filter(warehouse__client__user=user, is_active=True, warehouse__is_active=True)

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        warehouse_id = self.request.data.get('id_warehouse')
        
        try:
            warehouse = Warehouse.objects.get(id=warehouse_id)
        except Warehouse.DoesNotExist:
            return self.error_response("Warehouse not found.", status_code=status.HTTP_404_NOT_FOUND)
        
        if not warehouse.is_active:
            return self.error_response("Warehouse is inactive.", status_code=status.HTTP_403_FORBIDDEN)
        
        try:
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return self.error_response(str(e))

    def perform_update(self, serializer):
        record = self.get_object()
        if record.warehouse.is_active:
            try:
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Exception as e:
                return self.error_response(str(e))
        else:
            return self.error_response("Warehouse not found or inactive.", status_code=status.HTTP_403_FORBIDDEN)

    def destroy(self, request, *args, **kwargs):
        record = self.get_object()
        if self.request.user.is_staff and record.is_active:  
            try:  
               record.is_active = False
               record.save()
               return Response(status=status.HTTP_204_NO_CONTENT)
            except Exception as e:
                return self.error_response(str(e)) 
        else:
            return self.error_response("You do not have permission to delete this record or the record is inactive.", status_code=status.HTTP_403_FORBIDDEN)


            