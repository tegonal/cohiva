from django.contrib.auth.models import Group, User
from rest_framework import serializers

from .models import Contract, RentalUnit


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["url", "username", "email", "groups"]


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ["url", "name"]


class RentalUnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = RentalUnit
        fields = [
            "id",
            "url",
            "name",
            "label",
            "label_short",
            "rental_type",
            "rooms",
            "min_occupancy",
            "building",
            "floor",
            "area",
            "area_balcony",
            "area_add",
            "height",
            "volume",
            "rent_total",
            "rent_year",
            "nk",
            "nk_electricity",
            "share",
            "depot",
            "note",
            "description",
            "status",
            "adit_serial",
            "comment",
            "ts_created",
            "ts_modified",
        ]


## Alternative: HyperlinkedModelSerializer
## -> uses hyperlinks to represent relationships, rather than primary keys.
class ContractSerializer(serializers.ModelSerializer):
    contact_formal = serializers.SerializerMethodField()

    def get_contact_formal(self, obj):
        adr = obj.get_contact_address()
        if adr:
            return adr.formal
        return True

    class Meta:
        model = Contract
        fields = [
            "id",
            "url",
            "contractors",
            "main_contact",
            "rental_units",
            "state",
            "date",
            "date_end",
            "rent_reduction",
            "share_reduction",
            "send_qrbill",
            "billing_contract",
            "note",
            "comment",
            "ts_created",
            "ts_modified",
            "contact_formal",
        ]
        ## exclude unused fields: 'children', 'children_old', 'emonitor_id',
        ## 'object_actions', 'links', 'backlinks'
