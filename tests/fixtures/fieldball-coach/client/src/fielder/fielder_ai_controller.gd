class_name FielderAIController
extends Node3D
## AI controller for a fielder. Drives movement and ball interactions.
## Does NOT write ball_holder directly — uses BallStateService.

var _ball_state_service: BallStateService
var _fielder: Fielder
var _current_objective: RuntimeObjective = null


func initialize(fielder: Fielder, ball_state: BallStateService) -> void:
	_fielder = fielder
	_ball_state_service = ball_state


func _on_catch_opportunity() -> void:
	# Request transfer through the service — never write directly
	_ball_state_service.request_transfer(_fielder)


func _on_objective_assigned(objective: RuntimeObjective) -> void:
	_current_objective = objective
	_current_objective.completed.connect(_on_objective_complete)


func _on_objective_complete() -> void:
	_current_objective = null
