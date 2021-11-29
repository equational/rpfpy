# rpfpy
multiple iterations looking for the best way to write reversible point-free python
1) Create a function that swaps positional and keyword arguments. Swapping is reversable. 
2) Use eval and lambda to generate a reversable function that swaps position and keyword arguments. 
3) Lambdas are a pain to debug, so create dynamic classes that define reversable callable objects
4) Let's try this backwards: says we have data objects that carry function arguments (args, and kwargs), can we make reversable callable objects? Do they interact with our previous functions?
5) Small interlude: let's add some methods to reverse functions (complementary).
6) Focusing on the data objects and make the reversable callable objects from these.
7) First go at replacing local functions with tail continuation.
8) It is Python, point-free, composable, reversible, and we can tier interpretation with multiple levels of tail continuation.
