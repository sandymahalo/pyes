#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Alberto Paro'
__all__ = ['clean_string', 'ResultSet', "ESRange", "ESRangeOp"]


# Characters that are part of Lucene query syntax must be stripped
# from user input: + - && || ! ( ) { } [ ] ^ " ~ * ? : \
# See: http://lucene.apache.org/java/3_0_2/queryparsersyntax.html#Escaping
SPECIAL_CHARS = [33, 34, 38, 40, 41, 42, 45, 58, 63, 91, 92, 93, 94, 123, 124, 125, 126]
UNI_SPECIAL_CHARS = dict((c, None) for c in SPECIAL_CHARS)
STR_SPECIAL_CHARS = ''.join([chr(c) for c in SPECIAL_CHARS])

class ESRange(object):
    def __init__(self, field, from_value=None, to_value=None, include_lower=None, 
                 include_upper=None, boost=None, **kwargs):
        """
        type can be "gt", "gte", "lt", "lte"
        
        """
        self.field = field
        self.from_value = from_value
        self.to_value = to_value
        self.type = type
        self.include_lower = include_lower
        self.include_upper = include_upper
        self.boost = boost
    
    def serialize(self):
        
        filters = {}
        if self.from_value is not None:
            filters['from'] = self.from_value
        if self.to_value is not None:
            filters['to'] = self.to_value
        if self.include_lower is not None:
            filters['include_lower'] = self.include_lower
        if self.include_upper is not None:
            filters['include_upper'] = self.include_upper
        if self.boost is not None:
            filters['boost'] = self.boost
        return self.field, filters

class ESRangeOp(ESRange):
    def __init__(self, field, op, value, boost=None):
        from_value = to_value = include_lower = include_upper = None
        if op == "gt":
            from_value = value
            include_lower = False
        elif op == "gte":
            from_value = value
            include_lower = True
        if op == "lt":
            to_value = value
            include_upper = False
        elif op == "lte":
            to_value = value
            include_upper = True
        super(ESRangeOp, self).__init__(field, from_value, to_value, \
                include_lower, include_upper, boost)

def clean_string(text):
    """
    Remove Lucene reserved characters from query string
    """
    if isinstance(text, unicode):
        return text.translate(UNI_SPECIAL_CHARS)
    return text.translate(None, STR_SPECIAL_CHARS)
    
class ResultSet(object):
    def __init__(self, results, fix_keys = True, clean_highlight=True):
        """
        results: an es query results dict
        fix_keys: remove the "_" from every key, useful for django views
        clean_highlight: removed empty highlight
        """
        self.results = results
        self._total = None
        self.valid = False
        self.facets = self.results.get('facets', {})
        if 'hits' in self.results:
            self.valid = True
            self.results = self.results['hits']
        if fix_keys:
            self.fix_keys()
        if clean_highlight:
            self.clean_highlight()
        
    @property
    def total(self):
        if self._total is None:
            self._total = 0
            if self.valid:
                self._total = self.results.get("total", 0)
        return self._total
    
    def fix_keys(self):
        """
        Remove the _ from the keys of the results
        """
        if not self.valid:
            return
        
        for hit in self.results['hits']:
            for key, item in hit.items():
                if key.startswith("_"):
                    hit[key[1:]]=item
                    del hit[key]
    
    def clean_highlight(self):
        """
        Remove the empty highlight
        """
        if not self.valid:
            return
        
        for hit in self.results['hits']:
            if 'highlight' in hit:
                hl = hit['highlight']
                for key, item in hl.items():
                    if not item:
                        del hl[key]
    
    def __getattr__(self, name):
        if name in self.results:
            return self.results[name]

def keys_to_string(data):
    """
    Function to convert all the unicode keys in string keys
    """
    if isinstance(data, dict):
        for key in list(data.keys()):
            if isinstance(key, unicode):
                value = data[key]
                val = keys_to_string(value)
                del data[key]
                data[str(key)] = val
    return data

#def process_query_result(func):
#    @wraps(func)
#    def _func(*args, **kwargs):
#        result = func(*args, **kwargs)
#        if 'hits' in result:
#            setattr(result, "total", result['hits']['total'])
#            if 'hits' in result['hits']:
#                for hit in result['hits']['hits']:
#                    for key, item in hit.items():
#                        if key.startswith("_"):
#                            hit[key[1:]]=item
#                            del hit[key]
#        else:
#            setattr(result, "total", 0)
#        return result
#    return _func
#
#def file_to_attachme
