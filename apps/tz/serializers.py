from rest_framework import serializers
from .models import Order, Product, OrderProduct

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

class OrderProductSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())

    class Meta:
        model = OrderProduct
        fields = ['id', 'product', 'price', 'rental_duration']

class OrderSerializer(serializers.ModelSerializer):
    products = OrderProductSerializer(source='orderproduct_set', many=True)

    class Meta:
        model = Order
        fields = ['id', 'start_date', 'end_date', 'total_price', 'products']

    def create(self, validated_data):
        products_data = validated_data.pop('orderproduct_set')
        order = Order.objects.create(**validated_data)  # Создаем сам заказ

        # Создаем связанные объекты OrderProduct
        for product_data in products_data:
            product = product_data.pop('product')
            OrderProduct.objects.create(order=order, product=product, **product_data)

        return order
