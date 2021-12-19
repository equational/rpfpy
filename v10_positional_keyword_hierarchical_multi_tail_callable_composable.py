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
from typing import Tuple, Any, Optional, Protocol, Union


class Call(Protocol):
    def __call__(self, *args, continuations: Optional['Continuations'], **kwargs):
        pass

@dataclass(init=True, frozen=True)
class Continuations:
    continuation: Union[Call, object]
    continuations: Optional['Continuations'] = None

    def __call__(self, *args, **kwargs):
        return self.continuation(*args, continuations=self.continuations, **kwargs)

    def __getitem__(self, item):
        if item==0:
            return self.continuation
        else:
            return self.continuations

@dataclass(init=False, frozen=True)
class AKW:
    args: Any
    continuations: Optional[Continuations]
    kwargs: Any

    def __init__(self, *args, continuations=None, **kwargs):
        object.__setattr__(self, 'args', args)
        object.__setattr__(self, 'kwargs', kwargs)
        object.__setattr__(self, 'continuations', continuations)


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
        return self.f(*args, continuations=Continuations(self.g, continuations), **kwargs)


def mkc_k(k: str) -> Tuple[Call0, Call0]:
    d_k = eval(f"lambda self, *args, continuations, {k}, **kwargs:  continuations(*(({k},)+args), **kwargs)")
    c_k = eval(f"lambda self, *args, continuations, **kwargs: continuations(*args[1:], {k}=args[0], **kwargs)")
    d = type('D_'+k, (Call0,), {'tag': k, '__call__': d_k})
    c = type('C_'+k, (Call0,), {'tag': k, '__call__': c_k})
    return d(), c()


d_k1, c_k1 = mkc_k('k1')

class Inc(Call0):
    def __call__(self, *args, continuations, **kwargs):
        return continuations(args[0]+1, *args[1:], **kwargs)


class Dec(Call0):
    def __call__(self, *args, continuations, **kwargs):
        return continuations(args[0]-1, *args[1:], **kwargs)

dec, inc = Dec(), Inc()


print(inc(0, 'a', 'b', k1=1, k2=2, continuations=Continuations(AKW)))

class Apply(Call1):
    pass

print(Apply(inc)(0, 'a', 'b', k1=1, k2=2, continuations=Continuations(AKW)))

class MapSet(Call1):
    def __call__(self, first_set, *args, continuations, **kwargs):
        def lowered(element):
            return (self.f(element, *args, continuations=Continuations(AKW), **kwargs)).args[0]
        first_set_mapped = set(map(lowered, first_set))
        return continuations(first_set_mapped, *args, **kwargs)

print(MapSet(inc)({1,2}, 'a', 'b', k1=1, k2=2, continuations=Continuations(AKW)))

print((d_k1*MapSet(inc)*c_k1)('a', 'b', k1={1,2}, k2=2, continuations=Continuations(AKW)))

class Map(Call1):
    def __call__(self, first_mappable, *args, continuations, **kwargs):
        def lowered(element):
            return (self.f(element, *args, continuations=Continuations(AKW), **kwargs)).args[0]
        if isinstance(first_mappable, (dict, )):
            first_mapped = {k: lowered(v) for k, v in first_mappable.items()}
        elif is_dataclass(first_mappable):
            first_mapped =  first_mappable.__class__(**{field.name: lowered(getattr(first_mappable, field.name))
                                                        for field in fields(first_mappable)})
        else:
            first_mapped = first_mappable.__class__(map(lowered, first_mappable))
        return continuations(first_mapped, *args, **kwargs)

print((d_k1*Map(inc)*c_k1)('a', 'b', k1={1,2}, k2=2, continuations=Continuations(AKW)))
print((d_k1*Map(inc)*c_k1)('a', 'b', k1=[1,2], k2=2, continuations=Continuations(AKW)))
print((d_k1*Map(inc)*c_k1)('a', 'b', k1=(1,2), k2=2, continuations=Continuations(AKW)))
print((d_k1*Map(inc)*c_k1)('a', 'b', k1={'x': 1,'y': 2}, k2=2, continuations=Continuations(AKW)))

@dataclass(init=True, frozen=True)
class Pair:
    first: Any
    second: Any

print((d_k1*Map(inc)*c_k1)('a', 'b', k1=Pair(1,2), k2=2, continuations=Continuations(AKW)))



print(" ")