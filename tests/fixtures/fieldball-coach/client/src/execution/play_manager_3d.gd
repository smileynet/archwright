class_name PlayManager3D
extends Node3D
## Pure step executor. Advances through steps, manages chains, signals completion.
## Does NOT: resolve play data, present UI, build objectives.

signal step_completed(step_index: int)
signal run_finished()

var _resolved_play: ResolvedPlayView
var _objectives: Array[RuntimeObjective] = []
var _current_step: int = 0
var _chains_complete: int = 0
var _total_chains: int = 0


func start_execution(resolved_play: ResolvedPlayView, objectives: Array[RuntimeObjective]) -> void:
	_resolved_play = resolved_play
	_objectives = objectives
	_current_step = 0
	_advance_step()


func _advance_step() -> void:
	if _current_step >= _resolved_play.step_count:
		run_finished.emit()
		return

	var step_objectives = _objectives_for_step(_current_step)
	_total_chains = step_objectives.size()
	_chains_complete = 0

	for objective in step_objectives:
		objective.completed.connect(_on_chain_complete)
		objective.start()


func _on_chain_complete() -> void:
	_chains_complete += 1
	if _chains_complete >= _total_chains:
		step_completed.emit(_current_step)
		_current_step += 1
		_advance_step()


func _objectives_for_step(step_index: int) -> Array[RuntimeObjective]:
	return _objectives.filter(func(o): return o.step_index == step_index)
