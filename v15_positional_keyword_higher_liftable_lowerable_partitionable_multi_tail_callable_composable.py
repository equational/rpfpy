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

from dataclasses import dataclass
from typing import Tuple, Any, Optional, Protocol, Union, Dict, Iterable, Iterator
from collections.abc  import Mapping, MappingView
from copy import copy

class Call(Protocol):
    def __call__(self, *args, continuations: Optional['Continuations'], **kwargs):
        pass

@dataclass(init=True, frozen=True)
class Continuations:
    continuations: Optional['Continuations']

    def __call__(self, *args, **kwargs):
        return self.continuations(*args, **kwargs)

    def fail(self, *args, **kwargs):
        return self.continuations.fail(*args, **kwargs)



@dataclass(init=True, frozen=True)
class OnSuccess(Continuations):
    succeed: Union[Call, object]

    def __init__(self, succeed, continuations=None):
        object.__setattr__(self, 'succeed', succeed)
        super().__init__(continuations)

    def __call__(self, *args, **kwargs):
        return self.succeed(*args, continuations=self.continuations, **kwargs)

@dataclass(init=True, frozen=True)
class OnFail(Continuations):
    fail_: Union[Call, object]

    def __init__(self, fail, continuations=None):
        object.__setattr__(self, 'fail_', fail)
        super().__init__(continuations)

    def fail(self, *args, **kwargs):
        return self.fail_(*args, continuations=self.continuations, **kwargs)

@dataclass(init=True, frozen=True)
class AKW_(Continuations):
    args: Any
    kwargs: Any

    def cocall(self, f):
        return f(*self.args, continuations=self.continuations, **self.kwargs)


@dataclass(init=False, frozen=True)
class AKW(AKW_):
    def __init__(self, *args, continuations=None, **kwargs):
        super().__init__(continuations, args, kwargs)


@dataclass(frozen=True, init=True)
class Call0(Call):
    def __call__(self, *args, continuations: Optional['Continuations'], **kwargs):
        return continuations(*args, **kwargs)

    def __mul__(self, g):
        return Call2(self, g)

    def __pow__(self, g):
        return Call2(g, self)


@dataclass(init=True, frozen=True)
class Succeed(Call0):
    pass


@dataclass(init=True, frozen=True)
class Fail(Call0):
    def __call__(self, *args, continuations: Optional['Continuations'], **kwargs):
        return continuations.fail(*args, **kwargs)


@dataclass(init=True, frozen=True)
class FirstIter(Call0):
    disjunctions: Iterable[Call]

    @dataclass(init=True, frozen=True)
    class Iter(AKW_):
        iter_f:  Iterator[Call]

        def fail(self, *args, **kwargs):
            copy_iter_f = copy(self.iter_f)
            try:
                f = next(copy_iter_f)
            except StopIteration:
                return self.continuations.fail(*args, **kwargs)
            else:
                return f(
                    *self.args,
                    continuations=FirstIter.Iter(self.continuations, self.args, self.kwargs, copy_iter_f),
                    **self.kwargs)

    def __call__(self, *args, continuations: Optional['Continuations'], **kwargs):
        first_iter_f = iter(self.disjunctions)
        try:
            f = next(first_iter_f)
        except StopIteration:
            return continuations.fail(*args, **kwargs)
        else:
            return f(
                *args,
                continuations=FirstIter.Iter(continuations, args, kwargs, first_iter_f),
                **kwargs)


@dataclass(init=False, frozen=True)
class First(FirstIter):
    def __init__(self, *args):
        super().__init__(args)

@dataclass(init=True, frozen=True)
class AllIter(Call0):
    adjunctions: Iterable[Call]

    @dataclass(init=True, frozen=True)
    class Iter(AKW_):
        iter_f:  Iterator[Call]

        def __call__(self, *args, **kwargs):
            copy_iter_f = copy(self.iter_f)
            try:
                f = next(copy_iter_f)
            except StopIteration:
                return self.continuations(*args, **kwargs)
            else:
                return f(
                    *self.args,
                    continuations=AllIter.Iter(self.continuations, self.args, self.kwargs, copy_iter_f),
                    **self.kwargs)

    def __call__(self, *args, continuations: Optional['Continuations'], **kwargs):
        all_iter_f = iter(self.adjunctions)
        try:
            f = next(all_iter_f)
        except StopIteration:
            return continuations.fail(*args, **kwargs)
        else:
            return f(
                *args,
                continuations=AllIter.Iter(continuations, args, kwargs, all_iter_f),
                **kwargs)


@dataclass(init=False, frozen=True)
class All(AllIter):
    def __init__(self, *args):
        super().__init__(args)


@dataclass(init=True, frozen=True)
class Call1(Call0):
    f: Call

    def __call__(self, *args, continuations, **kwargs):
        return self.f(*args, continuations=continuations, **kwargs)


@dataclass(init=True, frozen=True)
class Call2(Call1):
    g: Call

    def __call__(self, *args, continuations, **kwargs):
        return self.f(*args, continuations=ContinuationsSucceed(self.g, continuations), **kwargs)


t01 = First(Succeed())("ok", continuations=OnSuccess(AKW))
t02 = First(Fail(), Succeed())("ok", continuations=OnSuccess(AKW))
print(t01)
print(t02)

@dataclass(init=True, frozen=True)
class FAKW(AKW_):
    def __init__(self, *args, continuations=None, **kwargs):
        super().__init__(continuations, args, kwargs)


t03 = First(Fail())("ok", continuations=OnSuccess(AKW, OnFail(FAKW)))
t04 = First(Fail(), Fail())("ok", continuations=OnSuccess(AKW, OnFail(FAKW)))
print(t03)
print(t04)


t05 = All(Succeed())("ok", continuations=OnSuccess(AKW))
t06 = All(Succeed(), Succeed())("ok", continuations=OnSuccess(AKW))
print(t05)
print(t06)

@dataclass(init=True, frozen=True)
class FAKW(AKW_):
    def __init__(self, *args, continuations=None, **kwargs):
        super().__init__(continuations, args, kwargs)


t07 = All(Fail())("ok", continuations=OnSuccess(AKW, OnFail(FAKW)))
t08 = All(Succeed(), Fail())("ok", continuations=OnSuccess(AKW, OnFail(FAKW)))
print(t07)
print(t08)

@dataclass(init=True, frozen=True)
class InvertLogic(Continuations):
    def __call__(self, *args, **kwargs):
        return self.continuations.fail(*args, **kwargs)

    def fail(self, *args, **kwargs):
        return self.continuations(*args, **kwargs)


@dataclass(init=True, frozen=True)
class Fails(Call1):
    def __call__(self, *args, continuations: Optional['Continuations'], **kwargs):
        return self.f(*args, continuations= InvertLogic(continuations), **kwargs)


t09 = Fails(First(Fails(Succeed()), Fail()))("ok", continuations=OnSuccess(AKW))
t10 = Fails(First(Fail(), Succeed()))("ok", continuations=OnSuccess(AKW, OnFail(FAKW)))
t11 = Fails(First(Fail(), Fail()))("ok", continuations=OnSuccess(AKW, OnFail(FAKW)))
print(t09)
print(t10)
print(t11)

@dataclass(init=True, frozen=True)
class AllApplyN1(Call0):
    adjunctions: Iterable[Call]

    @dataclass(init=True, frozen=True)
    class Apply(AKW_):
        iter_f:  Iterator[Call]

        def __call__(self, first, *args, **kwargs):
            copy_iter_f = copy(self.iter_f)
            try:
                f = next(copy_iter_f)
            except StopIteration:
                return [first]
            else:
                others = f(
                    *self.args,
                    continuations=AllApplyN1.Apply(self.continuations, self.args, self.kwargs, copy_iter_f),
                    **self.kwargs)
                others.append(first)
                return others

    def __call__(self, *args, continuations: Optional['Continuations'], **kwargs):
        all_iter_f = iter(self.adjunctions)
        try:
            f = next(all_iter_f)
        except StopIteration:
            return continuations.fail(*args, **kwargs)
        else:
            others = f(
                *args,
                continuations=AllApplyN1.Apply(continuations, args, kwargs, all_iter_f),
                **kwargs)
            result = self.adjunctions.__class__(reversed(others))
            return continuations(result, *args[1:], **kwargs)


@dataclass(init=False, frozen=True)
class AllN1(AllApplyN1):
    def __init__(self, *args):
        super().__init__(args)


t12 = AllN1(Succeed(), Succeed())("ok", continuations=OnSuccess(AKW))
print(t12)

class Inc(Call0):
    def __call__(self, *args, continuations, **kwargs):
        return continuations(args[0]+1, *args[1:], **kwargs)


class Dec(Call0):
    def __call__(self, *args, continuations, **kwargs):
        return continuations(args[0]-1, *args[1:], **kwargs)

dec, inc = Dec(), Inc()

t13 = AllN1(inc, dec)(0, continuations=OnSuccess(AKW))
print(t13.args)

@dataclass(init=True, frozen=True)
class SelectApplyN1(Call0):
    disjunctions: Iterable[Call]

    @dataclass(init=True, frozen=True)
    class Apply(AKW_):
        iter_f:  Iterator[Call]

        def __call__(self, first, *args, **kwargs):
            copy_iter_f = copy(self.iter_f)
            try:
                f = next(copy_iter_f)
            except StopIteration:
                return [first]
            else:
                others = f(
                    *self.args,
                    continuations=SelectApplyN1.Apply(self.continuations, self.args, self.kwargs, copy_iter_f),
                    **self.kwargs)
                others.append(first)
                return others

        def fail(self, *args, **kwargs):
            copy_iter_f = copy(self.iter_f)
            try:
                f = next(copy_iter_f)
            except StopIteration:
                return []
            else:
                others = f(
                    *self.args,
                    continuations=SelectApplyN1.Apply(self.continuations, self.args, self.kwargs, copy_iter_f),
                    **self.kwargs)
                return others

    def __call__(self, *args, continuations: Optional['Continuations'], **kwargs):
        select_iter_f = iter(self.disjunctions)
        try:
            f = next(select_iter_f)
        except StopIteration:
            return continuations.fail(*args, **kwargs)
        else:
            others = f(
                *args,
                continuations=SelectApplyN1.Apply(continuations, args, kwargs, select_iter_f),
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
    def __call__(self, *args, continuations, **kwargs):
        if self.value > args[0]:
            return continuations((self.value, args[0]), *args[1:], **kwargs)
        else:
            return continuations.fail(*args, **kwargs)


t14 = SelectN1(Above(3))(5, continuations=OnSuccess(AKW, OnFail(FAKW)))
t15 = SelectN1(Above(3))(2, continuations=OnSuccess(AKW, OnFail(FAKW)))
t16 = SelectN1(Above(3), Above(5), Above(7), Above(8))(6, continuations=OnSuccess(AKW, OnFail(FAKW)))

print(t14.args)
print(t15.args)
print(t16.args)

t17 = SelectApplyN1((Above(3), Above(5), Above(7), Above(8)))(6, continuations=OnSuccess(AKW, OnFail(FAKW)))

print(t17.args)

print(" ")