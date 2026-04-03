from rest_framework import status
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from .models import Product, Cart, CartItem
from .serializers import ProductSerializer, AddToCartSerializer, CartSerializer


# Create your views here.
class ProductListView(ListAPIView):
    """
    Endpoint для получения списка товаров.
    Возвращает только активные товары.
    """
    queryset = Product.objects.filter(is_active=True)
    serializer_class = ProductSerializer

class ProductDetailView(RetrieveAPIView):
    """
    Endpoint для получения одного товара по id.
    Возвращает товар, если он существует и активен, иначе - 404.
    """
    queryset = Product.objects.filter(is_active=True)
    serializer_class = ProductSerializer


class AddToCartView(APIView):
    """
    Endpoint для добавления товара в корзину пользователя.
    Если товар уже есть в корзине, увеличивает количество.
    Если нет, создает новую позицию.
    """
    def post(self, request):
        """
        Обрабатывает POST-запрос добавления товара в корзину.
        Ожидает id товара и количество.
        Логика:
        - валидирует входные данные
        - находит товар
        - получает или создает корзину
        - добавляет товар в корзину или увеличивает количество.
        """
        serializer = AddToCartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product_id = serializer.validated_data['product_id']
        quantity = serializer.validated_data['quantity']
        product = get_object_or_404(Product, id=product_id, is_active=True)
        if not request.user.is_authenticated:
            return Response({'error': 'Not authenticated'}, status=401)
        cart, created = Cart.objects.get_or_create(user=request.user)
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        if not created:
            cart_item.quantity += quantity
        else:
            cart_item.quantity = quantity
        cart_item.save()
        return Response({'message': 'Товар добавлен в корзину.'})


class CartView(APIView):
    """
    Endpoint для получения корзины юзера.
    Возвращает корзину и список товаров в ней.
    """
    permission_classes = [IsAuthenticated]
    def get(self, request):
        cart, created = Cart.objects.get_or_create(user=request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data)