import functools
import inspect

from utils.logger import get_logger

logger = get_logger("step")


class _ReadableDict(dict):
    """Formats as `key=value, ...` in step titles, while `{arg[key]}` still works."""

    def __format__(self, spec):
        return ", ".join(f"{key}={value}" for key, value in self.items())


def step(title: str):
    """Log a readable step before the call; {placeholders} are filled from the call arguments."""

    def decorator(func):
        signature = inspect.signature(func)

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            arguments = signature.bind(*args, **kwargs)
            arguments.apply_defaults()
            values = {
                name: _ReadableDict(value) if isinstance(value, dict) else value
                for name, value in arguments.arguments.items()
            }
            logger.info("STEP: %s", title.format(**values))
            return func(*args, **kwargs)

        return wrapper

    return decorator
