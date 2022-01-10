# rpfpy
multiple iterations looking for the best way to write reversible point-free python

Blog entry is here: https://equational.blogspot.com/2022/01/reversible-contextual-python-with.html

Here is a run through of what each rewrite version is about:
1) This effort starts with a hard coded functions to swap a positional argument to keyword arguments and vice versa (the other way around).  Swapping is reversable, and our goal here is to write reversible code. 
2) A generic keyword argument' constructor/destructor function can be implemented by simply 'accessing kwargs'. However, Python has no efficient ways to remove keys from a dict, and that forces us to use 'ugly' copy constructs to 'pass on' a kwargs, minus the chosen keyword. Therefore  version two uses eval and lambda to generate a an effcient generic keyword argument' constructor/destructor. 
3) Lambdas are a pain to debug and to type annotate,  version three uses callable objects instead of lambdas.
4) None of the above is composable nor 'stateful' (from a 'traditional' perspective), as all happens within function arguments. Version 4 adds function composition and introduce a AKW class, to 'statefully' hold function arguments. It is 'reversible', in that we can 'call' (cocall) a function with the object's data as arguments. 
5) This is all dynamic typing, and initially at least, with no type conditional expression. However, to 'feel the ground', version 5 does the following: if two complementary functions/lambdas are expressed as callable object, then we can give their type classes a class attribute which programmatically provides this complementary tie. For example, given d_k1() an operator from keyword arg k1 to posional arg, one can find its complementary operator c_k1(), from a positional arg to a keyword arg k1.
6) Focusing on function arguments is somewhat 'stream oriented'. The AKW class introduced in 4, is more of a classical 'stateful' approach. Version 6 shows how function composition can be constructed on this stateful view.
7) Functions and callable objects are nice. Yet by default they force us to create 'return value states'. These return states 'semantics' are different and do not naturally fit within our simple 'call' semantics. Another aspect is they are 'invisible' to the notion of reversible code.  Therefore version seven takes a first go at using tail contination to avoid 'return states' of functions. 
8) Continuation passing can express a 'deeper' execution context with the help of a 'stack' of tail continuations. Version 8 introduces a continuation 'list' for this purpose.
9) Version 9 extends operators to have something equivalent to the notion 'quoted' expressions in Scheme/Lisp.
10) Version 10 introduces a basic map function. 
11) The classical tail continuation is only telling us where the output of a function should go. With a 'stack' / 'list' of continuations, we can carry more information, for example the 'index' or 'key' of the element that is currently being mapped. Version 11 shows how this is done, and shows how we can make a map able to recurse over hierchies of containers. Also this rewrite introduces a first 'partition' 'unpartion' operator.
12) Here we partition and unpartition classes of dataclass fields. 
13) Logical programming allows us to perform 'or' and 'and' like operations, and often have something similare to a 'not'. Version 13, shows how logical programming is 'easy' with tail continuation.
14) Adding a 'match' operator (with free-variable) to logical programming gives us a simple way to write declarative programs (here in Python).
15) Logical programming is more powerful with lambda expressions (or callable objects). Version 15 defines the operator SelectApplyN1, which apply multiple operators to a single argument, and keeps those that succeed. The goal where is to validate that we can mix declarative and lambda like function application.
16) In the previous code rewrites, spcial keyword arguments are defined (e.g. for continuation passing, for the free-variable list) and are explicitely defined in all the function signatures. Version 16, pushes this approach in a slightly non-sensical way by adding the keyword argument 'state' to the reference call signature, and explicitely adding this 'state' argument throughout the code. This results in the question: 'why be explicit'?
17) Version 17, only declares keyword arguments explicitly when used locally. However, the tail continuation list is an explicit keyword argument, and expressed everywhere. The 'standard' call signature looks like this:
18) At which point I ask myself: "why not go all the way"? Therefore version 18 moves the continuation stack to a positional argument, as follows:
19) Context annotation is revisited in version 19, and expressed more generically. To be specific, the continuation stack gets dynamically decorated with contextual information that can be queried 'within context'. These decorators are referred to by 'type'.
20) Continuing on context annotation, the recursive map of version 11 is adapted in version 20 and a 'depth' context specific function is introduced. The goal is to show that while "positional" context annotations is a handy nice, even more valuable is the ability to algorithmically extend your contexts.
21) Finally, we conclude this series with version 21 and a careful change ensures that the complete context stack is captured when capturing the state of compuation (e.g. with AKW as introduce in version 4).  This context becomes active again when we 'continue' compuations from each saved state (with cocall).

see also:
Current state: https://equational.blogspot.com/2022/01/reversible-contextual-python-with.html

1-8: https://equational.blogspot.com/2021/12/point-free-reversible-python.html).

9: https://equational.blogspot.com/2021/12/data-composition-from-functional.html

And YouTube https://youtu.be/xrbyC4ZTL4E where I put the "voice over" description of these early code snippets. 

All original content copyright James Litsios, 2022.
