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

def q16(k):
    return (
        eval(f'lambda f0: lambda *args, {k}, **kwargs: f0({k}, *args, **kwargs)'),
        eval(f'lambda f0: lambda *args, **kwargs: f0(*args[1:], {k}=args[0], **kwargs)')
    )

q17, q18 = q16('k1')

from typing import Tuple, Any
from dataclasses import dataclass

@dataclass(init=True, frozen=True)
class Compose:
    f: Any
    g: Any

    def __call__(self, *args, **kwargs):
        return self.f(self.g(*args, **kwargs))

c17 = Compose(q17, q18)

print(c17)

c17(p)('a', 'b', k1=1, k2=2)

@dataclass(frozen=True, init=True)
class DKWArg0:
    tag: str

    def __call__(self, f):
        return eval(f'lambda *args, {self.tag}, **kwargs: f({self.tag}, *args, **kwargs)', locals())


@dataclass(frozen=True, init=True)
class CKWArg0:
    tag : str

    def __call__(self, f):
        return eval(f'lambda *args, **kwargs: f(*args[1:], {self.tag}=args[0], **kwargs)', locals())


def q17(k: str) -> Tuple[DKWArg0, CKWArg0]:
    return (DKWArg0(k), CKWArg0(k))

q18, q19 = q17('k1')

c19 = Compose(q18, q19)

print(c19)

c19(p)('a', 'b', k1=1, k2=2)


@dataclass(init=True, frozen=True)
class DKWArg1:
    f: Any


@dataclass(init=True, frozen=True)
class CKWArg1:
    f: Any


def q21(k: str) -> Tuple[DKWArg1, CKWArg1]:
    dcall = eval(f'lambda self, *args, {k}, **kwargs: self.f({k}, *args, **kwargs)')
    ccall = eval(f'lambda self, *args, **kwargs: self.f(*args[1:], {k}=args[0], **kwargs)')
    d = type('DKWArg1'+k, (DKWArg1,), {'tag': k, '__call__': dcall})
    c = type('CKWArg1'+k, (CKWArg1,), {'tag': k, '__call__': ccall})
    return d, c


q22, q23 = q21('k1')

c24 = Compose(q22, q23)

print(c24)

c24(p)('a', 'b', k1=1, k2=2)

print('')