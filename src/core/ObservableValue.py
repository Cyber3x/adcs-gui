from typing import TypeVar, Generic, Callable, List

T = TypeVar('T')


class Observable(Generic[T]):
    def __init__(self):
        self._callbacks: List[Callable[[T], None]] = []

    def add_callback(self, callback: Callable[[T], None]):
        self._callbacks.append(callback)

    def remove_callback(self, callback: Callable[[T], None]):
        self._callbacks.remove(callback)

    def _notify_callbacks(self, value: T):
        for callback in self._callbacks:
            callback(value)


class ObservableValue(Observable[T]):
    def __init__(self, default_value: T, name: str = None):
        super().__init__()
        self._value: T = default_value
        self._name: str = name or "ObservableProperty"

    def get(self) -> T:
        return self._value

    def set(self, value: T):
        if self._value != value:
            self._value = value
            self._notify_callbacks(value)

    def get_name(self) -> str:
        return self._name

    def reprJSON(self):
        return self._value


def create_observable_value(default_value: T, name: str = None) -> ObservableValue[T]:
    observable_prop = ObservableValue(default_value, name)
    return observable_prop
