from rest_framework import status
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from apps.shop.models import Product, Cart, Order
from apps.shop.api.serializers import (
    ProductSerializer,
    AddToCartSerializer,
    CartSerializer,
    OrderSerializer,
    UpdateCartItemSerializer
)
from apps.shop.services.order_service import create_order_from_cart
from apps.shop.services.cart_service import add_product_to_cart, update_cart_item_quantity, delete_cart_item
from apps.shop.domain.exceptions import ShopDomainException
from apps.shop.api.error_handlers import domain_exception_response


# Create your views here.
class ProductListView(ListAPIView):
    """
    Endpoint для получения списка товаров.
    Возвращает только активные товары.
    Поддерживает фильтрацию по категории и поиск по названию.
    """
    serializer_class = ProductSerializer
    def get_queryset(self):
        queryset = Product.objects.filter(is_active=True).order_by('id')
        search = self.request.query_params.get('search', None)
        category = self.request.query_params.get('category', None)
        if search:
            queryset = queryset.filter(name__icontains=search)
        if category:
            queryset = queryset.filter(category__slug=category)
        return queryset

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
    permission_classes = [IsAuthenticated]
    def post(self, request):
        """
        Обрабатывает POST-запрос добавления товара в корзину.
        Ожидает id товара и количество.
        """
        serializer = AddToCartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            add_product_to_cart(
                user=request.user,
                product_id=serializer.validated_data['product_id'],
                quantity=serializer.validated_data['quantity']
            )
        except ShopDomainException as error:
            return domain_exception_response(error)

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


class CreateOrderView(APIView):
    """
    Endpoint для создания заказа из корзины.
    HTTP-слой только принимает запрос и вызывает сервис.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Обрабатывает POST-запрос создания заказа из корзины.
        """
        try:
            result = create_order_from_cart(request.user)
        except ShopDomainException as error:
            return domain_exception_response(error)

        return Response(
            {'message': 'Заказ создан.', 'order_id': result.id},
            status=status.HTTP_201_CREATED
        )


class OrderListView(ListAPIView):
    """
    Endpoint для получения списка заказов текущего пользователя.
    """
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by('-created_at')


class OrderDetailView(RetrieveAPIView):
    """
    Endpoint для получения одного заказа по id.
    Юзер может получить только свой заказ.
    """
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)


class CartItemDetailView(APIView):
    """
    Endpoint изменения и удаления позиции корзины.
    """
    permission_classes = [IsAuthenticated]
    def patch(self, request, pk):
        serializer = UpdateCartItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            cart_item = update_cart_item_quantity(
                user=request.user,
                cart_item_id=pk,
                quantity=serializer.validated_data['quantity'],
            )
        except ShopDomainException as error:
            return domain_exception_response(error)
        return Response({
            'message': 'Количество обновлено.',
            'quantity': cart_item.quantity,
        })

    def delete(self, request, pk):
        try:
            delete_cart_item(
                user=request.user,
                cart_item_id=pk,
            )
        except ShopDomainException as error:
            return domain_exception_response(error)
        return Response({
            'message': 'Товар удалён из корзины.'
        })