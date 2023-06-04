from threading import Lock
from dataclasses import make_dataclass
from types import FunctionType, new_class
from typing import ClassVar
from .exceptions import ActionTypeFoundError

class Action():
    pass

StateAction = new_class("StateAction", (Action, ))
AttackAction = new_class("AttackAction", (Action, ))

_create_typed_action = lambda n, l, c: make_dataclass(n, [("lock", ClassVar[Lock], l), ("payload", type, None), ("callback", FunctionType, None)] , bases=(c, ))

def create_action(name, typed):
    if typed == "state":
        _Action = _create_typed_action(name, Lock(), StateAction)
    elif typed  == "attack":
        _Action = _create_typed_action(name, Lock(), AttackAction)
    else:
        raise ActionTypeFoundError("Didn't found action type for %s. [StateAction or AttackAction]" % typed)
    return _Action

def create_action_creator(name, typed):
    _Action = create_action(name, typed)
    def _action_creator(payload=None, callback=None):
        return _Action(payload, callback)
    return _Action, _action_creator

StoreInitStateAction = create_action("INTERNAL_INIT_STATE_ACTION", typed="state")


def create_grouping_actions(group_name, action_names, typed):
    lock = Lock()
    fields = []
    if typed == "state":
        for action_name in action_names:
            _Action = _create_typed_action(action_name, lock, StateAction)
            fields.append( (action_name, ClassVar[_Action], _Action) )
    elif typed  == "attack":
        for action_name in action_names:
            _Action = _create_typed_action(action_name, lock, AttackAction)
            fields.append( (action_name, ClassVar[_Action], _Action) )
    else:
        raise ActionTypeFoundError("Didn't found action type for %s. [StateAction or AttackAction]" % typed)
    return make_dataclass(group_name, fields, bases=(type, ))
