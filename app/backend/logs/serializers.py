from rest_framework import serializers

from .models import Log


class LogSerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)
    username = serializers.SerializerMethodField()
    action_display = serializers.CharField(source="get_action_display", read_only=True)

    class Meta:
        model = Log
        fields = ["id", "username", "action", "action_display", "payload", "created_at"]

    def get_username(self, obj):
        return obj.user.username if obj.user else None
