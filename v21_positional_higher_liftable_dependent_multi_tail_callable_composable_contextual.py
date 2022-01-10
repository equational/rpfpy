"""
MIT License

Copyright (c) 2021 James Litsios

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from dataclasses import dataclass, fields, is_dataclass
from typing import Tuple, Any, Optional, Protocol, Union, Dict, List, Iterable, Iterator
from abc import abstractmethod
from copy import copy

class Call(Protocol):
    def __call__(self,
                 continuations: Optional['Continuations'],
                 *args,
                 **kwargs):
        pass


@dataclass(init=True, frozen=True)
class Continuation(Protocol):

    @abstractmethod
    def __call__(self, *args, fail: bool = False, **kwargs):
        assert False

    # def fail(self, *args, **kwargs):
    #     return self(*args, fail=True, **kwargs)


@dataclass(init=True, frozen=True)
class Continuations:
    continuations: Optional['Continuations']

    def __call__(self, *args, fail: bool = False, **kwargs):
        return self.next()(*args, fail=fail, **kwargs)

    def next_by_cls(self, cls) -> Optional['Continuations']:
        c = self.continuations
        while(c is not None and not isinstance(c, cls)):
            c = c.continuations
        return c

    def by_cls(self, cls) -> Optional['Continuations']:
        c = self
        while(c is not None and not isinstance(c, cls)):
            c = c.continuations
        return c

    def next(self) -> Optional['Continuations']:
        return self.next_by_cls(CallContinuations)


    def next_one(self) -> Optional['Continuations']:
        assert isinstance(self, CallContinuations)
        return self.continuations


    def copy_without_first_cls(self, cls) -> Optional['Continuations']:
        c = self.continuations
        while(c is not None and not isinstance(c, cls)):
            c = c.continuations
        return c


@dataclass(init=True, frozen=True)
class CallContinuations(Continuations, Continuation):
    pass



@dataclass(frozen=True, init=True)
class Call0(Call):
    def __call__(self, continuations: Optional['Continuations'], *args, **kwargs):
        return continuations(*args, **kwargs)

    def __mul__(self, g):
        return Call2(self, g)

    def __pow__(self, g):
        return Call2(g, self)


@dataclass(init=True, frozen=True)
class Call1(Call0):
    f: Call

    def __call__(self, continuations, *args, **kwargs):
        return self.f(continuations, *args, **kwargs)


@dataclass(init=True, frozen=True)
class Call2(Call1):
    g: Call

    def __call__(self, continuations, *args, **kwargs):
        return self.f(Continuation1(self.g, continuations), *args, **kwargs)



def mkc_k(k: str) -> Tuple[Call0, Call0]:
    d_k = eval(f"lambda self, continuations, *args, {k}, **kwargs:  continuations(*(({k},)+args), **kwargs)")
    c_k = eval(f"lambda self, continuations, *args, **kwargs: continuations(*args[1:], {k}=args[0], **kwargs)")
    d = type('D_'+k, (Call0,), {'tag': k, '__call__': d_k})
    c = type('C_'+k, (Call0,), {'tag': k, '__call__': c_k})
    return d(), c()


@dataclass(init=True, frozen=True)
class FailContinuation(CallContinuations):
    def __call__(self, *args, fail: bool = False, **kwargs):
        return super().__call__(*args, fail=True, **kwargs)


@dataclass(init=True, frozen=True)
class Continuation1(CallContinuations):
    continuation: Union[Call, object]

    def __init__(self, continuation, continuations=None):
        object.__setattr__(self, 'continuation', continuation)
        super().__init__(continuations)

    def __call__(self, *args, fail: bool = False, **kwargs):
        if not fail:
            return self.continuation(self.next_one(), *args, **kwargs)
        else:
            return self.continuation(FailContinuation(self.next_one()), *args, **kwargs)


@dataclass(init=True, frozen=True)
class OnSuccessOrFail(CallContinuations):
    succeed: Union[Call, object]
    fail: Union[Call, object]

    def __init__(self, succeed, continuations=None):
        object.__setattr__(self, 'succeed', succeed)
        super().__init__(continuations)

    def __call__(self, *args, fail: bool = False, **kwargs):
        if fail:
            return self.fail(self.next_one(), *args, **kwargs)
        else:
            return self.succeed(self.next_one(), *args, **kwargs)

@dataclass(init=True, frozen=True)
class OnSuccess(CallContinuations):
    succeed: Union[Call, object]

    def __init__(self, succeed, continuations=None):
        object.__setattr__(self, 'succeed', succeed)
        super().__init__(continuations)

    def __call__(self, *args, fail: bool = False, **kwargs):
        if not fail:
            return self.succeed(self.next_one(), *args, **kwargs)
        else:
            return super().__call__(*args, fail=fail, **kwargs)

@dataclass(init=True, frozen=True)
class OnFail(CallContinuations):
    fail_: Union[Call, object]

    def __init__(self, fail, continuations=None):
        object.__setattr__(self, 'fail_', fail)
        super().__init__(continuations)

    def __call__(self, *args, fail: bool = False, **kwargs):
        if fail:
            return self.fail_(self.next_one(), *args, **kwargs)
        else:
            return super().__call__(*args, fail=fail, **kwargs)



@dataclass(init=True, frozen=True)
class AKW_(CallContinuations):
    args: Any
    kwargs: Any

    def cocall(self, f):
        return f(self.next_one(), *self.args, **self.kwargs)


@dataclass(init=False, frozen=True)
class AKW(AKW_):
    def __init__(self, continuations, *args, **kwargs):
        super().__init__(continuations, args, kwargs)


@dataclass(init=True, frozen=True)
class Succeed(Call0):
    pass


@dataclass(init=True, frozen=True)
class Fail(Call0):
    def __call__(self, continuations, *args, **kwargs):
        return continuations(*args, fail=True, **kwargs)

@dataclass(init=True, frozen=True)
class Indexed(Continuations):
    index: int


def opt_index(self):
    opt = self.by_cls(Indexed)
    if opt is not None:
        return opt.index
    else:
        return None


setattr(Continuations, 'opt_index', opt_index)


@dataclass(init=True, frozen=True)
class FirstIter(Call0):
    disjunctions: Iterable[Tuple[int, Call]]

    @dataclass(init=True, frozen=True)
    class Iter(AKW_):
        iter_f:  Iterator[Tuple[int, Call]]

        def __call__(self, *args, fail: bool = False, **kwargs):
            if fail:
                copy_iter_f = copy(self.iter_f)
                try:
                    idx, f = next(copy_iter_f)
                except StopIteration:
                    return self.continuations(*args, fail=True, **kwargs)
                else:
                    return f(
                        Indexed(FirstIter.Iter(self.continuations, self.args, self.kwargs, copy_iter_f), idx),
                        *self.args,
                        **self.kwargs)

    def __call__(self, continuations: Optional['Continuations'], *args, **kwargs):
        first_iter_f = iter(enumerate(self.disjunctions))
        try:
            idx, f = next(first_iter_f)
        except StopIteration:
            return continuations(*args, fail=True, **kwargs)
        else:
            return f(
                Indexed(FirstIter.Iter(continuations, args, kwargs, first_iter_f), idx),
                *args,
                **kwargs)


@dataclass(init=False, frozen=True)
class First(FirstIter):
    def __init__(self, *args):
        super().__init__(args)

@dataclass(init=True, frozen=True)
class AllIter(Call0):
    adjunctions: Iterable[Tuple[int, Call]]

    @dataclass(init=True, frozen=True)
    class Iter(AKW_):
        iter_f:  Iterator[Call]

        def __call__(self, *args, fail: bool = False, **kwargs):
            if not fail:
                copy_iter_f = copy(self.iter_f)
                try:
                    idx, f = next(copy_iter_f)
                except StopIteration:
                    return self.continuations(*args, **kwargs)
                else:
                    return f(
                        Indexed(AllIter.Iter(self.continuations, self.args, self.kwargs, copy_iter_f), idx),
                        *self.args,
                        **self.kwargs)
            else:
                return super().__call__(*args, fail=fail, **kwargs)

    def __call__(self, continuations: Optional['Continuations'], *args, **kwargs):
        all_iter_f = iter(enumerate(self.adjunctions))
        try:
            idx, f = next(all_iter_f)
        except StopIteration:
            return continuations(*args, fail=True, **kwargs)
        else:
            return f(
                Indexed(AllIter.Iter(continuations, args, kwargs, all_iter_f), idx),
                *args,
                **kwargs)


@dataclass(init=False, frozen=True)
class All(AllIter):
    def __init__(self, *args):
        super().__init__(args)


@dataclass(init=True, frozen=True)
class Call1(Call0):
    f: Call

    def __call__(self, continuations, *args, **kwargs):
        return self.f(continuations, *args, **kwargs)


@dataclass(init=True, frozen=True)
class Call2(Call1):
    g: Call

    def __call__(self, continuations, *args, **kwargs):
        return self.f(OnSuccess(self.g, continuations), *args, **kwargs)


t01 = First(Succeed())(OnSuccess(AKW), "ok")
t02 = First(Fail(), Succeed())(OnSuccess(AKW), "ok")
print(t01)
print(t02)

@dataclass(init=True, frozen=True)
class FAKW(AKW_):
    def __init__(self, *args, continuations=None, **kwargs):
        super().__init__(continuations, args, kwargs)


t03 = First(Fail())(OnSuccess(AKW, OnFail(FAKW)), "ok")
t04 = First(Fail(), Fail())(OnSuccess(AKW, OnFail(FAKW)), "ok")
print(t03)
print(t04)


t05 = All(Succeed())(OnSuccess(AKW), "ok")
t06 = All(Succeed(), Succeed())(OnSuccess(AKW), "ok")
print(t05)
print(t06)

t07 = All(Fail())(OnSuccess(AKW, OnFail(FAKW)), "ok")
t08 = All(Succeed(), Fail())(OnSuccess(AKW, OnFail(FAKW)), "ok")
print(t07)
print(t08)

@dataclass(init=True, frozen=True)
class InvertLogic(CallContinuations):
    def __call__(self, *args, fail: bool = False, **kwargs):
        return self.continuations(*args, fail=not fail, **kwargs)


@dataclass(init=True, frozen=True)
class Fails(Call1):
    def __call__(self, continuations: Optional['Continuations'], *args, **kwargs):
        return self.f(InvertLogic(continuations), *args, **kwargs)


t09 = Fails(First(Fails(Succeed()), Fail()))(OnSuccess(AKW), "ok")
t10 = Fails(First(Fail(), Succeed()))(OnSuccess(AKW, OnFail(FAKW)), "ok")
t11 = Fails(First(Fail(), Fail()))(OnSuccess(AKW, OnFail(FAKW)), "ok")
print(t09)
print(t10)
print(t11)

@dataclass(init=True, frozen=True)
class AllApplyN1(Call0):
    adjunctions: Iterable[Tuple[int, Call]]

    @dataclass(init=True, frozen=True)
    class Apply(AKW_):
        iter_f:  Iterator[Call]

        def __call__(self, first, *args, fail: bool = False, **kwargs):
            if not fail:
                copy_iter_f = copy(self.iter_f)
                try:
                    idx, f = next(copy_iter_f)
                except StopIteration:
                    return [first]
                else:
                    others = f(
                        Indexed(AllApplyN1.Apply(self.continuations, self.args, self.kwargs, copy_iter_f), idx),
                        *self.args,
                        **self.kwargs)
                    others.append(first)
                    return others
            else:
                return super().__call__(*args, fail=fail, **kwargs)

    def __call__(self, continuations: Optional['Continuations'], *args, **kwargs):
        all_iter_f = iter(enumerate(self.adjunctions))
        try:
            idx, f = next(all_iter_f)
        except StopIteration:
            return continuations(*args, fail=True, **kwargs)
        else:
            others = f(
                Indexed(AllApplyN1.Apply(continuations, args, kwargs, all_iter_f), idx),
                *args,
                **kwargs)
            result = self.adjunctions.__class__(reversed(others))
            return continuations(result, *args[1:], **kwargs)


@dataclass(init=False, frozen=True)
class AllN1(AllApplyN1):
    def __init__(self, *args):
        super().__init__(args)


t12 = AllN1(Succeed(), Succeed())(OnSuccess(AKW), "ok")
print(t12)

class Inc(Call0):
    def __call__(self, continuations, *args, **kwargs):
        return continuations(args[0]+1, *args[1:], **kwargs)


class Dec(Call0):
    def __call__(self, continuations, *args, **kwargs):
        return continuations(args[0]-1, *args[1:], **kwargs)

dec, inc = Dec(), Inc()

t13 = AllN1(inc, dec)(OnSuccess(AKW), 0)
print(t13.args)

@dataclass(init=True, frozen=True)
class SelectApplyN1(Call0):
    disjunctions: Iterable[Tuple[int, Call]]

    @dataclass(init=True, frozen=True)
    class Apply(AKW_):
        iter_f:  Iterator[Call]

        def __call__(self, first, *args, fail: bool = False, **kwargs):
            if not fail:
                copy_iter_f = copy(self.iter_f)
                try:
                    idx, f = next(copy_iter_f)
                except StopIteration:
                    return [first]
                else:
                    others = f(
                        Indexed(SelectApplyN1.Apply(self.continuations, self.args, self.kwargs, copy_iter_f), idx),
                        *self.args,
                        **self.kwargs)
                    others.append(first)
                    return others
            else:
                copy_iter_f = copy(self.iter_f)
                try:
                    idx, f = next(copy_iter_f)
                except StopIteration:
                    return []
                else:
                    others = f(
                        Indexed(SelectApplyN1.Apply(self.continuations, self.args, self.kwargs, copy_iter_f), idx),
                        *self.args,
                        **self.kwargs)
                    return others

    def __call__(self, continuations: Optional['Continuations'], *args, **kwargs):
        select_iter_f = iter(enumerate(self.disjunctions))
        try:
            idx, f = next(select_iter_f)
        except StopIteration:
            return continuations(*args, fail=True, **kwargs)
        else:
            others = f(
                Indexed(SelectApplyN1.Apply(continuations, args, kwargs, select_iter_f), idx),
                *args,
                **kwargs)
            result = self.disjunctions.__class__(reversed(others))
            return continuations(result, *args[1:], **kwargs)

@dataclass(init=False, frozen=True)
class SelectN1(SelectApplyN1):
    def __init__(self, *args):
        super().__init__(args)




@dataclass(init=True, frozen=True)
class Above(Call0):
    value: int
    def __call__(self, continuations, *args, **kwargs):
        if self.value > args[0]:
            return continuations((self.value, args[0], continuations.opt_index()), *args[1:], **kwargs)
        else:
            return continuations(*args, fail=True, **kwargs)


t14 = SelectN1(Above(3))(OnSuccess(AKW, OnFail(FAKW)), 5)
t15 = SelectN1(Above(3))(OnSuccess(AKW, OnFail(FAKW)), 2)
t16 = SelectN1(Above(3), Above(5), Above(7), Above(8))(OnSuccess(AKW, OnFail(FAKW)), 6)

print(t14.args)
print(t15.args)
print(t16.args)

t17 = SelectApplyN1((Above(3), Above(5), Above(7), Above(8)))(OnSuccess(AKW, OnFail(FAKW)), 6)

print(t17.args)

@dataclass(init=True, frozen=True)
class MKAKW(Call):

    def __call__(self, continuations: Optional['Continuations'], *args, **kwargs):
        return AKW(continuations, *args, **kwargs)


@dataclass(init=True, frozen=True)
class Assorted(Continuations):
    pass


def opt_assorted(self):
    opt = self.by_cls(Assorted)
    if opt is not None:
        return opt
    else:
        return None

setattr(Continuations, 'opt_assorted', opt_assorted)

@dataclass(init=True, frozen=True)
class Keyed(Continuations):
    key: Any


def opt_keyed(self):
    opt = self.by_cls(Keyed)
    if opt is not None:
        return opt.key
    else:
        return None

setattr(Continuations, 'opt_keyed', opt_keyed)


@dataclass(init=True, frozen=True)
class RMap(Call1):

    def __call__(self, continuations, first_mappable, *args, **kwargs):
        def lowered(extend_continuations, element):
            return (self(OnSuccess(AKW, extend_continuations(continuations)), element, *args, **kwargs)).args[0]

        if isinstance(first_mappable, (dict,)):
            first_mapped = {k: lowered(lambda cs: Keyed(cs, k), v) for k, v in first_mappable.items()}
        elif isinstance(first_mappable, (tuple,)):
            first_mapped = tuple([lowered(lambda cs: Indexed(cs, i), v) for i, v in enumerate(first_mappable)])
        elif isinstance(first_mappable, (list,)):
            first_mapped = [lowered(lambda cs: Indexed(cs, i), v) for i, v in enumerate(first_mappable)]
        elif isinstance(first_mappable, (set,)):
            first_mapped = set([lowered(lambda cs: Assorted(cs), v) for v in first_mappable])
        elif is_dataclass(first_mappable):
            first_mapped = first_mappable.__class__(**{field.name: lowered(lambda cs: Keyed(cs, field.name),
                                                                           getattr(first_mappable, field.name))
                                                       for field in fields(first_mappable)})
        else:
            return self.f(continuations, first_mappable, *args, **kwargs)
        return continuations(first_mapped, *args, **kwargs)

@dataclass(init=True, frozen=True)
class Pair:
    first: Any
    second: Any


d_k1, c_k1 = mkc_k('k1')

print((d_k1*RMap(inc)*c_k1)(OnSuccess(AKW, OnFail(FAKW)), 'a', 'b', k1=[1,[2, 3]], k2=2))
print((d_k1*RMap(inc)*c_k1*d_k1*RMap(dec)*c_k1)(OnSuccess(AKW, OnFail(FAKW)), 'a', 'b', k1=[1,[2, 3]], k2=2))
print((d_k1*RMap(inc*inc)*c_k1)(OnSuccess(AKW, OnFail(FAKW)), 'a', 'b', k1=Pair(1, Pair(2, 3)), k2=2))


@dataclass(init=True, frozen=True)
class Parented(Continuations):
    parent: Continuations


def opt_parent(self):
    opt = self.by_cls(Parented)
    if opt is not None:
        return opt.parent
    else:
        return None

setattr(Continuations, 'opt_parent', opt_parent)

@dataclass(init=True, frozen=True)
class RMap2(Call1):

    def __call__(self, continuations, first_mappable, *args, **kwargs):
        def lowered(extend_continuations, element):
            akw = (self(OnSuccess(AKW, extend_continuations(continuations)), element, *args, **kwargs))
            return akw.args[0]

        if isinstance(first_mappable, (dict,)):
            first_mapped = {k: lowered(lambda cs: Parented(continuations, Keyed(cs, k)), v) for k, v in first_mappable.items()}
        elif isinstance(first_mappable, (tuple,)):
            first_mapped = tuple([lowered(lambda cs: Parented(continuations, Indexed(cs, i)), v) for i, v in enumerate(first_mappable)])
        elif isinstance(first_mappable, (list,)):
            first_mapped = [lowered(lambda cs: Parented(continuations, Indexed(cs, i)), v) for i, v in enumerate(first_mappable)]
        elif isinstance(first_mappable, (set,)):
            first_mapped = set([lowered(lambda cs: Parented(continuations, Assorted(cs)), v) for v in first_mappable])
        elif is_dataclass(first_mappable):
            first_mapped = first_mappable.__class__(**{field.name: lowered(lambda cs: Parented(continuations, Keyed(cs, field.name)),
                                                                           getattr(first_mappable, field.name))
                                                       for field in fields(first_mappable)})
        else:
            return self.f(continuations, first_mappable, *args, **kwargs)
        return continuations(first_mapped, *args, **kwargs)


def depth(continuations):
    count = 0
    continuations = continuations.opt_parent()
    while(continuations is not None):
        count += 1
        continuations = continuations.opt_parent()
    return count

@dataclass(init=True, frozen=True)
class Annotate(Call0):
    def __call__(self, continuations, *args, **kwargs):
        return continuations((args[0], depth(continuations)), *args[1:], **kwargs)

annotate = Annotate()

print((d_k1*RMap2(inc*annotate)*c_k1)(OnSuccess(AKW, OnFail(FAKW)), 'a', 'b', k1=[1,[2, 3]], k2=2))
print((d_k1*RMap2(inc)*c_k1*d_k1*RMap2(dec*annotate)*c_k1)(OnSuccess(AKW, OnFail(FAKW)), 'a', 'b', k1=[1,[2, 3]], k2=2))
print((d_k1*RMap2(inc*inc*annotate)*c_k1)(OnSuccess(AKW, OnFail(FAKW)), 'a', 'b', k1=Pair(1, Pair(2, 3)), k2=2))

d_k2, c_k2 = mkc_k('k2')
print((d_k2*inc*annotate*c_k2)(OnSuccess(AKW, OnFail(FAKW)), 'a', 'b', k1=Pair(1, Pair(2, 3)), k2=2))



print(" ")