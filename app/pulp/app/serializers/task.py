from rest_framework import serializers

from pulp.app import models
from pulp.app.serializers import ModelSerializer


class TaskTagSerializer(serializers.ModelSerializer):
    name = serializers.CharField(
        help_text="The name of the tag",
    )

    class Meta:
        model = models.TaskTag
        fields = ('name',)


class TaskSerializer(ModelSerializer):
    group = serializers.UUIDField(
        help_text="The group that this task belongs to.",
        read_only=True
    )

    state = serializers.CharField(
        help_text="The current state of the task. The possible values include:"
                  " 'waiting', 'skipped', 'running', 'completed', 'failed' and 'canceled'.",
        read_only=True
    )

    started_at = serializers.DateTimeField(
        help_text="Timestamp of the when this task started execution.",
        read_only=True
    )

    finished_at = serializers.DateTimeField(
        help_text="Timestamp of the when this task stopped execution.",
        read_only=True
    )

    non_fatal_errors = serializers.JSONField(
        help_text="A JSON Object of errors encountered during the execution of this task.",
        read_only=True
    )

    result = serializers.JSONField(
        help_text="A JSON Object of what this task returned (if any).",
        read_only=True
    )

    worker = serializers.HyperlinkedRelatedField(
        help_text="The worker associated with this task."
                  " This field is empty if a worker is not yet assigned.",
        read_only=True,
        view_name='workers-detail'
    )

    parent = serializers.HyperlinkedRelatedField(
        help_text="The parent task that spawned this task.",
        read_only=True,
        view_name='tasks-detail'
    )

    tags = TaskTagSerializer(
        many=True,
        read_only=True
    )

    class Meta:
        model = models.Task
        fields = ModelSerializer.Meta.fields + ('group', 'state', 'started_at',
                                                'finished_at', 'non_fatal_errors',
                                                'result', 'worker', 'parent', 'tags')

