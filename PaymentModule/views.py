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

        # NEW: Daily count dictionary for current year
        daily_count = defaultdict(int)
        daily_agg = year_payments.values('payment_date__date').annotate(
            count=Count('id')
        )

        for item in daily_agg:
            day_key = item['payment_date__date'].strftime('%Y-%m-%d')
            daily_count[day_key] = item['count'] or 0

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
            'daily_count': dict(daily_count),  # ✅ NEW
            'total_price': total_price,
            'total_count': total_count,
            'year_price': year_price,
            'year_count': year_count,
            'month_price': month_price,
            'month_count': month_count,
            'today_price': today_price,
            'today_count': today_count,
            'monthly_prices': dict(monthly_prices),
        })




class PaymentAPIView(APIView):
    def get(self, request):
        year_param = request.query_params.get('year')
        if year_param == '1':
            today = datetime.today()
            start_date = (today - timedelta(days=365)).replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = today.replace(hour=23, minute=59, second=59, microsecond=999999)

            payments_in_year = Payment.objects.filter(payment_date__range=[start_date, end_date]).order_by('-payment_date')
            total_price_year = payments_in_year.aggregate(total=Sum('price'))['total'] or 0
            total_items = payments_in_year.count()

            # Pagination
            try:
                page = int(request.query_params.get('page', 1))
                limit = int(request.query_params.get('limit', 10))
                if page < 1 or limit < 1:
                    raise ValueError
            except ValueError:
                return Response({'error': 'Invalid pagination parameters'}, status=status.HTTP_400_BAD_REQUEST)

            start = (page - 1) * limit
            end = start + limit
            paginated_payments = payments_in_year[start:end]

            serializer = PaymentSerializer(paginated_payments, many=True)
            total_pages = (total_items + limit - 1) // limit

            # Monthly summary: 12 months before + current = 13 total
            monthly_summary = []
            current = start_date.replace(day=1)
            last_month_to_include = (today.replace(day=1) + relativedelta(months=1))  # Start of next month

            while current < last_month_to_include:
                month_start = current
                month_end = (month_start + relativedelta(months=1)) - timedelta(seconds=1)

                month_payments = payments_in_year.filter(payment_date__range=[month_start, month_end])
                month_price = month_payments.aggregate(total=Sum('price'))['total'] or 0
                month_count = month_payments.count()

                monthly_summary.append({
                    "month": f"{month_start.year}-{month_start.month:02d}",
                    "total_price": month_price,
                    "payment_count": month_count
                })

                current += relativedelta(months=1)

            return Response({
                "start_date": start_date.strftime('%Y-%m-%d'),
                "end_date": end_date.strftime('%Y-%m-%d'),
                "total_price": total_price_year,
                "total_items": total_items,
                "limit": limit,
                "page": page,
                "total_pages": total_pages,
                "monthly_summary": monthly_summary,
                "items": serializer.data
            })

        # === NEW FILTERING LOGIC ADDED HERE ===
        start_str = request.query_params.get('start')
        end_str = request.query_params.get('end')

        if start_str or end_str:
            # Parse dates safely, expect format like '2025-4-12'
            try:
                start_date = datetime.strptime(start_str, '%Y-%m-%d') if start_str else None
                end_date = datetime.strptime(end_str, '%Y-%m-%d') if end_str else None
            except ValueError:
                return Response({'error': 'Invalid date format for start or end. Use YYYY-M-D'}, status=status.HTTP_400_BAD_REQUEST)

            payments_filtered = Payment.objects.all()

            if start_date and end_date:
                # start day inclusive (start_date 00:00:00), end day exclusive (end_date 00:00:00)
                payments_filtered = payments_filtered.filter(payment_date__gte=start_date, payment_date__lt=end_date)
            elif start_date:
                payments_filtered = payments_filtered.filter(payment_date__gte=start_date)
            elif end_date:
                payments_filtered = payments_filtered.filter(payment_date__lt=end_date)

            payments_filtered = payments_filtered.order_by('-payment_date')

            total_items = payments_filtered.count()

            # Pagination
            try:
                page = int(request.query_params.get('page', 1))
                limit = int(request.query_params.get('limit', 10))
                if page < 1 or limit < 1:
                    raise ValueError
            except ValueError:
                return Response({'error': 'Invalid pagination parameters'}, status=status.HTTP_400_BAD_REQUEST)

            start = (page - 1) * limit
            end = start + limit
            paginated_payments = payments_filtered[start:end]

            serializer = PaymentSerializer(paginated_payments, many=True)
            total_pages = (total_items + limit - 1) // limit

            return Response({
                "limit": limit,
                "page": page,
                "total_pages": total_pages,
                "total_items": total_items,
                "items": serializer.data
            })
        # === END NEW FILTERING LOGIC ===

        # Default: no year=1 and no start/end, return all with pagination as you already had
        payments = Payment.objects.all().order_by('-payment_date')

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

        return Response({
            "limit": limit,
            "page": page,
            "total_pages": total_pages,
            "total_items": total_items,
            "items": serializer.data
        })


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
