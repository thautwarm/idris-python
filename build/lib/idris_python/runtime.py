"""
Some staging objects for compilations of common abstract machine.
"""
import operator
import numpy as np
import os

from functools import update_wrapper
from idris_python.idris_apis import make_funcs_from_session


def throw(e):
    raise Exception(e)


def write_str(io, a):
    print(a, end='', file=io)


def unsafe_call(f, args):
    return f(*args)


def get_runtime(link_session):
    dep = make_funcs_from_session(link_session)
    to_text = dep['to_text']
    from_text = dep['from_text']

    def pipe(_):
        return os.pipe()

    def after_str_then(f):
        def call(arg):
            return f(to_text(arg))

        return call

    def after_then_str(f):
        def call(arg):
            return from_text(f(arg))

        return call

    def cmp(x, y):
        return x == y

    return {
        'cam-rt.cmp': operator.eq,
        'cam-rt.is': operator.is_,
        'cam-rt.err': throw,
        'prim-plus': operator.add,
        'prim-minus': operator.sub,
        'prim-times': operator.mul,
        'prim-udiv': operator.floordiv,
        'prim-sdiv': operator.floordiv,
        'prim-urem': operator.mod,
        'prim-srem': operator.mod,
        'prim-eq': operator.eq,
        'prim-slt': operator.lt,
        'prim-sle': operator.le,
        'prim-sgt': operator.gt,
        'prim-sge': operator.ge,
        'prim-and': operator.
        and_,  # not sure the idris one is bitwise operation or logic operation.
        'prim-or': operator.or_,

        # STR METHOD1
        'prim-streq': dep['str_eq'],
        'prim-strlen': dep['str_len'],
        'prim-strindex': dep['str_index'],
        'prim-strlt': dep['str_lt'],

        # EFFECT
        "prim-external": throw,
        'prim-writestr': write_str,  # for supporting some rich consoles.
        'prim-readstr': input,

        # CONVERSION
        'prim-floatstr': after_then_str(str),
        'prim-strfloat': after_str_then(float),
        'prim-intstr': after_then_str(str),
        'prim-strint': after_str_then(int),
        'prim-intch': chr,
        'prim-chint': ord,
        # 'prim-sext': lambda x: x,
        # 'prim-zext': lambda x: x,

        # STR METHOD2
        'prim-strhead': dep['str_head'],
        'prim-strtail': dep['str_tail'],
        'prim-strcons': dep['str_cons'],
        'prim-strconcat': dep['str_concat'],
        'prim-crash': throw,

        # io
        "builtin-println": print,
        "builtin-simple_open": open,
        "builtin-simple_read": dep['read_all_text'],
        "builtin-filesystem_pipe": pipe,
        "builtin-filesystem_open_file": open,
        "builtin-filesystem_close_file": lambda f: f.close(),
        "builtin-filesystem_read_all_text": dep['read_all_text'],

        # flist
        "builtin-reverse_flist": dep['reverse_flist'],
        "builtin-flist_to_native": dep['from_flist'],
        "builtin-list_to_foreign": dep['to_flist'],

        # fvect
        "builtin-reverse_fvect": dep['reverse_fvect'],
        "builtin-fvect_to_native": dep['from_fvect'],
        "builtin-vect_to_foreign": dep['to_fvect'],

        # fhvect
        "builtin-reverse_fhvect": dep['reverse_fhvect'],
        "builtin-fhvect_to_native": dep['from_fhvect'],
        "builtin-hvect_to_foreign": dep['to_fhvect'],

        # string
        "builtin-to_text": str,
        "builtin-fstr_to_native": from_text,
        "builtin-str_to_foreign": to_text,
        "builtin-module_property": getattr,
        "builtin-get_module": dep['get_module'],
        "builtin-unsafe_call": unsafe_call,
        "builtin-identity": lambda x: x
    }
