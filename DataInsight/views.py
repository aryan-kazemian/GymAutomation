from rest_framework import generics
from rest_framework.response import Response
from .models import ClubStats, MemberSubLog
from .serializers import ClubStatsSerializer
from UserModule.models import GenMember
from LogModule.models import Log
import jdatetime
from django.utils import timezone
from django.db.models import Count
from datetime import datetime, timedelta
from django.utils.timezone import now
from UserModule.models import GenMember, GenPerson
from datetime import timedelta
from django.utils.timezone import now
from khayyam import JalaliDate
import jdatetime



def jalali_to_gregorian(jalali_date):
    """
    Converts a Jalali date (jdatetime.date or string 'YYYY-MM-DD') to Gregorian date
    """
    if isinstance(jalali_date, str):
        year, month, day = map(int, jalali_date.split('-'))
        jalali_date = jdatetime.date(year, month, day)
    return jalali_date.togregorian()



# Utility function to get Gregorian midnight from Jalali date
def get_jalali_midnight_gregorian(j_year=None, j_month=None, j_day=None):
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


# Update top 3 sports
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
    top_sports_list = []
    for sport_data in sport_counts[:3]:
        sport_id = sport_data['sport']
        count = sport_data['count']
        pct = (count / total_active) * 100
        sport_instance = active_members.filter(sport_id=sport_id).first().sport
        top_sports_list.append({
            "name": sport_instance.name,
            "count": count,
            "percentage": round(pct, 2)
        })
    stats.top_sports_stats = top_sports_list


# Update new members today and yesterday change %
def update_new_members(stats):
    midnight_today = get_jalali_midnight_gregorian()
    new_today = GenMember.objects.filter(
        creation_datetime__gte=midnight_today,
        person__isnull=False
    ).count()
    stats.new_members_today = new_today

    yesterday_jalali = jdatetime.datetime.now() - jdatetime.timedelta(days=1)
    yesterday_midnight = get_jalali_midnight_gregorian(
        yesterday_jalali.year, yesterday_jalali.month, yesterday_jalali.day
    )
    new_yesterday = GenMember.objects.filter(
        creation_datetime__gte=yesterday_midnight,
        creation_datetime__lt=midnight_today,
        person__isnull=False
    ).count()

    stats.new_members_change_pct = int((new_today / (new_yesterday or 1)) * 100)


# Update active members and monthly change %
def update_active_members(stats):
    today_jalali = jdatetime.datetime.now()
    today_midnight = get_jalali_midnight_gregorian(
        today_jalali.year, today_jalali.month, today_jalali.day
    )
    active_today = GenMember.objects.filter(
        session_left__gt=0,
        end_date__gte=today_midnight
    ).count()
    stats.active_members = active_today

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
    last_month_active = MemberSubLog.objects.filter(
        end_date__gte=first_day_last_month,
        created_at__lte=last_day_last_month
    ).count()

    stats.active_members_change_pct = (
        int(((active_today - last_month_active) / last_month_active) * 100)
        if last_month_active > 0 else (100 if active_today > 0 else 0)
    )


# Update average daily attendance
def update_avg_daily_attendance(stats):
    logs = Log.objects.order_by('entry_time').values_list('entry_time', flat=True)
    if not logs:
        stats.avg_daily_attendance = 0.0
        return

    day_counts = {}
    for entry_time in logs:
        entry_time = timezone.localtime(entry_time)
        j_date = jdatetime.date.fromgregorian(
            year=entry_time.year,
            month=entry_time.month,
            day=entry_time.day
        )
        day_counts[j_date] = day_counts.get(j_date, 0) + 1

    stats.avg_daily_attendance = float(sum(day_counts.values()) / len(day_counts))


# Update retention rate and change vs last 6 months
def update_retention(stats):
    expired_subs = MemberSubLog.objects.filter(end_date__lt=timezone.now())
    retained_count = sum(
        MemberSubLog.objects.filter(member=sub.member, created_at__gt=sub.end_date).exists()
        for sub in expired_subs
    )
    total_expired = expired_subs.count()
    stats.retention_rate_pct = int((retained_count / total_expired) * 100) if total_expired > 0 else 0

    six_months_ago = timezone.now() - timedelta(days=30*6)
    past_expired_subs = MemberSubLog.objects.filter(
        end_date__gte=six_months_ago,
        end_date__lt=timezone.now()
    )
    past_retained_count = sum(
        MemberSubLog.objects.filter(member=sub.member, created_at__gt=sub.end_date).exists()
        for sub in past_expired_subs
    )
    past_total = past_expired_subs.count()
    past_avg_retention = (past_retained_count / past_total) * 100 if past_total > 0 else 0
    stats.retention_change_pct = int(stats.retention_rate_pct - past_avg_retention)

# Update top 3 attendance hours with average count per day (ignoring zero days)
def update_top_attendance_hours(stats):
    logs = Log.objects.filter(entry_time__isnull=False, exit_time__isnull=False)
    if not logs.exists():
        stats.top_attendance_hours = []
        return

    from collections import defaultdict
    import math

    attendance_data = defaultdict(lambda: defaultdict(int))

    for log in logs:
        entry_jalali = jdatetime.datetime.fromgregorian(
            datetime=timezone.localtime(log.entry_time)
        )
        exit_jalali = jdatetime.datetime.fromgregorian(
            datetime=timezone.localtime(log.exit_time)
        )

        if exit_jalali <= entry_jalali:
            continue

        start_hour = math.floor(entry_jalali.hour + entry_jalali.minute / 60)
        end_hour = math.floor(exit_jalali.hour + exit_jalali.minute / 60)

        date_key = f"{entry_jalali.year}-{entry_jalali.month:02d}-{entry_jalali.day:02d}"

        for hour in range(start_hour, end_hour + 1):
            next_hour = (hour + 1) % 24
            hour_range = f"{hour}-{next_hour}"
            attendance_data[hour_range][date_key] += 1

    avg_counts = []
    for hour_range, daily_counts in attendance_data.items():
        non_zero_counts = list(daily_counts.values())
        if non_zero_counts:
            avg_count = sum(non_zero_counts) / len(non_zero_counts)
            avg_counts.append({
                "hour_range": hour_range,
                "avg_count": round(avg_count, 2)
            })

    avg_counts.sort(key=lambda x: x["avg_count"], reverse=True)
    stats.top_attendance_hours = avg_counts[:3]


# Update average attendance by weekday (ignoring zero days)
def update_attendance_by_weekday(stats):
    logs = Log.objects.filter(entry_time__isnull=False)
    if not logs.exists():
        stats.attendance_by_weekday = {}
        return

    from collections import defaultdict

    weekday_data = defaultdict(lambda: defaultdict(int))

    for log in logs:
        local_entry = timezone.localtime(log.entry_time)
        weekday_name = local_entry.strftime('%A')
        date_key = local_entry.date().isoformat()
        weekday_data[weekday_name][date_key] += 1

    avg_counts = {}
    for weekday_name, daily_counts in weekday_data.items():
        non_zero_counts = list(daily_counts.values())
        if non_zero_counts:
            avg_count = sum(non_zero_counts) / len(non_zero_counts)
            avg_counts[weekday_name] = round(avg_count, 2)

    stats.attendance_by_weekday = avg_counts


# Update members count by age groups
def update_age_groups(stats):
    """
    Calculates the number of active members in each age group and stores it in the stats.age_groups JSONField.
    Age groups: under_18, 18_to_25, 26_to_35, over_35
    Only considers members with an active membership (end_date in the future).
    All dates are stored in Jalali and converted to Gregorian for calculations.
    """
    age_groups_count = {
        'under_18': 0,
        '18_to_25': 0,
        '26_to_35': 0,
        'over_35': 0
    }

    # Get active members (membership end date in the future)
    active_members = GenMember.objects.filter(end_date__gt=timezone.now())


    for member in active_members:
        if not member.person or not member.person.birth_date:
            continue

        # Convert Jalali birth_date to Gregorian datetime
        try:
            birth_gregorian = jalali_to_gregorian(member.person.birth_date)
        except Exception:
            continue

        # Calculate age
        today = now().date()
        age = today.year - birth_gregorian.year - ((today.month, today.day) < (birth_gregorian.month, birth_gregorian.day))

        # Count in age group
        if age < 18:
            age_groups_count['under_18'] += 1
        elif 18 <= age <= 25:
            age_groups_count['18_to_25'] += 1
        elif 26 <= age <= 35:
            age_groups_count['26_to_35'] += 1
        else:
            age_groups_count['over_35'] += 1

    # Save to stats
    stats.age_groups = age_groups_count
    stats.save()

# Update membership trends for the last 7 months
def update_membership_trends(stats):
    """
    Calculates the daily active members for the last 7 months and stores them in stats.membership_trends JSONField.
    Only considers MemberSubLog entries with end_date later than 7 months ago.
    Dates are converted to Jalali months for keys in the JSON.
    Format:
    {
        "12": {"1": 102, "2": 100, ...},  # month 12 = Esfand
        "1": {"1": 120, "2": 115, ...},   # month 1 = Farvardin
        ...
    }
    """
    today = now().date()
    seven_months_ago = today - timedelta(days=30*7)  # approximate 7 months

    # Filter relevant MemberSubLogs
    recent_logs = MemberSubLog.objects.filter(end_date__gte=seven_months_ago)

    trends = {}

    current_day = seven_months_ago
    while current_day <= today:
        # Convert current day to Jalali
        j_date = JalaliDate(current_day)
        month = str(j_date.month)
        day = str(j_date.day)

        # Count active members on this day
        active_count = recent_logs.filter(
            created_at__date__lte=current_day,
            end_date__date__gte=current_day
        ).count()

        if active_count > 0:
            if month not in trends:
                trends[month] = {}
            trends[month][day] = active_count

        current_day += timedelta(days=1)

    # Save to stats
    stats.membership_trends = trends
    stats.save()


# Main update function
def update_info():
    stats = ClubStats.objects.latest('date_recorded')

    update_new_members(stats)
    update_active_members(stats)
    update_avg_daily_attendance(stats)
    update_retention(stats)
    update_top_sports(stats)
    update_top_attendance_hours(stats)
    update_attendance_by_weekday(stats)
    update_age_groups(stats)
    update_membership_trends(stats)

    stats.save()


# API View
class ClubStatsListAPIView(generics.ListAPIView):
    queryset = ClubStats.objects.all()
    serializer_class = ClubStatsSerializer

    def list(self, request, *args, **kwargs):
        if not ClubStats.objects.exists():
            # Initialize empty stats if none exist
            new_stats = ClubStats(
                active_members=0,
                active_members_change_pct=0,
                new_members_today=0,
                new_members_change_pct=0,
                avg_daily_attendance=0,
                retention_rate_pct=0,
                retention_change_pct=0,
                top_sports_stats=[],
                attendance_by_weekday={},
                membership_trends={},
                age_groups={},
            )
            new_stats.save()

        update_info()

        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
