"""
event.py - Event system

A Class decorator event system.

Copyright (c) 2018 The Fuel Rats Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md
"""
import logging
from functools import wraps
from typing import Callable, List, Dict, Union

# typedef
subscriptions = List[Callable]
log = logging.getLogger(f"mecha.{__name__}")


class Event:
    """
    Registers a async function as an event.

    The registered event will be the name of the decorated function.

    Examples:
        any async function definition can be decorated, and the function will be registered as a
        command
         >>> @Event
         ... async def my_event(*args, **kwargs):
         ...    pass
         >>> "my_event" in Event.events
         True

         an event can also be defined without a function definition
         >>> my_other_event = Event("my_other_event")
         >>> "my_other_event" in Event.events
         True

         Notes:
             Events declared via the Event("name") form will need to be invoked by something.

             Events are callables, and should be treated like async functions when called.
    """
    events: Dict[str, 'Event'] = {}
    """Registry mapping event names to their subscribers"""

    def __init__(self, coro: Union[Callable, str]):
        log.debug(f"decorating coro {coro}")
        if callable(coro):
            # decorator form
            self.decorated_coro = coro
            self.name = coro.__name__
        elif isinstance(coro, str):
            # Event("name") form
            self.decorated_coro = None
            self.name = coro

        self.subscribers: subscriptions = []
        """This events subscribers"""

        Event._register(self)

    async def _emit(self, *args, **kwargs):
        """Emit an event to all subscribers"""
        for subscriber in self.subscribers:
            log.debug(f"calling subscriber {subscriber}...")
            await subscriber(*args, **kwargs)

    async def __call__(self, *args, **kwargs):
        log.debug(f"event {self.name} invoked...")
        if self.decorated_coro is not None:
            await self.decorated_coro(*args, **kwargs)
        log.debug(f"emitting event to subscribers...")
        await self._emit(*args, **kwargs)

    @classmethod
    def _register(cls, event: 'Event'):
        """
        Registers a new event

        Args:
            event(Event): Event to register

        Raises:
            ValueError: attempted to register an event has already been registered
        """
        if event.name in cls.events:
            raise ValueError(f"name {event.name} is already registered as an event. "
                             f"please choose a different name")
        cls.events[event.name] = event

    @classmethod
    def subscribe(cls, event_name):
        """
        Subscribe to an event

        Args:
            event_name (str):
        """

        def decorator(coro):
            """
            decorator that returns the wrapped function
            """

            @wraps(coro)
            async def wrapper(*args, **kwargs):
                """
                Simple pass-pass through wrapper
                """
                return await coro(*args, **kwargs)

            # do reg here
            if event_name in cls.events:
                cls.events[event_name].subscribers.append(coro)
            else:
                raise ValueError
            return wrapper

        return decorator