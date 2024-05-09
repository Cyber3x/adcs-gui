from abc import ABC, abstractmethod
from typing import Generic, TypeVar

T = TypeVar('T')


class ISubject(ABC, Generic[T]):
    @abstractmethod
    def add_listener(self, listener: T):
        """Add a listener to list of listeners"""
        pass

    @abstractmethod
    def remove_listener(self, listener: T):
        """Remove listener from a list of listeners"""

    @abstractmethod
    def notify_listeners(self, *args, **kwargs):
        """Notify listeners that an event has happened"""
        pass
