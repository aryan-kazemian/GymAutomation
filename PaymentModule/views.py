from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from .models import Payment
from .serializers import PaymentSerializer
import jdatetime
from django.db.models import Q, Sum



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

        filters = Q()

        # Check for 'month' param (Jalali month filter)
        month_str = request.query_params.get('month')
        if month_str:
            try:
                month = int(month_str)
                if not (1 <= month <= 12):
                    raise ValueError()
            except ValueError:
                return Response({'error': 'Invalid month parameter, must be 1-12.'}, status=status.HTTP_400_BAD_REQUEST)

            # We want payments where payment_date's Jalali month == month
            # So we will filter payments by converting payment_date to Jalali month in Python
            # This requires us to fetch all payments first and filter manually or filter by possible Gregorian range approx.

            # To optimize, convert the Jalali month to Gregorian date range for this year:
            today_gregorian = jdatetime.date.today().togregorian()
            today_jalali = jdatetime.date.today()

            # To cover full Jalali year, we get Jalali year from today, then calculate first and last day for that month
            jalali_year = today_jalali.year
            start_jalali = jdatetime.date(jalali_year, month, 1)
            # calculate end day for the month (simplest way: use jdatetime.date range +1 month -1 day)
            if month == 12:
                end_jalali = jdatetime.date(jalali_year + 1, 1, 1) - jdatetime.timedelta(days=1)
            else:
                end_jalali = jdatetime.date(jalali_year, month + 1, 1) - jdatetime.timedelta(days=1)

            # convert to Gregorian for filtering in DB:
            start_gregorian = start_jalali.togregorian()
            end_gregorian = end_jalali.togregorian()

            filters &= Q(payment_date__range=[start_gregorian, end_gregorian])

        # Exact match filters
        for field in ['user', 'price', 'payment_date']:
            # Only apply if 'month' not present because payment_date is filtered differently when month is present
            if month_str and field == 'payment_date':
                continue
            value = request.query_params.get(field)
            if value is not None:
                filters &= Q(**{field: value})

        # Partial match filters
        for field in ['duration', 'paid_method', 'payment_status', 'full_name']:
            value = request.query_params.get(field)
            if value is not None:
                filters &= Q(**{f"{field}__icontains": value})

        # Payment date range filter, skip if month param used (to avoid conflicting date filters)
        start_date = request.query_params.get('from')
        end_date = request.query_params.get('to')
        if not month_str:
            if start_date and end_date:
                filters &= Q(payment_date__range=[start_date, end_date])
            elif start_date:
                filters &= Q(payment_date__gte=start_date)
            elif end_date:
                filters &= Q(payment_date__lte=end_date)

        payments = Payment.objects.filter(filters)

        # Calculate total_price only if 'month' is present
        total_price = None
        if month_str:
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
