from lxml import etree

class GalaxyXML(object):

    def __init__(self):
        self.root = etree.Element('root')

    def export(self):
        return etree.tostring(self.root, pretty_print=True)


class Util(object):

    @classmethod
    def coerce(cls, data):
        """Recursive data sanitisation
        """
        if isinstance(data, dict):
            return {k: cls.coerce(v) for k, v in data.items() if v is not None}
        elif isinstance(data, list):
            return [cls.coerce(v) for v in data]
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
    def clean_kwargs(cls, params):
        if 'kwargs' in params:
            kwargs = params['kwargs']
            for k in kwargs:
                params[k] = kwargs[k]
            del params['kwargs']
        del params['self']
        return params
