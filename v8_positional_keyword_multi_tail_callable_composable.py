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
from typing import Tuple, Any, Optional, Protocol, Union


class Continuation(Protocol):
    def __call__(self, *args, continuations: Optional['Continuations'], **kwargs):
        pass

@dataclass(init=True, frozen=True)
class Continuations:
    continuation: Union[Continuation, object]
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
class Continuation0(Continuation):
    def __call__(self, *args, continuations: Optional['Continuations'], **kwargs):
        return continuations(*args, **kwargs)

    def __mul__(self, g):
        return Continuation2(self, g)

    def __pow__(self, g):
        return Continuation2(g, self)


@dataclass(init=True, frozen=True)
class Continuation1(Continuation0):
    f: Continuation

    def __call__(self, *args, continuations, **kwargs):
        return self.f(*args, continuations=continuations, **kwargs)



@dataclass(init=True, frozen=True)
class Continuation2(Continuation1):
    g: Continuation

    def __call__(self, *args, continuations, **kwargs):
        return self.f(*args, continuations=Continuations(self.g, continuations), **kwargs)


def mkc_k(k: str) -> Tuple[Continuation0, Continuation0]:
    d_k = eval(f"lambda self, *args, continuations, {k}, **kwargs:  continuations(*(({k},)+args), **kwargs)")
    c_k = eval(f"lambda self, *args, continuations, **kwargs: continuations(*args[1:], {k}=args[0], **kwargs)")
    d = type('D_'+k, (Continuation0,), {'tag': k, '__call__': d_k})
    c = type('C_'+k, (Continuation0,), {'tag': k, '__call__': c_k})
    return d(), c()


d_k1, c_k1 = mkc_k('k1')

id_k1_A = d_k1*c_k1
id_k1_B = c_k1**d_k1
print(id_k1_A)
print(id_k1_B)

print(id_k1_A('a', 'b', k1=1, k2=2, continuations=Continuations(AKW)))
print(id_k1_B('a', 'b', k1=1, k2=2, continuations=Continuations(AKW)))

class Inc(Continuation0):
    def __call__(self, *args, continuations, **kwargs):
        return continuations(args[0]+1, *args[1:], **kwargs)

class Dec(Continuation0):
    def __call__(self, *args, continuations, **kwargs):
        return continuations(args[0]-1, *args[1:], **kwargs)

dec, inc = Dec(), Inc()

d_dec = d_k1 * dec
inc_c = inc * c_k1
d_dec_inc_c = d_dec * inc_c

print(d_dec_inc_c)

print(d_dec_inc_c('a', 'b', k1=1, k2=2, continuations=Continuations(AKW)))

d_dec = d_k1 * dec
d_dec_c = d_dec * c_k1

print(d_dec_c)

print(d_dec_c('a', 'b', k1=1, k2=2, continuations=Continuations(AKW)))

print(d_dec('a', 'b', k1=1, k2=2, continuations=Continuations(c_k1 * AKW)))

print(d_dec('a', 'b', k1=1, k2=2, continuations=Continuations(dec * c_k1 * AKW)))


print("")