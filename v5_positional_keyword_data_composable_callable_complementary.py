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
from typing import Tuple, Any


@dataclass(init=True, frozen=True)
class Compose:
    f: Any
    g: Any

    def __call__(self, *args, **kwargs):
        return self.f(self.g(*args, **kwargs))


@dataclass(init=True, frozen=True)
class KWArg2:
    f: Any

    @classmethod
    @abstractmethod
    def complementary(cls):
        pass

    @classmethod
    def compose_complement(cls):
        return Compose(cls, cls.complementary())

class KWArg2D(KWArg2):
    pass

class KWArg2C(KWArg2):
    pass

from types import MethodType

@dataclass(init=False, frozen=True)
class AKW:
    args: Any
    kwargs: Any

    def __init__(self, *args, **kwargs):
        object.__setattr__(self, 'args', args)
        object.__setattr__(self, 'kwargs', kwargs)

    # would ideally be called 'cocall' or something like that
    def __call__(self, f):
        return f(*self.args, **self.kwargs)


def q28(k: str) -> Tuple[KWArg2D, KWArg2C]:
    dcall = eval(f'lambda self, *args, {k}, **kwargs: self.f({k}, *args, **kwargs)')
    ccall = eval(f'lambda self, *args, **kwargs: self.f(*args[1:], {k}=args[0], **kwargs)')
    d = type('KWArg2D'+k, (KWArg2D,), {'tag': k, '__call__': dcall})
    c = type('KWArg2C'+k, (KWArg2C,), {'tag': k, '__call__': ccall})
    d.complementary = MethodType(lambda cls: c, d)
    c.complementary = MethodType(lambda cls: d, c)
    return d, c

q29, q30 = q28('k1')

c30 = q29.compose_complement()
print(c30)

c30(AKW)('a', 'b', k1=1, k2=2)(p)

def inc(f0):
    return lambda *args, **kwargs: f0(args[0]+1, *args[1:], **kwargs)

def dec(f0):
    return lambda *args, **kwargs: f0(args[0]-1, *args[1:], **kwargs)

d_dec = Compose(q29, dec)
inc_c = Compose(inc, q30)
d_dec_inc_c = Compose(d_dec, inc_c)

print(d_dec_inc_c)

d_dec_inc_c(p)('a', 'b', k1=1, k2=2)

d_dec = Compose(q29, dec)
d_dec_inc_c = Compose(d_dec, q30)

print(d_dec_inc_c)

d_dec_inc_c(p)('a', 'b', k1=1, k2=2)

d_dec_inc_c(AKW)('a', 'b', k1=1, k2=2)(p)

AKW('a', 'b', k1=1, k2=2)(d_dec_inc_c(p))

AKW('a', 'b', k1=1, k2=2)(d_dec_inc_c(AKW))(p)


print("")
