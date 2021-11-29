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

def p(*args, **kwargs):
    for i, arg in enumerate(args):
        print(f'{i}:{arg}')
    for k, v in kwargs.items():
        print(f'{k}:{v}')

from abc import abstractmethod
from dataclasses import dataclass
from typing import Tuple, Any, Dict, Callable, ClassVar

@dataclass(frozen=True, init=True)
class TailCall0:
    def __call__(self, *args, tail_call: Callable[[Any, ...], Any], **kwargs):
        return tail_call(*args, **kwargs)

    def __mul__(self, g):
        return TailCall2(self, g)

    def __pow__(self, g):
        return TailCall2(g, self)


@dataclass(init=True, frozen=True)
class TailCall1(TailCall0):
    f: Any

    def __call__(self, *args, tail_call, **kwargs):
        return self.f(*args, tail_call=tail_call, **kwargs)


@dataclass(init=True, frozen=True)
class CallTail:
    f: Any
    tail_call: Any

    def __call__(self, *args, **kwargs):
        return self.f(*args, tail_call=self.tail_call, **kwargs)


@dataclass(init=True, frozen=True)
class TailCall2(TailCall1):
    g: Any

    def __call__(self, *args, tail_call, **kwargs):
        return self.f(*args, tail_call=CallTail(self.g, tail_call), **kwargs)



def mkc_k(k: str) -> Tuple[TailCall0, TailCall0]:
    d_k = eval(f"lambda self, *args, tail_call, {k}, **kwargs:  tail_call(*(({k},)+args), **kwargs)")
    c_k = eval(f"lambda self, *args, tail_call, **kwargs: tail_call(*args[1:], {k}=args[0], **kwargs)")
    d = type('D_'+k, (TailCall0,), {'tag': k, '__call__': d_k})
    c = type('C_'+k, (TailCall0,), {'tag': k, '__call__': c_k})
    return d(), c()


d_k1, c_k1 = mkc_k('k1')

id_k1_A = d_k1*c_k1
id_k1_B = c_k1**d_k1
print(id_k1_A)
print(id_k1_B)

id_k1_A('a', 'b', k1=1, k2=2, tail_call=p)
id_k1_B('a', 'b', k1=1, k2=2, tail_call=p)

class Inc(TailCall0):
    def __call__(self, *args, tail_call, **kwargs):
        return tail_call(args[0]+1, *args[1:], **kwargs)

class Dec(TailCall0):
    def __call__(self, *args, tail_call, **kwargs):
        return tail_call(args[0]-1, *args[1:], **kwargs)

dec, inc = Dec(), Inc()

d_dec = d_k1 * dec
inc_c = inc * c_k1
d_dec_inc_c = d_dec * inc_c

print(d_dec_inc_c)

d_dec_inc_c('a', 'b', k1=1, k2=2, tail_call=p)

d_dec = d_k1 * dec
d_dec_c = d_dec * c_k1

print(d_dec_c)

d_dec_c('a', 'b', k1=1, k2=2, tail_call=p)

from dis import dis

dis(d_k1.__call__)
print("")
