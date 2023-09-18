from builtins import object, str

from lxml import etree


class GalaxyXML(object):
    def __init__(self):
        self.root = etree.Element("root")

    def export(self):
        return etree.tostring(self.root, pretty_print=True, encoding="unicode")


class Util(object):
    @classmethod
    def coerce(cls, data, kill_lists=False):
        """
        Recursive data sanitisation

        - recurse into lists, dicts, OrderedDict
        - remove dict/OrderedDict entries with None value
        - kill_lists: True -> replace lists by their first element
        """
        if isinstance(data, dict):
            return {k: cls.coerce(v, kill_lists=kill_lists) for k, v in list(data.items()) if v is not None}
        elif isinstance(data, list):
            if kill_lists:
                return cls.coerce(data[0])
            else:
                return [cls.coerce(v, kill_lists=kill_lists) for v in data]
        else:
            return cls.coerce_value(data)

    @classmethod
    def coerce_value(cls, obj):
        """Make everything a string!
        """
        if isinstance(obj, bool):
            if obj:
                return "true"
            else:
                return "false"
        elif isinstance(obj, str):
            return obj
        else:
            return str(obj)

    @classmethod
    def clean_kwargs(cls, params, final=False):
        if "kwargs" in params:
            kwargs = params["kwargs"]
            for k in kwargs:
                params[k] = kwargs[k]
            del params["kwargs"]
        if "self" in params:
            del params["self"]

        if "__class__" in params:
            del params["__class__"]

        # There will be more params, it would be NICE to use a whitelist
        # instead of a blacklist, but until we have more data let's just
        # blacklist stuff we see commonly.
        if final:
            for blacklist in ("positional",):
                if blacklist in params:
                    del params[blacklist]
        return params
