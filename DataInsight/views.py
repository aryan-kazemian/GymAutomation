from rest_framework import generics
from rest_framework.response import Response
from .models import ClubStats
from .serializers import ClubStatsSerializer
from UserModule.models import GenMember
import jdatetime
from datetime import datetime
from django.utils import timezone

def get_jalali_midnight_gregorian():
    now_jalali = jdatetime.datetime.now()
    midnight_jalali = jdatetime.datetime(now_jalali.year, now_jalali.month, now_jalali.day, 0, 0, 0)
    midnight_gregorian = midnight_jalali.togregorian()
    return timezone.make_aware(datetime(
        midnight_gregorian.year,
        midnight_gregorian.month,
        midnight_gregorian.day
    ))

def update_info():
            stats = ClubStats.objects.latest('date_recorded')
            midnight_today = get_jalali_midnight_gregorian()

            # Calculate new members today
            new_members_today_count = GenMember.objects.filter(
                creation_datetime__gte=midnight_today,
                person__isnull=False
            ).count()
            stats.new_members_today = new_members_today_count
            

            # Calculate new members yesterday
            now_jalali = jdatetime.datetime.now()
            yesterday_jalali = now_jalali - jdatetime.timedelta(days=1)
            yesterday_midnight = timezone.make_aware(datetime(*yesterday_jalali.togregorian().timetuple()[:3]))

            new_members_yesterday_count = GenMember.objects.filter(
                creation_datetime__gte=yesterday_midnight,
                creation_datetime__lt=midnight_today,
                person__isnull=False
            ).count()

            progress_pct = int((new_members_today_count / (new_members_yesterday_count or 1)) * 100)
            state.new_members_change_pct = progress_pct

             # Calculate Active members

            today_jalali_str = jdatetime.datetime.now().strftime('%Y-%m-%d')
            active_members_count = GenMember.objects.filter(
                session_left__gt=0,
                end_date__gte=today_jalali_str
            ).count()

            stats.active_members = active_members_count

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
