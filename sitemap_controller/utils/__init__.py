import sys
import typing as t
import types
import os


def from_envvar(settings, variable_name: str, silent: bool = False) -> bool:
    rv = os.environ.get(variable_name)
    if not rv:
        if silent:
            return False
        raise RuntimeError(
            f"The environment variable {variable_name!r} is not set"
            " and as such configuration could not be loaded. Set"
            " this variable and make it point to a configuration"
            " file"
        )
    return from_pyfile(settings, rv)


def from_pyfile(settings, filename: str) -> bool:
    filename = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "../../", filename
    )
    d = types.ModuleType("config")
    d.__file__ = filename
    try:
        with open(filename, mode="rb") as config_file:
            exec(compile(config_file.read(), filename, "exec"), d.__dict__)
    except OSError as e:
        e.strerror = f"Unable to load configuration file ({e.strerror})"
        return False

    from_object(settings, d)
    return True


def from_object(settings, obj):
    if isinstance(obj, str):
        obj = import_string(obj)
    for key in dir(obj):
        if key.isupper():
            settings[settings.default_section][key] = getattr(obj, key)


def import_string(import_name: str) -> t.Any:
    import_name = import_name.replace(":", ".")
    try:
        try:
            __import__(import_name)
        except ImportError:
            if "." not in import_name:
                raise
        else:
            return sys.modules[import_name]

        module_name, obj_name = import_name.rsplit(".", 1)
        module = __import__(module_name, globals(), locals(), [obj_name])
        try:
            return getattr(module, obj_name)
        except AttributeError as e:
            raise ImportError(e) from None

    except ImportError as e:
        return None
