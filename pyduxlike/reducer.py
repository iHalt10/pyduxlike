import collections
from functools import singledispatch
from .actions import StoreInitStateAction, StateAction, AttackAction, Action
from .exceptions import WrongFormattedReducerArgs

default_reducer = singledispatch

def reducer_validator(reducer):
    typed = None
    for action in reducer.registry.keys():
        if issubclass(action, Action):
            if typed == None:
                typed = action.__bases__[0]
                continue
            if not issubclass(action, typed):
                raise WrongFormattedReducerArgs("[%s] One reducer can't contain multiple types of Actions (state, attack)." % reducer)
    return typed

def _reducers_validator_and_get_list(reducers):
    reducer_typed_list = []
    for reducer in reducers:
        reducer_typed_list.append( reducer_validator(reducer) )
    return reducer_typed_list

def _get_reducer_name_from_func(func):
    return func.__name__

def _determine_reducer_names_and_funcs(reducers):
    if isinstance(reducers, (collections.Mapping,)):
        reducer_names = reducers.keys()
        reducer_funcs = reducers.values()

    elif isinstance(reducers, collections.Iterable):
        reducer_names = list(map(lambda red: _get_reducer_name_from_func(red), reducers))
        reducer_funcs = reducers
    else:
        raise WrongFormattedReducerArgs(
            "Reducer-Argument has to be dict(str, func) or an iterable of funcs! Found instead: <%s>" % str(reducers))
    return reducer_names, reducer_funcs


def _get_initial_reducer_state(reducer_func):
    return reducer_func(StoreInitStateAction())

_reducer_typed_list = []
def get_reducer_typed_list():
    return _reducer_typed_list

def combine_reducer(reducers):
    global _reducer_typed_list
    reducer_names, reducer_funcs = _determine_reducer_names_and_funcs(reducers)
    _reducer_typed_list = _reducers_validator_and_get_list(reducer_funcs)

    final_reducers = { StateAction: [], AttackAction: [] }
    for typed, name, func in zip(_reducer_typed_list, reducer_names, reducer_funcs):
        final_reducers[typed].append((name, func))

    # print(final_reducers)

    combined_initial_status = {}
    if StateAction in _reducer_typed_list:
        state_typed_reducer_names = []
        state_typed_reducer_funcs = []
        for reducer_name, reducer_func in final_reducers[StateAction]:
            state_typed_reducer_names.append(reducer_name)
            state_typed_reducer_funcs.append(reducer_func)
        combined_initial_status = dict(
            list(map(
                    lambda red_name, red_func: (red_name, _get_initial_reducer_state(red_func)),
                    state_typed_reducer_names, state_typed_reducer_funcs
                )
            )
        )
    # print(combined_initial_status)

    def state_combination(action, status):
        if status == {}:
            return combined_initial_status
        partial_next_status = {}
        for reducer_name, reducer_func in final_reducers[StateAction]:
            if not type(action) in reducer_func.registry.keys():
                continue
            old_state = status[reducer_name]
            new_state = reducer_func(action, old_state)
            partial_next_status[reducer_name] = new_state
        return partial_next_status

    def attack_combination(action, store):
        for reducer_name, reducer_func in final_reducers[AttackAction]:
            reducer_func(action, store)

    combination = { StateAction: state_combination, AttackAction: attack_combination}
    return combination



# def combination(action, store):
#     if issubclass(type(action), StateAction):
#         if store.status == {}:
#             return combined_initial_status
#         next_status = store.status.copy()
#         for reducer_name, reducer_func in final_reducers[StateAction]:
#             old_state = next_status[reducer_name]
#             new_state = reducer_func(action, old_state)
#             next_status[reducer_name] = new_state
#         return next_status
#     else:
#         for reducer_name, reducer_func in final_reducers[AttackAction]:
#             reducer_func(action, store)
#         return

