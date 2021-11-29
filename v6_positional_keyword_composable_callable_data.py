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


class AKW2D(AKW):
    pass

class AKW2C(AKW):
    pass


def q28(k: str) -> Tuple[AKW2D, AKW2C]:
    funcs = f"""
def init_d_k(self, *args, {k}, **kwargs):
   object.__setattr__(self, 'args', ({k},)+args)
   object.__setattr__(self, 'kwargs', kwargs)

def init_c_k(self, *args, **kwargs):
   object.__setattr__(self, 'args', args[1:])
   object.__setattr__(self, 'kwargs', dict({k}=args[0], **kwargs))
"""

    exec(funcs, globals())
    d = type('AKW2D'+k, (AKW2D,), {'tag': k, '__init__': init_d_k})
    c = type('AKW2C'+k, (AKW2C,), {'tag': k, '__init__': init_c_k})
    return d, c

q29, q30 = q28('k1')


@dataclass(init=True, frozen=True)
class Compose:
    f: Any
    g: Any

    def __call__(self, *args, **kwargs):
        return AKW(*args, **kwargs)(self.f)(self.g)

#c30 = lambda *args, **kwargs: q29(*args, **kwargs)(q30)
c30 = Compose(q29, q30)
print(c30)

c30('a', 'b', k1=1, k2=2)(p)

def inc(*args, **kwargs):
    return AKW(args[0]+1, *args[1:], **kwargs)

def dec(*args, **kwargs):
    return AKW(args[0]-1, *args[1:], **kwargs)

d_dec = Compose(q29, dec)
inc_c = Compose(inc, q30)
d_dec_inc_c = Compose(d_dec, inc_c)

print(d_dec_inc_c)

d_dec_inc_c('a', 'b', k1=1, k2=2)(p)

d_dec = Compose(q29, dec)
d_dec_c = Compose(d_dec, q30)

print(d_dec_c)

d_dec_c('a', 'b', k1=1, k2=2)(p)


print("")
