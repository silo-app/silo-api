import importlib
from typing import Type


def load_class_from_string(class_path: str) -> Type:
    try:
        module_path, class_name = class_path.rsplit(".", 1)
        module = importlib.import_module(module_path)
        return getattr(module, class_name)
    except (ValueError, ImportError, AttributeError) as e:
        raise ImportError(f"Could not load class '{class_path}': {e}")
