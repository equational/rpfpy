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
from typing import Tuple, Any, Optional, Protocol, Union, Dict
from abc import abstractmethod

@dataclass(init=True, frozen=True, repr=False)
class MVar:
    def __repr__(self):
        return str(id(self))

@dataclass(init=True, frozen=True)
class MUnBound:
    pass

class Call(Protocol):
    def __call__(self,
                 *args,
                 continuations: Optional['Continuations'],
                 **kwargs):
        pass


@dataclass(init=True, frozen=True)
class Matches:
    matches: Optional['Matches']

    @abstractmethod
    def __getitem__(self, key: MVar):
        return MUnBound

    def rollback(self):
        return self.matches.rollback()

def dereference(matches:Optional['Matches'], key: MVar):
    if matches is not None:
        while True:
            opt_value = matches[key]
            if opt_value is MUnBound:
                return key, key
            elif not isinstance(opt_value, MVar):
                return opt_value, key
            else:
                key = opt_value
    else:
        return key, key

def dereference_n(matches:Optional['Matches'], n, key: MVar):
    def dereference_n_(n, key: MVar):
        if n <= 0:
            return key
        else:
            derefed, _rkey = dereference(matches, key)
            if isinstance(derefed, (set, list, tuple)):
                return derefed.__class__([dereference_n_(n-1, v)
                                          for v in derefed])
            elif is_dataclass(derefed):
                return derefed.__class__(**{field.name: dereference_n_(n-1, getattr(derefed, field.name))
                                            for field in fields(derefed)})
            elif isinstance(derefed, dict):
                return {k: dereference_n_(n-1, v) for k, v in derefed.items()}
            else:
                return derefed
    return dereference_n_(n, key)


@dataclass(init=True, frozen=True)
class Continuation(Protocol):

    @abstractmethod
    def __call__(self, *args, fail: bool = False, **kwargs):
        assert False

    # def fail(self, *args, **kwargs):
    #     return self(*args, fail=True, **kwargs)



@dataclass(init=True, frozen=True)
class Continuations(Continuation):
    continuations: Optional['Continuations']

    def __call__(self, *args, fail: bool = False, **kwargs):
        return self.continuations(*args, fail=fail, **kwargs)


@dataclass(init=True, frozen=True)
class MatchsEntry(Matches):
    key_value: Tuple[MVar, Any]

    def __getitem__(self, key: MVar):
        key_value = self.key_value
        if key == key_value[0]:
            return self.key_value[1]
        else:
            if self.matches is not None:
                return self.matches.__getitem__(key)
            else:
                return MUnBound
    def __repr__(self):
        if self.matches is not None:
            rest = ', '+self.matches.__repr__()
        else:
            rest = '.'
        return str(self.key_value[0])+':='+str(self.key_value[1])+rest


@dataclass(frozen=True, init=True)
class Call0(Call):
    def __call__(self, *args, continuations: Optional['Continuations'], **kwargs):
        return continuations(*args, **kwargs)

    def __mul__(self, g):
        return Call2(self, g)

    def __pow__(self, g):
        return Call2(g, self)


@dataclass(init=True, frozen=True)
class Call1(Call0):
    f: Call

    def __call__(self, *args, continuations, **kwargs):
        return self.f(*args, continuations=continuations, **kwargs)


@dataclass(init=True, frozen=True)
class Call2(Call1):
    g: Call

    def __call__(self, *args, continuations, **kwargs):
        return self.f(*args, continuations=Continuation1(self.g, continuations), **kwargs)



def mkc_k(k: str) -> Tuple[Call0, Call0]:
    d_k = eval(f"lambda self, *args, continuations, {k}, **kwargs:  continuations(*(({k},)+args), **kwargs)")
    c_k = eval(f"lambda self, *args, continuations, **kwargs: continuations(*args[1:], {k}=args[0], **kwargs)")
    d = type('D_'+k, (Call0,), {'tag': k, '__call__': d_k})
    c = type('C_'+k, (Call0,), {'tag': k, '__call__': c_k})
    return d(), c()

@dataclass(init=True, frozen=True)
class Match(Call0):
    def __call__(self, matches: Optional['Matches'], left, right, *args, continuations: Optional['Continuations'], **kwargs):
        def match(left, right, matches):
            def match_lists(lefts, rights, matches):
                if len(lefts) == len(rights):
                    for left, right in zip(lefts, rights):
                        opt_matches = match(left, right, matches)
                        if opt_matches is None:
                            return None
                        else:
                            matches = opt_matches
                    return matches
                else:
                    return None
            left, key_left = dereference(matches, left)
            right, key_right = dereference(matches, right)
            if key_left is key_right:
                return matches
            if isinstance(left, MVar):
                if isinstance(right, MVar):
                    if left is right:
                        return matches
                    elif id(left) < id(right):
                        return MatchsEntry(matches, (left, right))
                    elif id(left) > id(right):
                        return MatchsEntry(matches, (right, left))
                    else:
                        assert False
                else:
                    return MatchsEntry(matches, (left, right))
            else:
                if isinstance(right, MVar):
                    return MatchsEntry(matches, (right, left))
                else:
                    if left.__class__ == right.__class__:
                        if isinstance(left, (set, list, tuple)):
                            lefts = list([l for l in left])
                            rights = list([r for r in right])
                            return match_lists(lefts, rights, matches)
                        elif is_dataclass(left):
                            lefts = [getattr(left, field.name)
                                     for field in fields(left)]
                            rights = [getattr(right, field.name)
                                      for field in fields(right)]
                            return match_lists(lefts, rights, matches)
                        elif isinstance(left, dict):
                            left_keys = list(left.keys())
                            right_keys = list(right.keys())
                            if left_keys == right_keys:
                                lefts = list([left[k] for k in left_keys])
                                rights = list([right[k] for k in left_keys])
                                return match_lists(lefts, rights, matches)
                            else:
                                return None
                        else:
                            if left == right:
                                return matches
                            else:
                                return None
                    else:
                        return None
        opt_matches = match(left, right, matches)
        if opt_matches is not None:
            return continuations(opt_matches, left, right, *args, **kwargs)
        else:
            return continuations(matches, left, right, *args, fail=True, **kwargs)

d_matches, c_matches = mkc_k('matches')
match = d_matches*Match()*c_matches


@dataclass(init=True, frozen=True)
class FailContinuation(Continuations):
    def __call__(self, *args, fail: bool = False, **kwargs):
        return super().__call__(*args, fail=True, **kwargs)


@dataclass(init=True, frozen=True)
class Continuation1(Continuations):
    continuation: Union[Call, object]

    def __init__(self, continuation, continuations=None):
        object.__setattr__(self, 'continuation', continuation)
        super().__init__(continuations)

    def __call__(self, *args, fail: bool = False, **kwargs):
        if not fail:
            return self.continuation(*args, continuations=self.continuations, **kwargs)
        else:
            return self.continuation(*args, continuations=FailContinuation(self.continuations), **kwargs)


@dataclass(init=True, frozen=True)
class OnSuccess(Continuations):
    succeed: Union[Call, object]

    def __init__(self, succeed, continuations=None):
        object.__setattr__(self, 'succeed', succeed)
        super().__init__(continuations)

    def __call__(self, *args, fail: bool = False, **kwargs):
        if not fail:
            return self.succeed(*args, continuations=self.continuations, **kwargs)
        else:
            return super().__call__(*args, fail=fail, **kwargs)

@dataclass(init=True, frozen=True)
class OnFail(Continuations):
    fail_: Union[Call, object]

    def __init__(self, fail, continuations=None):
        object.__setattr__(self, 'fail_', fail)
        super().__init__(continuations)

    def __call__(self, *args, fail: bool = False, **kwargs):
        if fail:
            return self.fail_(*args, continuations=self.continuations, **kwargs)
        else:
            return super().__call__(*args, fail=fail, **kwargs)

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


@dataclass(init=True, frozen=True)
class Succeed(Call0):
    pass


@dataclass(init=True, frozen=True)
class Fail(Call0):
    def __call__(self, *args, continuations: Optional['Continuations'], **kwargs):
        return continuations(*args, fail=True, **kwargs)

@dataclass(init=True, frozen=True)
class First_(Call0):
    disjunctions: Tuple[Call]

    @dataclass(init=True, frozen=True)
    class Iter(AKW_):
        or_: 'First_'
        index: int

        def __call__(self, *args, fail: bool = False, **kwargs):
            if fail:
                next_index = self.index + 1
                if next_index >= len(self.or_.disjunctions):
                    return self.continuations(*args, fail=True, **kwargs)
                else:
                    return self.or_.disjunctions[next_index](
                        *self.args,
                        continuations=First_.Iter(self.continuations, self.args, self.kwargs, self.or_, next_index),
                        **self.kwargs)
            else:
                return super().__call__(*args, **kwargs)

    def __call__(self, *args, continuations: Optional['Continuations'], **kwargs):
        return self.disjunctions[0](*args, continuations=First_.Iter(continuations, args, kwargs, self, 0), **kwargs)

@dataclass(init=False, frozen=True)
class First(First_):
    def __init__(self, *args):
        super().__init__(args)

@dataclass(init=True, frozen=True)
class All_(Call0):
    adjunctions: Tuple[Call]

    @dataclass(init=True, frozen=True)
    class Iter(AKW_):
        all_: 'All'
        index: int

        def __call__(self, *args, fail: bool = False, **kwargs):
            if not fail:
                next_index = self.index + 1
                if next_index >= len(self.all_.adjunctions):
                    return self.continuations(*args, **kwargs)
                else:
                    return self.all_.adjunctions[next_index](
                        *self.args,
                        continuations=All.Iter(self.continuations, self.args, self.kwargs, self.all_, next_index),
                        **self.kwargs)
            else:
                return super().__call__(*args, fail=True, **kwargs)

    def __call__(self, *args, continuations: Optional['Continuations'], **kwargs):
        return self.adjunctions[0](*args, continuations=All.Iter(continuations, args, kwargs, self, 0), **kwargs)


@dataclass(init=False, frozen=True)
class All(All_):
    def __init__(self, *args):
        super().__init__(args)


@dataclass(init=True, frozen=True)
class FAKW(AKW_):
    def __init__(self, *args, continuations, **kwargs):
        super().__init__(continuations, args, kwargs)


@dataclass(init=True, frozen=True)
class InvertLogic(Continuations):
    def __call__(self, *args, fail: bool = False, **kwargs):
        return self.continuations(*args, fail=not fail, **kwargs)


@dataclass(init=True, frozen=True)
class Fails(Call1):
    def __call__(self, *args, continuations: Optional['Continuations'], **kwargs):
        return self.f(*args, continuations= InvertLogic(continuations), **kwargs)


t01 = match(MVar(), MVar(), matches=None, continuations=OnSuccess(AKW, OnFail(FAKW)))
print(t01)

@dataclass(init=True, frozen=True)
class MVN(MVar):
    id: str

    def __repr__(self):
        return self.id

t02 = match(MVN('a'), MVN('b'), matches=None, continuations=OnSuccess(AKW, OnFail(FAKW)))
print(t02)

kwargs = {'matches':None, 'continuations':OnSuccess(AKW, OnFail(FAKW))}
a = MVN('a')
b = MVN('b')

t03 = match(a, b, **kwargs)
t04 = All(match, match)(a, b, **kwargs)
print(t03)
print(t04)


d_k1, c_k1 = mkc_k('k1')
d_k2, c_k2 = mkc_k('k2')

k1 = MVN('k1')
k2 = MVN('k2')

t05 = (d_k1*d_k2*match*c_k2*c_k1)(k1=k1, k2=k2, **kwargs)
print(t05)

@dataclass(init=True, frozen=True, repr=False)
class Expand(Call0):
    def __call__(self, matches: Optional['Matches'], *args, continuations: Optional['Continuations'], **kwargs):
        derefed_args = [dereference(matches, arg)[0] for arg in args]
        derefed_kwargs = dict([(k, dereference(matches, v)[0]) for k,v in kwargs.items()])
        return continuations(matches, *derefed_args, **derefed_kwargs)


expand = d_matches*Expand()*c_matches
t06 = (d_k1*d_k2*match*expand*c_k2*c_k1)(k1=k1, k2=k2, **kwargs)
print(t06)


d_a, c_a = mkc_k('a')
d_b, c_b = mkc_k('b')

t07 = (d_a*d_b*match*expand*c_b*c_a)(a=(k1,k2), b=(1, 2), **kwargs)
print(t07)

@dataclass(init=True, frozen=True)
class ExpandN(Call0):
    n: int
    def __call__(self, matches: Optional['Matches'], *args, continuations: Optional['Continuations'], **kwargs):
        derefed_args = dereference_n(matches, self.n, args)
        derefed_kwargs = dereference_n(matches, self.n, kwargs)
        return continuations(matches, *derefed_args, **derefed_kwargs)


def expandN(n):
    return d_matches*ExpandN(n)*c_matches


t08 = (d_a*d_b*match*expandN(2)*c_b*c_a)(a=(k1,k2), b=(1, 2), **kwargs)
t09 = (d_a*d_b*match*expandN(2)*c_b*c_a)(a=[k1,k2], b=[1, 2], **kwargs)
t10 = (d_a*d_b*match*expandN(2)*c_b*c_a)(a={k1,k2}, b={1, 2}, **kwargs)
t11 = (d_a*d_b*match*expandN(2)*c_b*c_a)(a={'x':k1,'y':k2}, b={'x':1, 'y':2}, **kwargs)
print(t08)
print(t09)
print(t10)
print(t11)



@dataclass(init=True, frozen=True)
class Pair:
    first: Any
    second: Any

t12 = (d_a*d_b*match*expandN(2)*c_b*c_a)(a=Pair(k1,k2), b=Pair(1, 2), **kwargs)
print(t12)

t13 = (d_a*d_b*match*c_b*c_a)(a=Pair(k1,k2), b=k2, **kwargs)
t14 = (d_a*d_b*match*expandN(4)*c_b*c_a)(a=Pair(k1,k2), b=k2, **kwargs)
print(t13)
print(t14)

kwargs = {'matches':None, 'continuations':OnSuccess(AKW, OnSuccess(AKW, OnFail(FAKW)))}
t15 = (d_a*d_b*match*c_b*c_a)(a=Pair(k1,k2), b=k2, **kwargs)
t16 = t15.cocall(d_a*d_b*match*expandN(2)*c_b*c_a)
print(t15)
print(t16)


match_a_b = d_a*d_b*match*c_b*c_a
match_k1_k2 = d_k1*d_k2*match*c_k2*c_k1

t17 = (match_a_b*match_k1_k2*expandN(5))(a=Pair(k1,k2), b=k2, k1=k1, k2='a', **kwargs)
print(t17)

t18 = match_a_b(a=Pair(k1,k2), b=k2, k1=k1, k2='a', **kwargs)
t19 = t18.cocall(match_k1_k2*expandN(5))
print(t18)
print(t19)

t20 = match('x', 'y', matches=None, continuations=OnSuccess(AKW, OnFail(FAKW)))
print(t20)


print(" ")