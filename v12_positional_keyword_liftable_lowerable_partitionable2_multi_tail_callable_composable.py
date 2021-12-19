from dataclasses import dataclass, make_dataclass, fields, asdict



def partitionC_ks1(cls, ks):
    fs = fields(cls)
    ks_fields = tuple([(f.name, f.type, f) for f in fs if f.name in ks])
    not_ks_fields = tuple([(f.name, f.type, f) for f in fs if f.name not in ks])
    ks_cls_name = cls.__name__ + '_W_' + '_'.join(ks)
    not_ks_cls_name = cls.__name__ + '_N_' + '_'.join(ks)
    ks_cls = make_dataclass(ks_cls_name, ks_fields, init=True, frozen=True) #, kw_only=True)
    not_ks_cls = make_dataclass(not_ks_cls_name, not_ks_fields, init=True, frozen=True) #, kw_only=True)
    return ks_cls, not_ks_cls

@dataclass(init=True, frozen=True, kw_only=True)
class A:
    a: str
    b: str
    c: int
    d: int

def name_and_type_of_fields(cls):
    return [(field.name, field.type) for field in fields(cls)]

print(A, name_and_type_of_fields(A))

X, Y = partitionC_ks1(A, ('a','c'))

print(X, name_and_type_of_fields(X))
print(Y, name_and_type_of_fields(Y))

a = A(a='a1', b='b1', c=11, d=21)
x = X(a='a2', c=12)
y = Y(b='b2', d=22)
print(a)
print(x)
print(y)

def d_A1(a: A):
    return X(a=a.a, c=a.c), Y(b=a.b, d=a.d)

def c_A1(x: X, y: Y):
    return A(a= x.a, b=y.b, c=x.c, d=y.d)

x1, y1 = d_A1(a)
a1 = c_A1(x1, y1)
print(x1)
print(y1)
print(a1)

def field_keys(fields):
    return [f.name for f in fields]

def subset_dict(d, keys):
    return {k: d[k] for k in keys}


@dataclass(init=True, frozen=True)
class CC:
    cls: object

    def __call__(self, o1, o2):
        return self.cls(**asdict(o1), **asdict(o2))


@dataclass(init=True, frozen=True)
class DC:
    cls1: object
    cls2: object

    def __call__(self, o):
        return (self.cls1(**subset_dict(asdict(o), field_keys(fields(self.cls1)))),
                self.cls2(**subset_dict(asdict(o), field_keys(fields(self.cls2)))))


def partitionC_ks2(cls, ks):
    fs = fields(cls)
    ks_fields = tuple([(f.name, f.type, f) for f in fs if f.name in ks])
    not_ks_fields = tuple([(f.name, f.type, f) for f in fs if f.name not in ks])
    ks_cls_name = cls.__name__ + '_W_' + '_'.join(ks)
    not_ks_cls_name = cls.__name__ + '_N_' + '_'.join(ks)
    ks_cls = make_dataclass(ks_cls_name, ks_fields, init=True, frozen=True)  # , kw_only=True)
    not_ks_cls = make_dataclass(not_ks_cls_name, not_ks_fields, init=True)  # , kw_only=True)
    return CC(cls), DC(ks_cls, not_ks_cls)

c_A2, d_A2 = partitionC_ks2(A, ('a','c'))

print(c_A2)
print(d_A2)

x2, y2 = d_A2(a)
a2 = c_A2(x2, y2)

print(x2)
print(y2)
print(a2)

print(" ")

# I tried to make this version work while watching "Le Samurai" of Jean-Pierre Melville,
# but failed to get access to the new classes within the eval.
# def partitionC_ks2(cls, ks):
#     fs = fields(cls)
#     ks_fields = tuple([(f.name, f.type, f) for f in fs if f.name in ks])
#     not_ks_fields = tuple([(f.name, f.type, f) for f in fs if f.name not in ks])
#     ks_cls_name = cls.__name__ + '_W_' + '_'.join(ks)
#     not_ks_cls_name = cls.__name__ + '_N_' + '_'.join(ks)
#     print(globals())
#     ks_cls = make_dataclass(ks_cls_name, ks_fields, init=True, frozen=True, namespace={'__module__': __name__}) #, kw_only=True)
#     not_ks_cls = make_dataclass(not_ks_cls_name, not_ks_fields, init=True, frozen=True, namespace={'__module__': __name__}) #, kw_only=True)
#     print(globals())
#     ks_cls_args = ', '.join([kf[0]+'=a.'+kf[0] for kf in ks_fields])
#     not_ks_cls_args = ', '.join([kf[0]+'=a.'+kf[0] for kf in not_ks_fields])
#     d_str = f'lambda a: ({ks_cls_name}({ks_cls_args}), {not_ks_cls_name}({not_ks_cls_args}))'
#     print(d_str)
#     d = eval(d_str, globals(), locals())
#     cls_ks_args = ', '.join([kf[0]+'=x.'+kf[0] for kf in ks_fields])
#     cls_not_ks_args = ', '.join([kf[0]+'=y.'+kf[0] for kf in not_ks_fields])
#     c_str = f'lambda x, y: {cls.__name__}({cls_ks_args}, {cls_not_ks_args})'
#     print(c_str)
#     c = eval(c_str, globals(), locals())
#     return c, d

