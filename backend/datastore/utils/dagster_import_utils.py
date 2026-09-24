import os
import warnings
from typing import List, Dict
from dagster import *

# warnings.filterwarnings("ignore", category=ExperimentalWarning)


def _find_instance_in_module(file: str, types: List[type]) -> Dict[str, object]:
    if file.endswith(".py"):
        module_name = file[:-3].replace("/", ".")
        module = importlib.import_module(module_name)
        return {k: v for k, v in module.__dict__.items() if not k.startswith("__") and type(v) in types}


def recursively_find_instances(root: str, types: Sequence[type]) -> Sequence[object]:
    res = {}

    def recurse(path: str):
        if os.path.isfile(path):
            instances = _find_instance_in_module(path, types)
            if instances:
                nonlocal res
                res = res | instances
            return
        else:
            for child in os.listdir(path):
                if not child.startswith("__"):
                    recurse(f"{path}/{child}")

    recurse(root)
    return list(res.values())