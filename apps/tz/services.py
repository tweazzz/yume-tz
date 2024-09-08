from datetime import datetime
from django.utils.timezone import make_aware, make_naive
from django.db.models import Sum, F
from .models import Product, OrderProduct

def rental_statistics(start_date_str, end_date_str):
    if not start_date_str or not end_date_str:
        return {"error": "Please provide both start_date and end_date."}, 400

    try:
        # Используем формат '%Y-%m-%d' для обработки дат без времени
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
    except ValueError:
        return {"error": "Invalid date format. Use YYYY-MM-DD format."}, 400

    # Приведение наивных datetime объектов к aware, если ваш проект использует timezone-aware datetime
    if not start_date.tzinfo:
        start_date = make_aware(start_date)
    if not end_date.tzinfo:
        end_date = make_aware(end_date)

    # Сумма аренды для каждого продукта
    rental_sums = (
        OrderProduct.objects.filter(
            order__start_date__gte=start_date,
            order__end_date__lte=end_date
        )
        .values(product_name=F('product__name'))
        .annotate(total_rental=Sum('price'))
    )

    # Получаем все продукты
    products = Product.objects.all()

    # Находим доступные интервалы для каждого продукта
    available_intervals = {}
    for product in products:
        # Все заказы для текущего продукта
        orders = OrderProduct.objects.filter(
            product=product,
            order__start_date__lt=end_date,
            order__end_date__gt=start_date
        ).order_by('order__start_date')

        intervals = []
        previous_end = start_date

        # Рассчитываем доступные интервалы
        for order in orders:
            order_start = order.order.start_date
            order_end = order.order.end_date

            if order_start > previous_end:
                intervals.append({
                    "start": previous_end.isoformat(),
                    "end": order_start.isoformat()
                })
            previous_end = order_end

        if previous_end < end_date:
            intervals.append({
                "start": previous_end.isoformat(),
                "end": end_date.isoformat()
            })

        available_intervals[product.name] = intervals

    # Формирование ответа
    response_data = {
        "rental_sums": list(rental_sums),
        "available_intervals": available_intervals
    }

    return response_data, 200
