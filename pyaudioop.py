"""Shim module to satisfy `import pyaudioop` used by pydub on Python 3.13+

pydub>=0.25 includes a fallback implementation located at `pydub.pyaudioop`.  
However, the library still imports it via `import pyaudioop`, assuming the
fallback has been installed as a top-level module.  This shim simply re-exports
all public names from `pydub.pyaudioop`, making them available under the name
`pyaudioop` so that `from pydub import AudioSegment` works without the removed
standard-library `audioop`.
"""

from importlib import import_module

# Import the fallback implementation that ships with pydub
_fallback = import_module("pydub.pyaudioop")

# Re-export everything
globals().update({name: getattr(_fallback, name) for name in dir(_fallback) if not name.startswith("__")})

def __getattr__(name):  # pragma: no cover
    # Support for module-level attribute access
    try:
        return getattr(_fallback, name)
    except AttributeError as exc:
        raise AttributeError(f"module 'pyaudioop' has no attribute {name!r}") from exc
