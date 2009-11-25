# Globally-accessible stuff (like the store) initialised at runtime, not import-time
runtime = {
    'store': None
}

__all__ = ['runtime']
