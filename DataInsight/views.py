from rest_framework import generics
from rest_framework.response import Response
from .models import ClubStats
from .serializers import ClubStatsSerializer
from UserModule.models import GenMember
from .models import MemberSubLog
import jdatetime
from django.utils import timezone
from django.db.models import Count, Avg, F
from django.utils import timezone
from datetime import datetime, timedelta
from LogModule.models import Log
from django.db.models import Max



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


def update_top_sports(stats):
    now = timezone.now()
    active_members = GenMember.objects.filter(
        end_date__gte=now,
        sport__isnull=False
    )

    total_active = active_members.count() or 1

    sport_counts = (
        active_members
        .values('sport')
        .annotate(count=Count('id'))
        .order_by('-count')
    )

    top_sports = sport_counts[:3]
    
    for idx in range(3):
        if idx < len(top_sports):
            sport_id = top_sports[idx]['sport']
            count = top_sports[idx]['count']
            pct = (count / total_active) * 100

            sport_instance = active_members.filter(sport_id=sport_id).first().sport

            setattr(stats, f'top{idx+1}_sport_name', sport_instance)
            setattr(stats, f'top{idx+1}_sport_count', count)
            setattr(stats, f'top{idx+1}_sport_pct', round(pct, 2))
        else:
            setattr(stats, f'top{idx+1}_sport_name', None)
            setattr(stats, f'top{idx+1}_sport_count', 0)
            setattr(stats, f'top{idx+1}_sport_pct', 0.0)




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

    # Calculate  Avg Daily Attendance 

    logs = Log.objects.order_by('entry_time').values_list('entry_time', flat=True)

    if not logs:
        return 0.0

    day_counts = {}
    for entry_time in logs:
        entry_time = timezone.localtime(entry_time)
        j_date = jdatetime.date.fromgregorian(
            year=entry_time.year,
            month=entry_time.month,
            day=entry_time.day
        )
        day_counts[j_date] = day_counts.get(j_date, 0) + 1

    if not day_counts:
        return 0.0

    avg = sum(day_counts.values()) / len(day_counts)
    stats.avg_daily_attendance = float(avg)


    # Get the latest subscription end date to define the current month
    now_jalali = jdatetime.datetime.now()
    first_day_six_months_ago = get_jalali_midnight_gregorian(
        now_jalali.year, max(now_jalali.month - 5, 1), 1
    )

    # --- Retention rate calculation ---
    # Members whose subscription ended this month
    expired_subs = MemberSubLog.objects.filter(
        end_date__lt=timezone.now()
    )

    retained_count = 0
    for sub in expired_subs:
        has_renewed = MemberSubLog.objects.filter(
            member=sub.member,
            created_at__gt=sub.end_date
        ).exists()
        if has_renewed:
            retained_count += 1

    total_expired = expired_subs.count()
    if total_expired > 0:
        stats.retention_rate_pct = int((retained_count / total_expired) * 100)
    else:
        stats.retention_rate_pct = 0

    # --- Retention change vs last 6 months ---
    # Calculate average retention for the last 6 months
    six_months_ago = timezone.now() - timedelta(days=30*6)
    past_expired_subs = MemberSubLog.objects.filter(
        end_date__gte=six_months_ago,
        end_date__lt=timezone.now()
    )

    past_retained_count = 0
    for sub in past_expired_subs:
        has_renewed = MemberSubLog.objects.filter(
            member=sub.member,
            created_at__gt=sub.end_date
        ).exists()
        if has_renewed:
            past_retained_count += 1

    past_total = past_expired_subs.count()
    if past_total > 0:
        past_avg_retention = (past_retained_count / past_total) * 100
        stats.retention_change_pct = int(stats.retention_rate_pct - past_avg_retention)
    else:
        stats.retention_change_pct = 0

    # Calculate Top 3 Sport 

    update_top_sports(stats)

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
                retention_rate_pct=0,
                retention_change_pct=0,
                top1_sport_name=None,
                top1_sport_count=0,
                top1_sport_pct=0.0,
                top2_sport_name=None,
                top2_sport_count=0,
                top2_sport_pct=0.0,
                top3_sport_name=None,
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
