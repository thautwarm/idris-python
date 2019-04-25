"""
A common abstract machine implemented in Python side
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import *
from enum import Enum
from toolz import compose
from idris_python.runtime import get_runtime
import ast
import operator
import copy

T = TypeVar('T')


class AST:
    def __getitem__(self, item: AST):
        return App(Staged(operator.getitem), [self, item])

    def set(self, item: AST, value: AST):
        return App(Staged(operator.setitem), [self, item, value])

    def __call__(self, *args: AST):
        return App(self, list(args))

    def __add__(self, other: AST):
        return App(Staged(operator.add), [self, other])

    def __sub__(self, other: AST):
        return App(Staged(operator.sub), [self, other])

    def __truediv__(self, other: AST):
        return App(Staged(operator.truediv), [self, other])

    def __mul__(self, other: AST):
        return App(Staged(operator.mul), [self, other])


def print_io(io, *args):
    print(*args, end='', file=io)


@dataclass
class If(AST):
    cond: Constructs
    t_br: Constructs
    f_br: Constructs

    def dump(self, indent, io):
        print_io(io, 'if ')
        i1 = self.cond.dump(indent + 3, io)
        print_io(io, '\n', ' ' * (indent + 3))
        i2 = self.t_br.dump(indent + 4, io)
        print_io(io, '\n', ' ' * indent, 'else ', '\n', ' ' * (indent + 4))
        i3 = self.f_br.dump(indent + 4, io)
        return max(i1, i2, i3)


@dataclass
class While(AST):
    cond: Constructs
    body: Constructs

    def dump(self, indent, io):
        print_io(io, 'while ')
        i1 = self.cond.dump(indent + 5, io)
        print_io(io, '\n', ' ' * (indent + 4))
        i2 = self.body.dump(indent + 4, io)
        return max(i1, i2)


@dataclass
class Fun(AST):
    args: List[str]
    body: Constructs

    def dump(self, indent, io):
        print_io(io, 'fun ')
        args = self.args
        print_io(io, ', '.join(args))

        i = indent + 5 + sum(map(len, args)) + 2 * max(len(args) - 1, 0)
        print_io(io, ' -> ')
        i += 3
        if i < 35:
            return self.body.dump(i, io)

        print_io(io, '\n', ' ' * (indent + 4))
        return self.body.dump(indent + 4, io)

@dataclass
class Link(AST):
    name: str

    def dump(self, indent, io):
        s = f'link + {self.name}'
        print_io(io, s)
        return indent + len(s)

@dataclass
class App(AST):
    fn: Constructs
    args: List[Constructs]

    def dump(self, indent, io):
        i = self.fn.dump(indent, io)
        args = iter(self.args)
        i += 1
        print_io(io, '(')
        for arg in args:
            i = arg.dump(i, io)
            print_io(io, ', ')
            i += 2
        print_io(io, ')')
        i += 1
        return i




@dataclass
class Var(AST):
    name: str

    def dump(self, _, io):
        print_io(io, self.name)
        return len(self.name)


@dataclass
class Let(AST):
    bind: str
    expr: Constructs
    body: Constructs

    def dump(self, indent, io):
        print_io(io, 'let ', self.bind, ' = ')
        i = indent + 7 + len(self.bind)
        if i < 40:
            i = self.expr.dump(i, io)
        else:
            print_io(io, '\n', ' ' * (indent + 4))
            i = self.expr.dump(indent + 4, io)

        if i + 4 < 40:
            print_io(io, ' in ')
            j = self.body.dump(i + 4, io)
        else:
            print_io(io, '\n', ' ' * (indent + 4), ' in ')
            j = self.body.dump(indent + 8, io)

        return max(i, j)


@dataclass
class LetRec(AST):
    seqs: List[Tuple[str, Constructs]]
    body: Constructs

    def dump(self, indent, io):
        print_io(io, 'let rec')
        inds = []
        app = inds.append

        for k, v in self.seqs:
            print_io(io, '\n', ' ' * (indent + 4), k, ' = ')
            i = indent + 4 + len(k) + 3
            if i < 40:
                i = v.dump(i, io)
            else:
                print_io(io, '\n', ' ' * (indent + 8))
                i = max(i, v.dump(indent + 8, io))
            app(i)

        return max(inds)


@dataclass
class BlockExpr(AST):
    seq: List[Constructs]

    def dump(self, indent, io):
        print_io(io, '{')

        def gen():
            for each in self.seq:
                print_io(io, '\n', ' ' * (indent + 2))
                yield each.dump(indent + 2, io)

        ret = max(gen())
        print_io(io, '\n', ' ' * indent, '}')
        return ret


class DataStructure:
    @dataclass
    class Tuple(AST):
        elts: List[Constructs]

        def dump(self, indent, io):
            print_io(io, '(')
            i = indent + 1
            for elt in self.elts:
                i = elt.dump(i, io)
                print_io(io, ', ')
                i += 2
            print_io(io, ')')
            return i + 1

    @dataclass
    class List(AST):
        elts: List[Constructs]

        def dump(self, indent, io):
            print_io(io, '[')
            i = indent + 1
            for elt in self.elts:
                i = elt.dump(i, io)
                print_io(io, ', ')
                i += 2
            print_io(io, ']')
            return i + 1


@dataclass
class Const(AST):
    value: object

    def dump(self, indent, io):
        s = repr(self.value)
        print_io(io, s)
        return len(s) + indent


@dataclass
class Mutate(AST):
    target: Constructs
    value: Constructs

    def dump(self, indent, io):
        i = self.target.dump(indent, io)
        print_io(io, ' <- ')
        i += 4
        return self.value.dump(i, io)


@dataclass
class Staged(AST):
    value: object

    def dump(self, indent, io):
        s = repr(self.value)
        print_io(io, s)
        return len(s) + indent


@dataclass
class Location:
    lineno: int
    col_offset: int

    def update(self, node):
        node.lineno = self.lineno
        node.col_offset = self.col_offset
        return node


@dataclass
class Proj(AST):
    major: Constructs
    ith: Constructs

    def dump(self, indent, io):
        i = self.major.dump(indent, io)
        print_io(io, ' # ')
        i += 3
        return self.ith.dump(i, io)

@dataclass
class Symbol(AST):
    v: str

    def dump(self, indent, io):
        v = self.v
        print_io(io, ":", v)
        return len(v) + 1 + indent

@dataclass
class Located(AST):
    loc: Location
    decorated: Constructs

    def dump(self, indent, io):
        self.decorated.dump(indent, io)


class Ref(Generic[T]):
    def __init__(self, i: T):
        self.i = i

    def get_name(self):
        name = f"_{self.i}"
        self.i += 1
        return name

@dataclass
class Inspect(AST):

    def dump(self, i, io):
        print_io(io, '[inspect]')
        return i + 9


class Builder:
    @staticmethod
    def branch(r1: Register, block1: List, block2: List, loc: Location):
        return loc.update(ast.If(r1.to_ast(), block1, block2))

    @staticmethod
    def loop(r1: Register, block: List, loc: Location):
        return loc.update(ast.While(r1.to_ast(), block, None))

    @staticmethod
    def make_fn(name: str, args: List[str], block, loc: Location):
        return loc.update(
            ast.FunctionDef(
                name=name,
                args=ast.arguments(
                    args=[ast.arg(arg=each, annotation=None) for each in args],
                    vararg=None,
                    kwonlyargs=[],
                    kw_defaults=[],
                    kwarg=None,
                    defaults=[],
                ),
                body=block,
                decorator_list=[],
                returns=None,
            ))

    @staticmethod
    def call(f: Register, args: List[Register], loc: Location):
        return loc.update(
            ast.Call(
                func=f.to_ast(),
                args=[arg.to_ast() for arg in args],
                keywords=[]))

    @staticmethod
    def proj(major: Register, ith: Register, loc: Location):
        return loc.update(
            ast.Subscript(
                value=major.to_ast(),
                slice=ast.Index(ith.to_ast()),
                ctx=ast.Load()))


class RegisterType(Enum):
    Constant = 0
    Mutable = 1
    Readonly = 2


@dataclass
class Register:
    name: Union[str, object]
    type: RegisterType

    def to_ast(self):
        if self.type is RegisterType.Constant:
            return ast.Constant(self.name)
        return ast.Name(self.name, ctx=ast.Load())

    def assign(self, reg: Register):
        if self.type is RegisterType.Mutable:
            return ast.Assign([ast.Name(self.name, ctx=ast.Store())],
                              reg.to_ast())

        raise IOError("Readonly")

    def assign_ast(self, node: ast.expr):
        if self.type is RegisterType.Mutable:
            return ast.Assign([ast.Name(self.name, ctx=ast.Store())], node)
        raise IOError("Readonly")


@dataclass
class Scope:
    loc: Location

    prefix: str
    count: Ref[int]
    bounds: Dict[str, Register]
    freevars: Dict[str, Register]

    py_bounds: Set[str]
    py_freevars: Set[str]
    py_used_freevars: Set[str]

    code: List

    def get_var(self, n):
        ret = self.bounds.get(n)

        if not ret:
            # freevars in this language must be also python freevars
            ret = self.freevars.get(n)
            if not ret:
                raise NameError(n)
            ret_name = ret.name
            if ret_name in self.py_freevars:
                self.py_used_freevars.add(ret_name)

        if not ret:
            raise NameError(n)

        return ret

    def new_name(self):
        return f"{self.prefix}{self.count.get_name()}"

    @classmethod
    def global_ctx(cls, prefix):
        return Scope(
            Location(1, 1), prefix, Ref(0), {}, {}, set(), set(), set(), [])

    def enter_function(self, name=None):
        # As the adoption of lexical scope, available `py_freevars` are always declared before referencing,
        # which does remove the mental burden for user side and compiler side
        return Scope(self.loc, (name or '') + self.new_name(), Ref(0), {}, {
            **self.freevars,
            **self.bounds
        }, set(), {*self.py_freevars, *self.py_bounds}, set(), [])

    def enter(self, name=None):
        return Scope(self.loc, (name or '') + self.new_name(), Ref(0), {}, {
            **self.freevars,
            **self.bounds
        }, self.py_bounds, self.py_freevars, self.py_used_freevars, [])

    def const_register(self, value):
        return Register(value, RegisterType.Constant)

    def new_register(self, name: str = '', readonly=False):
        reg_name = name or self.new_name()
        reg = Register(
            reg_name,
            RegisterType.Readonly if readonly else RegisterType.Mutable)
        self.py_bounds.add(reg_name)
        return reg


class _Symbol:
    def __init__(self, s):
        self.s = s

    def __getitem__(self, i):
        if i is 0:
            return self
        raise RuntimeError("internal runtime error")

    def __repr__(self):
        return self.s


class LinkSession:
    syms: Dict[str, _Symbol]
    rt: dict

    def __init__(self):
        self.syms = {}
        self.rt = get_runtime(self)

    def __getitem__(self, s):
        sym = self.syms.get(s, None)
        if sym is None:
            sym = self.syms[s] = _Symbol(s)
        return sym

def run_code(node, link_session: LinkSession = None):
    link_session = link_session or LinkSession()
    lit_ids = {}

    def inner(n: Constructs, ctx: Scope):
        if isinstance(n, Var):
            return ctx.get_var(n.name)

        if isinstance(n, Located):
            ctx.loc = n.loc
            return inner(n.decorated, ctx)
        cur_loc = ctx.loc

        if isinstance(n, Link):
            value = link_session.rt[n.name]
            key = value, type(value)
            if key not in lit_ids:
                name = lit_ids[key] = f"lit_{len(lit_ids)}"
            else:
                name = lit_ids[key]

            return ctx.new_register(name)

        if isinstance(n, Inspect):
            return ctx.const_register(ctx.prefix)

        if isinstance(n, Proj):
            major = inner(n.major, ctx)
            ith = inner(n.ith, ctx)

            v = ctx.new_register()
            ctx.code.append(v.assign_ast(Builder.proj(major, ith, cur_loc)))
            return v

        if isinstance(n, If):
            cond = inner(n.cond, ctx)
            ret = ctx.new_register()

            new_ctx1 = ctx.enter()
            v1 = inner(n.t_br, new_ctx1)

            new_ctx2 = ctx.enter()
            v2 = inner(n.f_br, new_ctx2)

            new_ctx1.code.append(ret.assign(v1))
            new_ctx2.code.append(ret.assign(v2))

            ctx.code.append(
                Builder.branch(cond, new_ctx1.code, new_ctx2.code, cur_loc))
            return ret

        if isinstance(n, Let):
            new_ctx = ctx.enter()
            v = inner(n.expr, new_ctx)

            ctx.code.extend(new_ctx.code)
            ctx.bounds[n.bind] = v

            new_ctx = ctx.enter()
            ret = inner(n.body, new_ctx)
            ctx.code.extend(new_ctx.code)

            return ret

        if isinstance(n, Symbol):
            sym = link_session[n.v]
            return inner(Staged(sym), ctx)

        if isinstance(n, Mutate):
            target = inner(n.target, ctx)
            value = inner(n.value, ctx)
            f = compose(ctx.code.append, cur_loc.update, target.assign_ast)
            f(value.to_ast())
            return target

        if isinstance(n, While):
            cond = inner(n.cond, ctx)
            new_ctx = ctx.enter()
            inner(n.body, new_ctx)
            ctx.code.append(Builder.loop(cond, new_ctx.code, cur_loc))
            return ctx.const_register(None)

        if isinstance(n, Fun):
            fn_name = ctx.new_name()
            new_ctx = ctx.enter_function(''.join(n.args))
            args_map = [(each, new_ctx.new_register()) for each in n.args]
            new_ctx.bounds.update(dict(args_map))
            fn_ret = inner(n.body, new_ctx)

            f = compose(new_ctx.code.append, new_ctx.loc.update, ast.Return)
            f(fn_ret.to_ast())

            code_block = new_ctx.code
            py_used_freevars = new_ctx.py_used_freevars

            if py_used_freevars:
                code_block = [
                    ast.Nonlocal(list(py_used_freevars)), *code_block
                ]

            ctx.code.append(
                Builder.make_fn(fn_name, [v.name for _, v in args_map],
                                code_block, cur_loc))

            return ctx.new_register(fn_name)

        if isinstance(n, Staged):
            value = n.value
            key = value, type(value)
            try:
                if key not in lit_ids:
                    name = lit_ids[key] = f"lit_{len(lit_ids)}"
                else:
                    name = lit_ids[key]
            except RecursionError as e:
                print(link_session.rt['prim-strlen'](key[0]))
                raise e
            return ctx.new_register(name)

        if isinstance(n, App):
            f = inner(n.fn, ctx)
            args = [inner(each, ctx) for each in n.args]

            ret = ctx.new_register()
            ctx.code.append(ret.assign_ast(Builder.call(f, args, cur_loc)))
            return ret

        if isinstance(n, BlockExpr):
            seq = iter(n.seq)
            elt = next(seq, None)
            if not elt:
                return ctx.const_register(None)

            new_ctx = ctx.enter()
            ret = inner(elt, new_ctx)

            for elt in seq:
                ret = inner(elt, new_ctx)

            ctx.code.extend(new_ctx.code)
            return ret

        if isinstance(n, DataStructure.List):
            elts = [inner(elt, ctx).to_ast() for elt in n.elts]
            reg = ctx.new_register()
            lst = ast.List(elts=elts, ctx=ast.Load())
            cur_loc.update(lst)
            ctx.code.append(reg.assign_ast(lst))
            return reg

        if isinstance(n, DataStructure.Tuple):
            elts = [inner(elt, ctx).to_ast() for elt in n.elts]
            reg = ctx.new_register()
            tp = ast.Tuple(elts=elts, ctx=ast.Load())
            cur_loc.update(tp)
            ctx.code.append(reg.assign_ast(tp))
            return reg

        if isinstance(n, Const):
            return ctx.const_register(n.value)

        if isinstance(n, LetRec):
            names: Dict[str, Register] = {
                name: ctx.new_register()
                for name, _ in n.seqs
            }
            ctx.bounds.update(names)
            new_ctxs = [ctx.enter(name if isinstance(v, Fun) else None)for name, v in n.seqs]

            for i, (name, expr) in enumerate(n.seqs):
                new_ctx = new_ctxs[i]
                reg = inner(expr, new_ctx)
                ctx.code.extend(new_ctx.code)
                assign = names[name].assign(reg)
                cur_loc.update(assign)
                ctx.code.append(assign)

            return inner(n.body, ctx)

        raise TypeError(n)

    ctx = Scope.global_ctx(prefix='x')
    init_loc = ctx.loc

    v = inner(node, ctx)
    ctx.code.append(ast.Return(v.to_ast()))

    def_main = Builder.make_fn("main", list(lit_ids.values()), ctx.code,
                               init_loc)
    top_ast = ast.Module([def_main])
    ast.fix_missing_locations(top_ast)

    scope = {}
    exec(compile(top_ast, "<codegen>", "exec"), scope)
    return scope['main'](*(v for (v, typ_of_v) in lit_ids.keys()))


def where(body: Union[AST, List[AST]], **kwargs: AST):
    n = len(kwargs)
    if n is 0:
        raise TypeError

    body = BlockExpr(body) if isinstance(body, list) else body

    if n is 1:
        [(k, v)] = kwargs.items()
        return Let(k, v, body)

    # I don't why `list(kwargs.items())` failed for static checking here. Marked.
    return LetRec([(k, v) for k, v in kwargs.items()], body)


class _FunctionMaker:
    def __init__(self, *args: Var):
        self.args = [arg.name for arg in args]

    def __getitem__(self, item: Union[AST, Tuple[AST, ...]]):
        if not isinstance(item, tuple):
            return Fun(self.args, item)
        return Fun(self.args, BlockExpr(list(item)))


fn = _FunctionMaker

Constructs = Union[If, While, Fun, Var, Let, Staged, LetRec, App, Const,
                   Mutate, BlockExpr, DataStructure.List, DataStructure.
                   Tuple, Located, Proj, Link]

