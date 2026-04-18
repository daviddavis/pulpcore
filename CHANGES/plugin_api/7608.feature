Added a `task_kwargs` field to `TaskSchedule`, allowing plugins to store keyword arguments that
are forwarded to tasks when they are dispatched on schedule. `TaskSchedule` and
`TaskScheduleSerializer` are now exposed via the plugin API.
