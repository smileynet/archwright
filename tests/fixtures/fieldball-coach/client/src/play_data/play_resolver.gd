class_name PlayResolver
extends RefCounted
## Resolves authored PlayData into a disposable ResolvedPlayView.
## Shared between editor and runtime — called BEFORE execution starts.

func resolve(play_data: PlayData, format: PlayFormat) -> ResolvedPlayView:
	var view = ResolvedPlayView.new()
	view.step_count = play_data.steps.size()
	# Resolution logic: match positions to slots, resolve paths, etc.
	for step in play_data.steps:
		_resolve_step(step, format, view)
	return view


func _resolve_step(step: PlayStepData, format: PlayFormat, view: ResolvedPlayView) -> void:
	# Resolve each position's actions against the format's slot definitions
	pass
