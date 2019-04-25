from typing import *
from idris_python.abstract_machine import *
from idris_python.idris_apis import IdrisStr
import json


def list_conv(xs):
    return list(map(aeson_to_ir, xs))


def com_let(cs):
    return Let(cs[0], aeson_to_ir(cs[1]), aeson_to_ir(cs[2]))


def com_letrec(cs):
    return LetRec([(fst, aeson_to_ir(snd)) for [fst, snd] in cs[0]],
                  aeson_to_ir(cs[1]))


def com_if(cs):
    return If(*list_conv(cs))


def com_while(cs):
    return While(*list_conv(cs))


def com_mutate(cs):
    return Mutate(Var(cs[0]), aeson_to_ir(cs[1]))


def com_fun(cs):
    return Fun(cs[0], aeson_to_ir(cs[1]))


def com_app(cs):
    return App(aeson_to_ir(cs[0]), list_conv(cs[1]))


def com_var(cs):
    return Var(cs)


def com_block(cs):
    return BlockExpr(list_conv(cs))


def com_tuple(cs):
    return DataStructure.Tuple(list_conv(cs))


def com_proj(cs):
    return Proj(*list_conv(cs))


def com_const(cs):
    return Const(cs)


def com_internal(cs):
    return Link(cs)


def com_ch(cs):
    return Const(cs)


def com_str(cs):
    s = eval(repr(cs).replace(r'\\', '\\'))
    ret = ()
    wrap = IdrisStr
    for each in s[::-1]:
        ret = wrap((each, ret))
    return Staged(ret)


def com_sym(cs):
    return Symbol(cs)


def com_float(c):
    return Const(float(c))


switch = {
    'ComLet': com_let,
    'ComLetrec': com_letrec,
    'ComIf': com_if,
    'ComWhile': com_while,
    'ComMutate': com_mutate,
    'ComFun': com_fun,
    'ComApp': com_app,
    'ComVar': com_var,
    'ComBlock': com_block,
    'ComTuple': com_tuple,
    'ComProj': com_proj,
    'ComSymbol': com_sym,
    'ComInt': com_const,
    'ComBigInt': com_const,
    'ComDouble': com_float,
    'ComCh': com_const,
    'ComBool': com_const,
    'ComStr': com_str,
    'ComNil': None,
    'ComInternal': com_internal
}


def aeson_to_ir(d, switch=switch):
    action = switch[d['tag']]
    if not action:  # ComNil
        return Const(None)
    contents = d['contents']

    return action(contents)
