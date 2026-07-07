class_name BallStateService
extends RefCounted
## Single source of truth for ball possession.
## Controllers request transfers; this service validates and commits.

signal possession_changed(new_holder: Fielder)
signal transfer_rejected(requester: Fielder)

var ball_holder: Fielder = null
var _in_flight: bool = false
var _requester: Fielder = null


func request_transfer(requester: Fielder) -> void:
	if _in_flight:
		transfer_rejected.emit(requester)
		return
	if requester == ball_holder:
		transfer_rejected.emit(requester)
		return
	_in_flight = true
	_requester = requester
	_validate_transfer()


func _validate_transfer() -> void:
	# Validation logic — is the requester eligible?
	if _requester != null and _is_valid_receiver(_requester):
		ball_holder = _requester
		_in_flight = false
		_requester = null
		possession_changed.emit(ball_holder)
	else:
		# Reject — ball returns to previous holder
		_in_flight = false
		_requester = null
		transfer_rejected.emit(_requester)


func _is_valid_receiver(fielder: Fielder) -> bool:
	# Placeholder — real logic checks proximity, state, etc.
	return fielder != null
