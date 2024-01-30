from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Product, User
from .serializers import ProductSerializer
import random
from .producer import publish
# Create your views here.


class ProductViewSet(viewsets.ViewSet):

    def list(self, request): #/api/products
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)

    def create(self, request): #/api/products
        serializer = ProductSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        publish('product_created', serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def retreive(self, request, pk=None): #/api/products/<str:pk>
        product = Product.objects.get(id=pk)
        serializer = ProductSerializer(product)
        
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, pk=None): #/api/products/<str:pk>
        product = Product.objects.get(id=pk)
        serializer = ProductSerializer(instance=product, data=request.data)

        serializer.is_valid()
        serializer.save()
        publish('product_updated', serializer.data)
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
    
    def destroy(self, request, pk=None): #/api/products/<str:pk>
        product = Product.objects.get(id=pk)
        product.delete()
        publish('product_deleted', pk)
        return Response(status=status.HTTP_204_NO_CONTENT)
    

class UserAPIView(APIView):

    def get(self, request, *args, **kwargs):
        users = User.objects.all()
        user = random.choice(users)

        return Response({
            'id': user.id
        })

  

  