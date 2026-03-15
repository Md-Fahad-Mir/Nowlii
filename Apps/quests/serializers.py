from rest_framework import serializers
from .models import Quests, SubTasks


# ------------------------------------------------------------------------------
# QUESTS
# ------------------------------------------------------------------------------
class QuestsSerializers(serializers.ModelSerializer):
    class Meta:
        model = Quests
        fields = '__all__'

    def to_internal_value(self, data):
        if hasattr(data, '_mutable'):
            mutable_data = data.copy()
        else:
            import copy
            mutable_data = copy.copy(data)
            
        if mutable_data.get('select_a_date') == '':
            mutable_data['select_a_date'] = None
        if mutable_data.get('due_time') == '':
            mutable_data['due_time'] = None
            
        return super().to_internal_value(mutable_data)


# ------------------------------------------------------------------------------
# SUBTASKS
# ------------------------------------------------------------------------------
class SubTasksSerializers(serializers.ModelSerializer):
    class Meta:
        model = SubTasks
        fields = '__all__'