# Copied from https://github.com/Athesdrake/aiotfm/blob/master/aiotfm/client.py

import sys
import asyncio
import traceback


class EventBased:
	"""A class that implements asynchronous events
	"""
	def __init__(self):
		self._waiters = {}

	def event(self, coro):
		"""A decorator that registers an event.
		"""
		name = coro.__name__
		if not name.startswith('on_'):
			raise InvalidEvent("'{}' isn't a correct event naming.".format(name))
		if not asyncio.iscoroutinefunction(coro):
			message = "Couldn't register a non-coroutine function for the event {}.".format(name)
			raise InvalidEvent(message)

		setattr(self, name, coro)
		return coro

	def wait_for(self, event, condition=None, timeout=None, stopPropagation=False):
		"""Wait for an event.
		:param event: :class:`str` the event name.
		:param condition: Optional[`function`] A predicate to check what to wait for.
			The arguments must meet the parameters of the event being waited for.
		:param timeout: Optional[:class:`int`] the number of seconds before
			throwing asyncio.TimeoutError
		:return: [`asyncio.Future`](https://docs.python.org/3/library/asyncio-future.html#asyncio.Future)
			a future that you must await.
		"""
		event = event.lower()
		future = self.loop.create_future()

		if condition is None:
			def everything(*a):
				return True
			condition = everything

		if event not in self._waiters:
			self._waiters[event] = []

		self._waiters[event].append((condition, future, stopPropagation))

		return asyncio.wait_for(future, timeout)

	async def _run_event(self, coro, event_name, *args, **kwargs):
		"""|coro|
		Runs an event and handle the error if any.
		:param coro: a coroutine function.
		:param event_name: :class:`str` the event's name.
		:param args: arguments to pass to the coro.
		:param kwargs: keyword arguments to pass to the coro.
		:return: :class:`bool` whether the event ran successfully or not
		"""
		try:
			await coro(*args, **kwargs)
			return True
		# except asyncio.CancelledError:
		# 	raise
		except Exception as e:
			if hasattr(self, 'on_error'):
				await self.on_error(event_name, e, *args, **kwargs)
		return False

	def dispatch(self, event, *args, **kwargs):
		"""Dispatches events
		:param event: :class:`str` event's name. (without 'on_')
		:param args: arguments to pass to the coro.
		:param kwargs: keyword arguments to pass to the coro.
		:return: [`Task`](https://docs.python.org/3/library/asyncio-task.html#asyncio.Task)
			the _run_event wrapper task
		"""
		method = 'on_' + event

		if method in self._waiters:
			to_remove = []
			waiters = self._waiters[method]
			for i, (cond, fut, stop) in enumerate(waiters):
				if fut.cancelled():
					to_remove.append(i)
					continue

				try:
					result = bool(cond(*args))
				except Exception as e:
					fut.set_exception(e)
				else:
					if result:
						fut.set_result(args[0] if len(args) == 1 else args if len(args) > 0 else None)
						if stop:
							del waiters[i]
							return None
						to_remove.append(i)

			if len(to_remove) == len(waiters):
				del self._waiters[method]
			else:
				for i in to_remove[::-1]:
					del waiters[i]

		coro = getattr(self, method, None)
		if coro is not None:
			dispatch = self._run_event(coro, method, *args, **kwargs)
			return self.loop.call_soon_threadsafe(
				self.loop.create_task,
				dispatch
			)

	async def on_error(self, event, err, *a, **kw):
		"""Default on_error event handler. Prints the traceback of the error."""
		message = '\nAn error occurred while dispatching the event "{0}":\n\n{2}'
		tb = traceback.format_exc(limit=-3)
		print(message.format(event, err, tb), file=sys.stderr)
		return message.format(event, err, tb)