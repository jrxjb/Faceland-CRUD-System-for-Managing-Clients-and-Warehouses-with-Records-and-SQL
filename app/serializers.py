from rest_framework import serializers
from .models import Client, Warehouse,RecordsModel
from django.contrib.auth import get_user_model

CustomUser = get_user_model()
 
### Login users
class LoginRequestSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=255)
    password = serializers.CharField(write_only=True)

class LoginResponseSerializer(serializers.Serializer):
    access = serializers.CharField()  
    refresh = serializers.CharField()
    user_id = serializers.UUIDField()
    username = serializers.CharField(max_length=255)


###Register user
class RegisterRequestSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=255)
    password = serializers.CharField(write_only=True)


    def validate_username(self, value):
        if CustomUser.objects.filter(username=value).exists():
            raise serializers.ValidationError("A user with that username already exists.")
        return value


    def create(self, validated_data):
        user_instance = CustomUser.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password']
        )
        client = Client.objects.create(user=user_instance)
        return client

class RegisterResponseSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Client
        fields = ['username']


###  Client
class ClientSerializer(serializers.ModelSerializer):
    id_client = serializers.UUIDField(source='user.id', read_only=True)
    warehouses = serializers.SerializerMethodField()
    username = serializers.CharField(source='user.username', read_only=True)
    is_active = serializers.BooleanField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)


    class Meta:
        model = Client
        fields = ['id_client', 'username', 'warehouses', 'is_active', 'created_at', 'updated_at']

    def get_warehouses(self, obj):
        warehouses = obj.warehouses.filter(is_active=True)
        return WarehouseSerializer(warehouses, many=True).data

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', None)
        if user_data and isinstance(user_data, dict):
            user = instance.user
            if 'username' in user_data and user.username != user_data['username']:
                if CustomUser.objects.filter(username=user_data['username']).exclude(id=user.id).exists():
                    raise serializers.ValidationError({"user": {"username": "A user with that username already exists."}})
                user.username = user_data['username']
            if 'password' in user_data:
                user.set_password(user_data['password'])
            user.save()
        return super().update(instance, validated_data)


### records 

class RecordsSerializer(serializers.ModelSerializer):
    id_record = serializers.UUIDField(read_only=True)
    id_warehouse = serializers.PrimaryKeyRelatedField(source='warehouse', queryset=Warehouse.objects.all())
    type_record = serializers.CharField(max_length=10)
    quantity = serializers.IntegerField()

    class Meta:
        model = RecordsModel
        fields = ['id_record', 'id_warehouse', 'type_record', 'quantity', 'created_at', 'updated_at', 'is_active']
    
    def update(self, instance, validated_data):
        if 'quantity' in validated_data:
            validated_data.pop('quantity')
            validated_data.pop('type_record')
        return super().update(instance, validated_data)


#### Warehouse

class WarehouseSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='client.user.username', read_only=True)
    id_client = serializers.UUIDField(source='client.id', required=True)
    id_warehouse = serializers.UUIDField(source='id', read_only=True)
    is_active = serializers.BooleanField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    records = serializers.SerializerMethodField()

    class Meta:
        model = Warehouse
        fields = ['id_warehouse', 'name', 'address', 'id_client', 'username', 'is_active', 'created_at', 'updated_at', 'records']

    def get_records(self, obj):
        if isinstance(obj, Warehouse):
            records = obj.records.filter(is_active=True)
            return RecordsSerializer(records, many=True).data
        return []

    def update(self, instance, validated_data):
        client_data = validated_data.pop('client', None)
        if client_data:
            user_data = client_data.get('user', None)
            if user_data:
                user_id = user_data.get('id')
                if user_id:
                    client = Client.objects.get(user__id=user_id)
                    instance.client = client
        instance.name = validated_data.get('name', instance.name)
        instance.address = validated_data.get('address', instance.address)
        instance.save()
        return instance
