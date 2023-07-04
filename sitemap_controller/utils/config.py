import os
import sys
import typing as t
import types

settings = None


class Config(dict):
    global settings

    def __init__(self):
        self.settings = settings

    def has_option(self, option: str) -> bool:
        if option in self.keys():
            return True
        return False

    def get(self, option: str, default: t.Any = None) -> t.Any:
        if self.has_option(option):
            return self[option]
        else:
            return default

    def from_envvar(self, variable_name: str, silent: bool = False) -> bool:
        rv = os.environ.get(variable_name)
        if not rv:
            if silent:
                print(f"The environment variable {variable_name!r} is not set")
                return False
            raise RuntimeError(
                f"The environment variable {variable_name!r} is not set"
                " and as such configuration could not be loaded. Set"
                " this variable and make it point to a configuration"
                " file"
            )
        return self.from_pyfile(rv)

    def from_pyfile(self, filename: str) -> bool:
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

        self.from_object(d)
        return True

    def from_object(self, obj):
        if isinstance(obj, str):
            obj = self.import_string(obj)
        for key in dir(obj):
            if key.isupper():
                self[key] = getattr(obj, key)
                setattr(self, key, self[key])

    def import_string(self, import_name: str) -> t.Any:
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
