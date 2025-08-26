from rest_framework import serializers

from .models import Reservation, ReservationType


class ReservationSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="name.name")
    reservation_type = serializers.CharField(source="name.reservation_type.name")

    class Meta:
        model = Reservation
        fields = [
            "id",
            "name",
            "reservation_type",
            "date_start",
            "date_end",
            "can_edit",
            "summary",
        ]


class ReservationTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReservationType
        fields = [
            "id",
            "name",
            "fixed_time",
            "default_time_start",
            "default_time_end",
            "summary_required",
            "required_role",
        ]
