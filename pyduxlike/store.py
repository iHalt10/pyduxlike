from threading import Lock
from .actions import StoreInitStateAction, StateAction, AttackAction
from .exceptions import NoSubscriptionFoundError, DispatchBlockingTypeFoundError, ActionTypeFoundError
from .reducer import reducer_validator, get_reducer_typed_list

import copy

class Store(object):
    def __init__(self, reducer):
        self.__reducer = reducer
        self.__status = {}
        self.__status_lock = Lock()
        self.__subscriber = []
        self.__subscriber_lock = Lock()

    def dispatch(self, action, blocking="disable"):
        if isinstance(action, StoreInitStateAction): # single threading
            self.__status = self.__setup_reducers(action)
            return

        if blocking == "disable":
            pass
        elif blocking == "through" and not action.lock.acquire(blocking=False):
            return
        elif blocking == "wait":
            action.lock.acquire()
        else:
            raise DispatchBlockingTypeFoundError("Didn't found blocking type for %s. [disable or through or wait]" % blocking)

        if issubclass(type(action), StateAction):
            partial_next_status = self.__typed_dispatch(action)
            if blocking != "disable":
                action.lock.release()
            return partial_next_status
        else:
            self.__typed_dispatch(action)
            if blocking != "disable":
                action.lock.release()
            return

    def __typed_dispatch(self, action):
        if issubclass(type(action), StateAction):
            if type(self.__reducer) == dict:
                with self.__status_lock:
                    old_status = self.status
                partial_next_status = self.__reducer[StateAction](action, old_status)
                with self.__status_lock:
                    self.__status.update(partial_next_status)
            else:
                with self.__status_lock:
                    self.__status = self.__reducer(action, self.__status)
            for subscriber in self.__subscriber:
                subscriber(action, self)
            if action.callback != None:
                action.callback(action, self)
            return partial_next_status
        elif issubclass(type(action), AttackAction):
            if type(reducer) == dict:
                self.__reducer[AttackAction](action, self)
            else:
                self.__reducer(action, self)
            if action.callback != None:
                action.callback(action, self)
            return
        else:
            raise ActionTypeFoundError("Didn't found action type for %s. [StateAction or AttackAction]" % action)

    def __setup_reducers(self, action):
        if type(self.__reducer) == dict:
            return self.__reducer[StateAction](action, self.__status)
        else:
            return self.__reducer(action)

    @property
    def status(self):
        with self.__status_lock:
            return copy.deepcopy(self.__status)

    def subscribe(self, subscriber):
        with self.__subscriber_lock:
            self.__subscriber.append(subscriber)

    # def partial_resuscitation()
    #     with self.__status_lock:
    #         return copy.deepcopy(self.__status)

    # def unsubscribe(self, subscriber):
    #     try:
    #         self.__subscriber.remove(subscriber)
    #     except ValueError:
    #         raise NoSubscriptionFoundError("Didn't found subscription for: %s" % subscriber)

def _is_init_state(reducer):
    if type(reducer) == dict:
        return StateAction in get_reducer_typed_list()
    else:
        return StateAction == reducer_validator(reducer)

def create_store(reducer):
    store = Store(reducer)
    if _is_init_state(reducer):
        store.dispatch(StoreInitStateAction())
    return store

