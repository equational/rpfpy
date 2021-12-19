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


class Call(Protocol):
    def __call__(self, *args, continuations: Optional['Continuations'], **kwargs):
        pass

@dataclass(init=True, frozen=True)
class Continuations:
    continuation: Union[Call, object]
    continuations: Optional['Continuations'] = None

    def __call__(self, *args, **kwargs):
        return self.continuation(*args, continuations=self.continuations, **kwargs)

@dataclass(init=False, frozen=True)
class AKW:
    args: Any
    continuations: Optional[Continuations]
    kwargs: Any

    def __init__(self, *args, continuations=None, **kwargs):
        object.__setattr__(self, 'args', args)
        object.__setattr__(self, 'kwargs', kwargs)
        object.__setattr__(self, 'continuations', continuations)

    def __call__(self, f):
        return f(*self.args, continuations=self.continuations, **self.kwargs)


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


@dataclass(init=True, frozen=True)
class MKAKW(Call):

    def __call__(self, *args, continuations: Optional['Continuations'], **kwargs):
        return AKW(*args, continuations, **kwargs)


@dataclass(init=True, frozen=True)
class Indexed(MKAKW):
    index: int


@dataclass(init=True, frozen=True)
class Assorted(MKAKW):
    pass


@dataclass(init=True, frozen=True)
class Keyed(MKAKW):
    key: Any


@dataclass(init=True, frozen=True)
class Map(Call1):

    def __call__(self, first_mappable, *args, continuations, **kwargs):
        def lowered(continuation, element):
            return (self.f(element, *args, continuations=Continuations(continuation, continuations), **kwargs)).args[0]
        if isinstance(first_mappable, (dict, )):
            first_mapped = {k: lowered(Keyed(k), v) for k, v in first_mappable.items()}
        elif isinstance(first_mappable, (tuple,)):
            first_mapped = tuple([lowered(Indexed(i), v) for i, v in enumerate(first_mappable)])
        elif isinstance(first_mappable, (list,)):
            first_mapped = [lowered(Indexed(i), v) for i, v in enumerate(first_mappable)]
        elif isinstance(first_mappable, (set,)):
            first_mapped = set([lowered(Assorted(), v) for v in first_mappable])
        elif is_dataclass(first_mappable):
            first_mapped = first_mappable.__class__(**{field.name: lowered(Keyed(field.name),
                                                                           getattr(first_mappable, field.name))
                                                       for field in fields(first_mappable)})
        else:
            assert False
        return continuations(first_mapped, *args, **kwargs)




print((d_k1*Map(inc)*c_k1)('a', 'b', k1={1,2}, k2=2, continuations=Continuations(AKW)))
print((d_k1*Map(inc)*c_k1)('a', 'b', k1=[1,2], k2=2, continuations=Continuations(AKW)))
print((d_k1*Map(inc)*c_k1)('a', 'b', k1={'x': 1,'y': 2}, k2=2, continuations=Continuations(AKW)))


@dataclass(init=True, frozen=True)
class Pair:
    first: Any
    second: Any


print((d_k1*Map(inc)*c_k1)('a', 'b', k1=Pair(1, 2), k2=2, continuations=Continuations(AKW)))

print((d_k1*Map(inc)*c_k1*d_k1*Map(dec)*c_k1)('a', 'b', k1=[1, 2], k2=2, continuations=Continuations(AKW)))


class Inc2(Call0):
    def __call__(self, *args, continuations, **kwargs):
        print(continuations.continuation)
        return continuations(args[0]+1, *args[1:], **kwargs)

_t = (d_k1*Map(Inc2())*c_k1)('a', 'b', k1={'x': 1,'y': 2}, k2=2, continuations=Continuations(AKW))



@dataclass(init=True, frozen=True)
class RMap(Call1):

    def __call__(self, first_mappable, *args, continuations, **kwargs):
        def lowered(continuation, element):
            return (self(element, *args, continuations=Continuations(continuation, continuations), **kwargs)).args[0]

        if isinstance(first_mappable, (dict,)):
            first_mapped = {k: lowered(Keyed(k), v) for k, v in first_mappable.items()}
        elif isinstance(first_mappable, (tuple,)):
            first_mapped = tuple([lowered(Indexed(i), v) for i, v in enumerate(first_mappable)])
        elif isinstance(first_mappable, (list,)):
            first_mapped = [lowered(Indexed(i), v) for i, v in enumerate(first_mappable)]
        elif isinstance(first_mappable, (set,)):
            first_mapped = set([lowered(Assorted(), v) for v in first_mappable])
        elif is_dataclass(first_mappable):
            first_mapped = first_mappable.__class__(**{field.name: lowered(Keyed(field.name),
                                                                           getattr(first_mappable, field.name))
                                                       for field in fields(first_mappable)})
        else:
            return self.f(first_mappable, *args, continuations=continuations, **kwargs)
        return continuations(first_mapped, *args, **kwargs)


print((d_k1*RMap(inc)*c_k1)('a', 'b', k1=[1,[2, 3]], k2=2, continuations=Continuations(AKW)))
print((d_k1*RMap(inc)*c_k1*d_k1*RMap(dec)*c_k1)('a', 'b', k1=[1,[2, 3]], k2=2, continuations=Continuations(AKW)))
print((d_k1*RMap(inc)*c_k1)('a', 'b', k1=Pair(1, Pair(2, 3)), k2=2, continuations=Continuations(AKW)))

@dataclass(init=True, frozen=True)
class PartitionByIndex(Call1):

    def __call__(self, partitionable, *args, continuations, **kwargs):
        def lowered_indexed(continuation, element):
            return (self.f(element, *args, continuations=Continuations(continuation, continuations), **kwargs)).args[0]

        def just_index(i, seq):
            return [element for partition, element in seq if partition == i]

        def length(indexed):
            return max(next(map(list, zip(*indexed))), default=0)+1

        if isinstance(partitionable, (dict, )):
            first_indexed = list([lowered_indexed(Keyed(k), v) for k, v in partitionable.items()])
            first_partitioned = tuple([partitionable.__class__(just_index(i, first_indexed)) for i in range(0, length(first_indexed))])
        elif isinstance(partitionable, (tuple,list)):
            first_indexed = list([lowered_indexed(Indexed(i), v) for i, v in enumerate(partitionable)])
            first_partitioned = tuple([partitionable.__class__(just_index(i, first_indexed)) for i in range(0, length(first_indexed))])
        elif isinstance(partitionable, (set,)):
            first_indexed = list([lowered_indexed(Indexed(i), v) for i, v in enumerate(partitionable)])
            first_partitioned = tuple([set(just_index(i, first_indexed)) for i in range(0, length(first_indexed))])
        else:
            assert False
        return continuations(first_partitioned, *args, **kwargs)

class IndexType(Call0):
    def __call__(self, first, *args, continuations, **kwargs):
        cls = first.__class__
        if cls == int:
            index = 0
        elif cls == str:
            index = 1
        else:
            assert False
        return continuations((index, first), *args, **kwargs)

indexType = IndexType()

print((d_k1*PartitionByIndex(indexType)*c_k1)('a', 'b', k1=[1, 'a', 2, 'b'], k2=2, continuations=Continuations(AKW)))

@dataclass(init=True, frozen=True)
class UnPartition(Call0):

    def __call__(self, unpartitionable, *args, continuations, **kwargs):
        if isinstance(unpartitionable, (tuple, list, set)):
            first_partition = next(iter(unpartitionable))
            unpartitioned_first = first_partition.__class__(
                [value for partition in unpartitionable for value in partition])
        elif isinstance(unpartitionable, (dict,)):
            unpartitioned_first = {k: v for partition in unpartitionable for k, v in partition}
        else:
            assert False
        return continuations(unpartitioned_first, *args, **kwargs)

partitioned1 = (d_k1*PartitionByIndex(indexType)*c_k1)('a', 'b', k1=[1, 'a', 2, 'b'], k2=2, continuations=Continuations(AKW))
reverting = (d_k1*PartitionByIndex(indexType)*c_k1*d_k1*UnPartition()*c_k1)('a', 'b', k1=[1, 'a', 2, 'b'], k2=2, continuations=Continuations(AKW, Continuations(AKW)))
unpartitioned1 = (d_k1*UnPartition()*c_k1)('a', 'b', k1=([1, 2], ['a', 'b']), k2=2, continuations=Continuations(AKW))
print(partitioned1)
print(reverting)
print(unpartitioned1)

partitioned2 = (d_k1*PartitionByIndex(indexType)*c_k1)('a', 'b', k1=[1, 'a', 2, 'b'], k2=2, continuations=Continuations(AKW, Continuations(AKW)))
unpartitioned2 = partitioned2(d_k1*UnPartition()*c_k1)
print(partitioned2)
print(unpartitioned2)

def mk_index_partitioner(indexing):
    return PartitionByIndex(indexing), UnPartition()

c_pi1, d_pi1 = mk_index_partitioner(IndexType())

partitioned2 = (d_k1*c_pi1*c_k1)('a', 'b', k1=[1, 'a', 2, 'b'], k2=2, continuations=Continuations(AKW))
reverting2 = (d_k1*c_pi1*c_k1*d_k1*d_pi1*c_k1)('a', 'b', k1=[1, 'a', 2, 'b'], k2=2, continuations=Continuations(AKW, Continuations(AKW)))
unpartitioned2 = (d_k1*d_pi1*c_k1)('a', 'b', k1=([1, 2], ['a', 'b']), k2=2, continuations=Continuations(AKW))
print(partitioned2)
print(reverting2)
print(unpartitioned2)

print(" ")