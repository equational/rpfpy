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

p('a', 'b', k1=1, k2=2)


def q1(f0):
    def f1(*args, **kwargs):
        f0(*args, **kwargs)
    return f1

q1(p)('a', 'b', k1=1, k2=2)

def q2(f0):
    def f1(*args, k0, **kwargs):
        f0(k0, *args, **kwargs)
    return f1

def q3(f0):
    def f1(*args, **kwargs):
        f0(*args[1:], k0=args[0], **kwargs)
    return f1


q3(q2(p))('a', 'b', k1=1, k2=2)

q2(q3(p))('a', 'b', k0=0, k1=1, k2=2)

def q4(f0):
    return lambda *args, k0, **kwargs: f0(k0, *args, **kwargs)

def q5(f0):
    return lambda *args, **kwargs: f0(*args[1:], k0=args[0], **kwargs)

q5(q4(p))('a', 'b', k1=1, k2=2)

def q6(f0):
    return eval('lambda *args, k0, **kwargs: f0(k0, *args, **kwargs)', locals())

def q7(f0):
    return eval('lambda *args, **kwargs: f0(*args[1:], k0=args[0], **kwargs)', locals())

q7(q6(p))('a', 'b', k1=1, k2=2)

q8=eval('lambda f0: lambda *args, k0, **kwargs: f0(k0, *args, **kwargs)')

q9=eval('lambda f0: lambda *args, **kwargs: f0(*args[1:], k0=args[0], **kwargs)')

q9(q8(p))('a', 'b', k1=1, k2=2)

def q10(k):
    return eval(f'lambda f0: lambda *args, {k}, **kwargs: f0({k}, *args, **kwargs)')

def q11(k):
    return eval(f'lambda f0: lambda *args, **kwargs: f0(*args[1:], {k}=args[0], **kwargs)')

q12 = q10('k0')
q13 = q11('k0')

q13(q12(p))('a', 'b', k1=1, k2=2)

q14 = q10('k1')
q15 = q11('k1')

q14(q15(p))('a', 'b', k1=1, k2=2)

def q16(k):
    return (
        eval(f'lambda f0: lambda *args, {k}, **kwargs: f0({k}, *args, **kwargs)'),
        eval(f'lambda f0: lambda *args, **kwargs: f0(*args[1:], {k}=args[0], **kwargs)')
    )

q17, q18 = q16('k1')

q17(q18(p))('a', 'b', k1=1, k2=2)

def compose(f, g):
    return lambda *args, **kwargs: f(g(*args, **kwargs))

compose(q17, q18)(p)('a', 'b', k1=1, k2=2)


c0 = compose(q17, q18)
