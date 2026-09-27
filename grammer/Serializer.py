from rest_framework import serializers
from .models import Notes

class NotesSerializer(serializers.ModelSerializer):
    note = serializers.CharField(source='content', required=False)

    class Meta:
        model = Notes
        fields = ['id', 'title', 'content', 'note', 'timestamp']
        read_only_fields = ['id', 'timestamp']

    def to_internal_value(self, data):
        # Allow client to send either {"content": "..."} or {"note": "..."}
        if isinstance(data, dict):
            if 'content' not in data and 'note' in data:
                data = data.copy()
                data['content'] = data['note']
        return super().to_internal_value(data)