from pyduxlike import *

# IncrementAction, inc_creator_func = create_action_creator("Increment", "attack")
# DecrementAction, dec_creator_func = create_action_creator("Decrement", "attack")
# @default_reducer
# def total_reducer(action):
#     return {
#         "total": 0
#     }

# @total_reducer.register(AddItemAction)
# def _(action, state):
#     return {
#         "total": state["cnt"] + 1
#     }

# @total_reducer.register(DelItemAction)
# def _(action, state):
#     return {
#         "total": state["cnt"] - 1
#     }

# @default_reducer
# def items_reducer(action):
#     return {"items": []}

# @items_reducer.register(AddItemAction)
# def _(action, state):
#     return state["items"].append(action.payload["item"])

# @items_reducer.register(DelItemAction)
# def _(action, state):
#     return state["items"].append(action.payload["item"])
# AddItemAction = create_action("AddItem", "state")
# DelItemAction = create_action("DelItem", "state")

ItemActions = create_grouping_actions("Item", ["AddItem", "DelItem"], "state")


ChangeJpAction = create_action("ChangeJp", "state")
ChangeEnAction = create_action("ChangeEn", "state")


# @default_reducer
# def language_reducer(action):
#     return "en"

# @language_reducer.register(ChangeJpAction)
# def _(action, state):
#     return "jp"

# @language_reducer.register(ChangeEnAction)
# def _(action, state):
#     return "en"


# @default_reducer
# def total_reducer(action):
#     return 0

# @total_reducer.register(AddItemAction)
# def _(action, state):
#     return state + 1

# @total_reducer.register(DelItemAction)
# def _(action, state):
#     return state - 1

# @default_reducer
# def items_reducer(action):
#     return []

# @items_reducer.register(AddItemAction)
# def _(action, state):
#     state.append(action.payload["item"])
#     return state

# @items_reducer.register(DelItemAction)
# def _(action, state):
#     state.remove(action.payload["item"])
#     return state



@default_reducer
def language_reducer(action):
    return "en"

@language_reducer.register(ChangeJpAction)
def _(action, state):
    return "jp"

@language_reducer.register(ChangeEnAction)
def _(action, state):
    return "en"


@default_reducer
def total_reducer(action):
    return 0

@total_reducer.register(ItemActions.AddItem)
def _(action, state):
    return state + 1

@total_reducer.register(ItemActions.DelItem)
def _(action, state):
    return state - 1

@default_reducer
def items_reducer(action):
    return []

@items_reducer.register(ItemActions.AddItem)
def _(action, state):
    state.append(action.payload["item"])
    return state

@items_reducer.register(ItemActions.DelItem)
def _(action, state):
    state.remove(action.payload["item"])
    return state

import time
from threading import Thread

# store = create_store(combine_reducer([total_reducer, items_reducer]))
store = create_store(
    combine_reducer({
        "total": total_reducer,
        "items": items_reducer,
        "language": language_reducer
    })
)

view_complete = lambda a, s: print("{}: {}".format(a.__class__.__name__, s.status))
# store.subscribe(view_complete)


def view_complete2(a, s):
    time.sleep(10)
    print("{}: {}".format(a.__class__.__name__, s.status))

def boil_udon():
    global store
    print("udon")
    store.dispatch(ItemActions.AddItem({"item": "apple"}, view_complete2), blocking="wait")

def make_tuyu():
    global store
    time.sleep(1)
    print("tuyu")
    store.dispatch(ItemActions.DelItem({"item": "apple"}, view_complete), blocking="wait")

def make_ja():
    global store
    time.sleep(3)
    print("jp")
    store.dispatch(ChangeJpAction({}, view_complete), blocking="wait")

    # add_item_action = ItemActions.AddItem({"item": "apple", }, view_complete2, chain=None)
    # store.dispatch(, blocking="wait")
    # store.dispatch(ItemActions.DelItem({"item": "apple"}, view_complete, chain=add_item_action), blocking="wait")



thread1 = Thread(target=boil_udon)
thread2 = Thread(target=make_tuyu)
thread3 = Thread(target=make_ja)

thread1.start()
thread2.start()
thread3.start()


#### あとはここと
#### 状態 ヒストリー(undo)
#### 蘇生
#### チェーン
# store.dispatch(ItemActions.AddItem({"item": "apple"}), blocking="wait")
# store.dispatch(ItemActions.AddItem({"item": "banana"}), blocking="wait")
# store.dispatch(ItemActions.DelItem({"item": "apple"}), blocking="wait")
# store.dispatch(ItemActions.AddItem({"item": "feijoas"}))

# store.dispatch(ChangeJpAction())


store.status

status = MutexDict()

store.status

store.status(keys=["total", "items"])

store.status("total")




# action.chain => []
# a = Action1("pay", callbaxk, chain=[i])
# a => "pay", callbaxk, [i, a]

# def reducer(action, store):
#     b = Action2("pay", callbaxk, action.chain)
#     b => "pay", callbaxk, [i, a, b]





# print(store.status)

# Action {
#     payload  : {any},           // メインの情報
#     callback : {function}, // ビューのためのコールバック
# }

# # インスタン生成で、アクションが生成される
# IncrementAction = create_action(name="IncrementAction", typed="state")
# action = CustomActionType("my super payload", callback)
# store.dispatch(action)


# # 関数で、アクションが生成される
# IncrementAction, creator_func = create_action_creator(name="IncrementAction", typed="state")
# action = creator_func("my payload", callback)
# store.dispatch(action)
