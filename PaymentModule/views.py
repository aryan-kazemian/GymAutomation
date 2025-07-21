from collections import defaultdict
import calendar
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

from django.db.models import Sum, Count, Q
from django.utils.timezone import now

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Payment
from .serializers import PaymentSerializer
from UserModule.models import GenMember


class PaymentSummaryAPIView(APIView):
    def get(self, request):
        today = now().date()
        current_year = today.year
        current_month = today.month

        payments = Payment.objects.filter(
            user__members__is_single_settion=True
        )

        total_agg = payments.aggregate(total_price=Sum('price'), total_count=Count('id'))
        total_price = total_agg['total_price'] or 0
        total_count = total_agg['total_count'] or 0

        year_payments = payments.filter(payment_date__year=current_year)
        year_agg = year_payments.aggregate(year_price=Sum('price'), year_count=Count('id'))
        year_price = year_agg['year_price'] or 0
        year_count = year_agg['year_count'] or 0

        month_payments = year_payments.filter(payment_date__month=current_month)
        month_agg = month_payments.aggregate(month_price=Sum('price'), month_count=Count('id'))
        month_price = month_agg['month_price'] or 0
        month_count = month_agg['month_count'] or 0

        today_payments = month_payments.filter(payment_date__date=today)
        today_agg = today_payments.aggregate(today_price=Sum('price'), today_count=Count('id'))
        today_price = today_agg['today_price'] or 0
        today_count = today_agg['today_count'] or 0

        daily_prices = defaultdict(lambda: {'total_price': 0, 'count': 0})
        days_in_month = calendar.monthrange(current_year, current_month)[1]
        for day in range(1, days_in_month + 1):
            date_str = f"{current_year}-{current_month:02d}-{day:02d}"
            daily_prices[date_str] = {'total_price': 0, 'count': 0}

        daily_agg = month_payments.values('payment_date__date').annotate(
            total_price=Sum('price'),
            count=Count('id')
        )

        for item in daily_agg:
            date_key = item['payment_date__date'].strftime('%Y-%m-%d')
            daily_prices[date_key] = {
                'total_price': item['total_price'] or 0,
                'count': item['count'] or 0
            }

        monthly_prices = defaultdict(lambda: {'total_price': 0, 'count': 0})
        for month in range(1, 13):
            month_key = f"{current_year}-{month:02d}"
            monthly_prices[month_key] = {'total_price': 0, 'count': 0}

        monthly_agg = year_payments.values('payment_date__month').annotate(
            total_price=Sum('price'),
            count=Count('id')
        )

        for item in monthly_agg:
            month_key = f"{current_year}-{item['payment_date__month']:02d}"
            monthly_prices[month_key] = {
                'total_price': item['total_price'] or 0,
                'count': item['count'] or 0
            }

        return Response({
            'total_price': total_price,
            'total_count': total_count,
            'year_price': year_price,
            'year_count': year_count,
            'month_price': month_price,
            'month_count': month_count,
            'today_price': today_price,
            'today_count': today_count,
            'daily_prices': dict(daily_prices),
            'monthly_prices': dict(monthly_prices),
        })


class PaymentAPIView(APIView):
    def get(self, request):
        payment_id = request.query_params.get('id')
        if payment_id:
            try:
                payment = Payment.objects.get(id=payment_id)
                serializer = PaymentSerializer(payment)
                return Response(serializer.data)
            except Payment.DoesNotExist:
                return Response({'error': 'Payment not found.'}, status=status.HTTP_404_NOT_FOUND)

        year_param = request.query_params.get('year')
        if year_param == '1':
            today = datetime.today()
            start_date = (today - relativedelta(months=12)).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            end_date = today.replace(hour=23, minute=59, second=59, microsecond=999999)

            payments_in_year = Payment.objects.filter(payment_date__range=[start_date, end_date])
            total_price_year = payments_in_year.aggregate(total=Sum('price'))['total'] or 0
            total_items = payments_in_year.count()

            monthly_totals = []
            current_month = start_date
            for i in range(12):
                month_start = current_month
                month_end = (month_start + relativedelta(months=1)) - timedelta(seconds=1)

                total_month_price = payments_in_year.filter(payment_date__range=[month_start, month_end]) \
                    .aggregate(total=Sum('price'))['total'] or 0

                monthly_totals.append({
                    "year": month_start.year,
                    "month": month_start.month,
                    "total_price": total_month_price
                })

                current_month += relativedelta(months=1)

            response_data = {
                "total_price": total_price_year,
                "total_items": total_items,
                "monthly_totals": monthly_totals,
            }

            return Response(response_data)

        filters = Q()
        month_param = request.query_params.get('month')
        if month_param is not None:
            try:
                month_num = int(month_param)
                if month_num < 0:
                    return Response({'error': 'Month parameter cannot be negative.'}, status=status.HTTP_400_BAD_REQUEST)
            except ValueError:
                return Response({'error': 'Invalid month parameter, must be an integer.'}, status=status.HTTP_400_BAD_REQUEST)

            today = datetime.today()
            target_date = today - relativedelta(months=month_num)
            target_year = target_date.year
            target_month = target_date.month

            start_month_date = datetime(target_year, target_month, 1)
            end_month_date = (start_month_date + relativedelta(months=1)) - timedelta(seconds=1)

            filters &= Q(payment_date__range=[start_month_date, end_month_date])

        start_str = request.query_params.get('start')
        end_str = request.query_params.get('end')

        if start_str or end_str:
            try:
                if start_str:
                    start_date = datetime.fromisoformat(start_str)
                    filters &= Q(payment_date__gte=start_date)
                if end_str:
                    end_date = datetime.fromisoformat(end_str)
                    filters &= Q(payment_date__lte=end_date)
            except ValueError:
                return Response({'error': 'Invalid start or end datetime format. Use ISO format.'}, status=status.HTTP_400_BAD_REQUEST)

        for field in ['user', 'price', 'payment_date']:
            if (month_param is not None or start_str or end_str) and field == 'payment_date':
                continue
            value = request.query_params.get(field)
            if value is not None:
                filters &= Q(**{field: value})

        for field in ['duration', 'paid_method', 'payment_status', 'full_name']:
            value = request.query_params.get(field)
            if value is not None:
                filters &= Q(**{f"{field}__icontains": value})

        payments = Payment.objects.filter(filters)

        total_price = None
        if month_param is not None:
            total_price = payments.aggregate(total=Sum('price'))['total'] or 0

        order_by = request.query_params.get('order_by')
        if order_by == 'latest':
            payments = payments.order_by('-payment_date')
        elif order_by == 'earlier':
            payments = payments.order_by('payment_date')
        else:
            payments = payments.order_by('-payment_date')

        total_items = payments.count()

        try:
            page = int(request.query_params.get('page', 1))
            limit = int(request.query_params.get('limit', 10))
            if page < 1 or limit < 1:
                raise ValueError
        except ValueError:
            return Response({'error': 'Invalid pagination parameters'}, status=status.HTTP_400_BAD_REQUEST)

        start = (page - 1) * limit
        end = start + limit
        paginated_payments = payments[start:end]

        serializer = PaymentSerializer(paginated_payments, many=True)
        total_pages = (total_items + limit - 1) // limit

        response_data = {
            "limit": limit,
            "page": page,
            "total_pages": total_pages,
            "total_items": total_items,
            "items": serializer.data
        }

        if total_price is not None:
            response_data = {"total_price": total_price, **response_data}

        return Response(response_data)

    def post(self, request):
        serializer = PaymentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        payment_id = request.query_params.get('id')
        if not payment_id:
            return Response({'error': 'ID query param required for PATCH.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            payment = Payment.objects.get(id=payment_id)
        except Payment.DoesNotExist:
            return Response({'error': 'Payment not found.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = PaymentSerializer(payment, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        payment_id = request.query_params.get('id')
        if not payment_id:
            return Response({'error': 'ID query param required for DELETE.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            payment = Payment.objects.get(id=payment_id)
            payment.delete()
            return Response({'message': 'Payment deleted successfully.'})
        except Payment.DoesNotExist:
            return Response({'error': 'Payment not found.'}, status=status.HTTP_404_NOT_FOUND)