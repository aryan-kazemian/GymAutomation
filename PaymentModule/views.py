from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q, Sum
from .models import Payment
from .serializers import PaymentSerializer
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


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

        # New year filter handling
        year_param = request.query_params.get('year')
        if year_param == '1':
            # Calculate date range for last 12 months from today
            today = datetime.today()
            start_date = (today - relativedelta(months=12)).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            end_date = today.replace(hour=23, minute=59, second=59, microsecond=999999)

            # Filter payments in this range
            payments_in_year = Payment.objects.filter(payment_date__range=[start_date, end_date])

            # Calculate total price for the whole year (last 12 months)
            total_price_year = payments_in_year.aggregate(total=Sum('price'))['total'] or 0

            # Count total items in last 12 months
            total_items = payments_in_year.count()

            # Calculate monthly totals for the last 12 months
            monthly_totals = []
            current_month = start_date
            for i in range(12):
                # Month start
                month_start = current_month
                # Month end is one month ahead minus 1 second
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

        # If year=0 or missing, normal flow with month, start, end filters

        filters = Q()

        # Handle 'month' param with custom logic
        month_param = request.query_params.get('month')
        if month_param is not None:
            try:
                month_num = int(month_param)
                if month_num < 0:
                    return Response({'error': 'Month parameter cannot be negative.'}, status=status.HTTP_400_BAD_REQUEST)
            except ValueError:
                return Response({'error': 'Invalid month parameter, must be an integer.'}, status=status.HTTP_400_BAD_REQUEST)

            # Calculate target year and month based on current date
            today = datetime.today()
            # Go back month_num months
            target_date = today - relativedelta(months=month_num)
            target_year = target_date.year
            target_month = target_date.month

            # Calculate first and last datetime for that month
            start_month_date = datetime(target_year, target_month, 1)
            # To get end of the month, add one month then subtract 1 second
            end_month_date = (start_month_date + relativedelta(months=1)) - timedelta(seconds=1)

            filters &= Q(payment_date__range=[start_month_date, end_month_date])

        # Handle start and end datetime filters (overrides month filtering if both present)
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

        # Exact match filters (skip payment_date if month or start/end filters are applied)
        for field in ['user', 'price', 'payment_date']:
            if (month_param is not None or start_str or end_str) and field == 'payment_date':
                continue
            value = request.query_params.get(field)
            if value is not None:
                filters &= Q(**{field: value})

        # Partial match filters
        for field in ['duration', 'paid_method', 'payment_status', 'full_name']:
            value = request.query_params.get(field)
            if value is not None:
                filters &= Q(**{f"{field}__icontains": value})

        payments = Payment.objects.filter(filters)

        # Calculate total_price only if 'month' is present
        total_price = None
        if month_param is not None:
            total_price = payments.aggregate(total=Sum('price'))['total'] or 0

        # Ordering - default to latest payment_date descending
        order_by = request.query_params.get('order_by')
        if order_by == 'latest':
            payments = payments.order_by('-payment_date')
        elif order_by == 'earlier':
            payments = payments.order_by('payment_date')
        else:
            payments = payments.order_by('-payment_date')  # Default ordering

        total_items = payments.count()

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
        paginated_payments = payments[start:end]

        serializer = PaymentSerializer(paginated_payments, many=True)
        total_pages = (total_items + limit - 1) // limit  # ceiling division

        # Build response
        response_data = {
            "limit": limit,
            "page": page,
            "total_pages": total_pages,
            "total_items": total_items,
            "items": serializer.data
        }

        # Add total_price at the start of response if month filter is used
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
            return Response({'message': 'Payment deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)
        except Payment.DoesNotExist:
            return Response({'error': 'Payment not found.'}, status=status.HTTP_404_NOT_FOUND)
