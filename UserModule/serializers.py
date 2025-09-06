from rest_framework import serializers
import base64
from .models import GenShift, SecUser, GenPerson, GenPersonRole, GenMember, GenMembershipType, Sport, CoachManagement, CoachUsers
from rest_framework import serializers
from .models import GenMember
import base64

class FingerprintSerializer(serializers.ModelSerializer):
    minutiae = serializers.CharField(required=False, allow_blank=True)
    minutiae2 = serializers.CharField(required=False, allow_blank=True)
    minutiae3 = serializers.CharField(required=False, allow_blank=True)

    def to_internal_value(self, data):
        ret = super().to_internal_value(data)
        for field in ['minutiae', 'minutiae2', 'minutiae3']:
            if field in ret and ret[field]:
                ret[field] = base64.b64decode(ret[field])
        return ret

    class Meta:
        model = GenMember
        fields = ['minutiae', 'minutiae2', 'minutiae3', 'has_finger']

class CoachUsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = CoachUsers
        fields = '__all__'


class CoachManagementSerializer(serializers.ModelSerializer):
    coach_users = CoachUsersSerializer(many=True, read_only=True)  # nested users

    class Meta:
        model = CoachManagement
        fields = '__all__'


class Base64BinaryField(serializers.Field):
    def to_internal_value(self, data):
        try:
            return base64.b64decode(data)
        except Exception:
            raise serializers.ValidationError("Invalid base64-encoded data.")

    def to_representation(self, value):
        if value is not None:
            return base64.b64encode(value).decode('utf-8')
        return None


class GenShiftSerializer(serializers.ModelSerializer):
    class Meta:
        model = GenShift
        fields = ['id', 'shift_desc']


class SecUserSerializer(serializers.ModelSerializer):
    creation_datetime = serializers.DateTimeField(read_only=True)

    class Meta:
        model = SecUser
        fields = ['id', 'person', 'username', 'password', 'is_admin', 'shift', 'is_active', 'creation_datetime', 'lincess', 'access', 'is_vip']


class GenPersonSerializer(serializers.ModelSerializer):
    creation_datetime = serializers.DateTimeField(read_only=True)
    person_image = Base64BinaryField(required=False, allow_null=True)
    thumbnail_image = Base64BinaryField(required=False, allow_null=True)

    class Meta:
        model = GenPerson
        fields = [
            'id', 'first_name', 'last_name', 'full_name', 'father_name', 'gender', 'national_code', 'nidentity',
            'person_image', 'thumbnail_image', 'birth_date', 'tel', 'mobile', 'email', 'education', 'job',
            'has_insurance', 'insurance_no', 'ins_start_date', 'ins_end_date', 'address', 'has_parrent',
            'team_name', 'shift', 'user', 'creation_datetime', 'modifier', 'modification_datetime'
        ]


class GenPersonRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = GenPersonRole
        fields = ['id', 'role_desc']


class GenMembershipTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = GenMembershipType
        fields = ['id', 'membership_type_desc']


class GenMemberSerializer(serializers.ModelSerializer):
    face_template_1 = Base64BinaryField(required=False, allow_null=True)
    face_template_2 = Base64BinaryField(required=False, allow_null=True)
    face_template_3 = Base64BinaryField(required=False, allow_null=True)
    face_template_4 = Base64BinaryField(required=False, allow_null=True)
    face_template_5 = Base64BinaryField(required=False, allow_null=True)
    minutiae = Base64BinaryField(required=False, allow_null=True)
    minutiae2 = Base64BinaryField(required=False, allow_null=True)
    minutiae3 = Base64BinaryField(required=False, allow_null=True)
    session_left = serializers.IntegerField(required=False, allow_null=True)

    # ✅ Update sport to FK
    sport = serializers.PrimaryKeyRelatedField(
        queryset=Sport.objects.all(), required=False, allow_null=True
    )

    # Optional: to return sport name instead of ID in GET
    sport_name = serializers.SerializerMethodField()

    def get_sport_name(self, obj):
        return obj.sport.name if obj.sport else None

    class Meta:
        model = GenMember
        fields = [
            'id', 'membership_type', 'card_no', 'person', 'role', 'user', 'shift', 'is_black_list', 'box_radif_no',
            'has_finger', 'membership_datetime', 'modifier', 'modification_datetime', 'is_family', 'max_debit',
            'minutiae', 'minutiae2', 'minutiae3', 'salary', 'couch_id',
            'face_template_1', 'face_template_2', 'face_template_3', 'face_template_4', 'face_template_5',
            'session_left', 'end_date', 'sport', 'sport_name', 'price', "is_single_settion", "balance"
        ]



class SportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sport
        fields = ['id', 'name', 'price']