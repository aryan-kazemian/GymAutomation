from rest_framework import generics
from rest_framework.response import Response
from .models import ClubStats
from .serializers import ClubStatsSerializer
from UserModule.models import GenMember
from .models import MemberSubLog
import jdatetime
from datetime import datetime
from django.utils import timezone


def get_jalali_midnight_gregorian(j_year=None, j_month=None, j_day=None):
    """
    Convert Jalali date to aware Gregorian datetime at midnight.
    Defaults to today's Jalali date if none provided.
    """
    if j_year is None or j_month is None or j_day is None:
        now_jalali = jdatetime.datetime.now()
        j_year, j_month, j_day = now_jalali.year, now_jalali.month, now_jalali.day
    midnight_jalali = jdatetime.datetime(j_year, j_month, j_day, 0, 0, 0)
    midnight_gregorian = midnight_jalali.togregorian()
    return timezone.make_aware(datetime(
        midnight_gregorian.year,
        midnight_gregorian.month,
        midnight_gregorian.day
    ))


def update_info():
    stats = ClubStats.objects.latest('date_recorded')
    midnight_today = get_jalali_midnight_gregorian()

    # --- Calculate new members today ---
    new_members_today_count = GenMember.objects.filter(
        creation_datetime__gte=midnight_today,
        person__isnull=False
    ).count()
    stats.new_members_today = new_members_today_count

    # --- Calculate new members yesterday ---
    now_jalali = jdatetime.datetime.now()
    yesterday_jalali = now_jalali - jdatetime.timedelta(days=1)
    yesterday_midnight = get_jalali_midnight_gregorian(
        yesterday_jalali.year, yesterday_jalali.month, yesterday_jalali.day
    )

    new_members_yesterday_count = GenMember.objects.filter(
        creation_datetime__gte=yesterday_midnight,
        creation_datetime__lt=midnight_today,
        person__isnull=False
    ).count()

    progress_pct = int((new_members_today_count / (new_members_yesterday_count or 1)) * 100)
    stats.new_members_change_pct = progress_pct

    # --- Calculate active members today ---
    today_jalali = jdatetime.datetime.now()
    today_midnight = get_jalali_midnight_gregorian(
        today_jalali.year, today_jalali.month, today_jalali.day
    )

    active_members_count = GenMember.objects.filter(
        session_left__gt=0,
        end_date__gte=today_midnight
    ).count()
    stats.active_members = active_members_count

    # --- Calculate active members last month ---
    last_month_jalali = today_jalali.replace(day=1) - jdatetime.timedelta(days=1)
    first_day_last_month = get_jalali_midnight_gregorian(
        last_month_jalali.year, last_month_jalali.month, 1
    )

    last_day_last_month_jalali = jdatetime.date(
        last_month_jalali.year,
        last_month_jalali.month,
        jdatetime.j_days_in_month[last_month_jalali.month - 1]
    )
    last_day_last_month = get_jalali_midnight_gregorian(
        last_day_last_month_jalali.year,
        last_day_last_month_jalali.month,
        last_day_last_month_jalali.day
    )

    last_month_active_members_count = MemberSubLog.objects.filter(
        end_date__gte=first_day_last_month,
        created_at__lte=last_day_last_month
    ).count()

    # Calculate % change vs last month
    if last_month_active_members_count > 0:
        change_pct = int(((active_members_count - last_month_active_members_count) / last_month_active_members_count) * 100)
    else:
        change_pct = 100 if active_members_count > 0 else 0

    stats.active_members_change_pct = change_pct


    stats.save()


class ClubStatsListAPIView(generics.ListAPIView):
    queryset = ClubStats.objects.all()
    serializer_class = ClubStatsSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        if ClubStats.objects.exists():
            update_info()
        else:
            new_stats = ClubStats(
                active_members=0,
                active_members_change_pct=0,
                new_members_today=0,
                new_members_change_pct=0,
                avg_daily_attendance=0,
                attendance_change_pct=0,
                retention_rate_pct=0,
                retention_change_pct=0,
                top1_sport_name='',
                top1_sport_count=0,
                top1_sport_pct=0.0,
                top2_sport_name='',
                top2_sport_count=0,
                top2_sport_pct=0.0,
                top3_sport_name='',
                top3_sport_count=0,
                top3_sport_pct=0.0,
                top1_attendance_hour='',
                top1_attendance_count=0,
                top1_attendance_avg_hours=0.0,
                top2_attendance_hour='',
                top2_attendance_count=0,
                top2_attendance_avg_hours=0.0,
                top3_attendance_hour='',
                top3_attendance_count=0,
                top3_attendance_avg_hours=0.0,
                attendance_by_weekday={},
                avg_hours_by_weekday={},
                membership_trends={},
                age_groups={},
            )
            new_stats.save()
            update_info()

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
