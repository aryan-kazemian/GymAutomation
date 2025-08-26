# serializers.py
from rest_framework import serializers
from .models import ClubStats

class ClubStatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClubStats
        fields = '__all__'

    def to_representation(self, instance):
        data = super().to_representation(instance)

        # ---- transform attendance_by_weekday ----
        weekday_list = []
        for idx, (day, value) in enumerate(data.get("attendance_by_weekday", {}).items(), start=1):
            weekday_list.append({
                "id": idx,
                "day": day.lower(),
                "value": value
            })
        data["attendance_by_weekday"] = weekday_list

        # ---- transform membership_trends ----
        # Example Jalali months mapping
        jalali_months = {
            "1": "فروردین", "2": "اردیبهشت", "3": "خرداد",
            "4": "تیر", "5": "مرداد", "6": "شهریور",
            "7": "مهر", "8": "آبان", "9": "آذر",
            "10": "دی", "11": "بهمن", "12": "اسفند"
        }
        trends = []
        for month_num, days_data in data.get("membership_trends", {}).items():
            trends.append({
                "month": jalali_months.get(month_num, month_num),
                "new": sum(days_data.values()),     # 👈 adjust if you want "new" differently
                "active": max(days_data.values())   # 👈 adjust if you want "active" differently
            })
        data["membership_trends"] = trends

        # ---- transform age_groups ----
        colors = {
            "over_35": "#10B981",
            "18_to_25": "#3B82F6",
            "26_to_35": "#8B5CF6",
            "under_18": "#F59E0B",
        }
        age_group_list = []
        for key, value in data.get("age_groups", {}).items():
            age_group_list.append({
                "name": key.replace("_", "-"),  # e.g. "18_to_25" -> "18-25"
                "value": value,
                "color": colors.get(key, "#000000")
            })
        data["age_groups"] = age_group_list

        # ---- transform top_attendance_hours ----
        # If your model already saves [{"hour_range": "12-13", "avg_count": 200}, ...]
        # then convert to the desired shape:
        attendance_hours = []
        for idx, hour_data in enumerate(data.get("top_attendance_hours", []), start=1):
            hour_range = hour_data.get("hour_range", "0-0")
            hour = int(hour_range.split("-")[0])  # just pick start hour
            attendance_hours.append({
                "id": idx,
                "rank": idx,
                "hour": hour,
                "value": hour_data.get("avg_count", 0)
            })
        data["top_attendance_hours"] = attendance_hours

        # You can also modify `top_sports_stats` if needed (e.g. percentages already set in update function)

        return data
