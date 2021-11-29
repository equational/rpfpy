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

def q1(*args, k1, **kwargs):
    p(*args, k1, **kwargs)

q1('a', 'b', k1=1, k2=2)

def q2(*args, **kwargs):
    p(*args[1:], k0=args[0], **kwargs)

q2('a', 'b', k1=1, k2=2)

def q3(*args, k0, **kwargs):
    p(k0, *args, **kwargs)

def q4(*args, **kwargs):
    q3(*args[1:], k0=args[0], **kwargs)

q4('a', 'b', k1=1, k2=2)


