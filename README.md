# rpfpy
multiple iterations looking for the best way to write reversible point-free python

(links are to YouTube https://youtu.be/xrbyC4ZTL4E where I put the "voice over" description of these code snippets. Blog entry is here 
1-8: https://equational.blogspot.com/2021/12/point-free-reversible-python.html).
9: https://equational.blogspot.com/2021/12/data-composition-from-functional.html

1) Create a function that swaps positional and keyword arguments. Swapping is reversable. https://youtu.be/xrbyC4ZTL4E?t=72
2) Use eval and lambda to generate a reversable function that swaps position and keyword arguments. https://youtu.be/xrbyC4ZTL4E?t=321
3) Lambdas are a pain to debug, so create dynamic classes that define reversable callable objects https://youtu.be/xrbyC4ZTL4E?t=618
4) Let's try this backwards: says we have data objects that carry function arguments (args, and kwargs), can we make reversable callable objects? Do they interact with our previous functions? https://youtu.be/xrbyC4ZTL4E?t=909
5) Small interlude: let's add some methods to reverse functions (complementary). https://youtu.be/xrbyC4ZTL4E?t=1548
6) Focusing on the data objects and make the reversable callable objects from these. https://youtu.be/xrbyC4ZTL4E?t=1658
7) First go at replacing local functions with tail continuation. https://youtu.be/xrbyC4ZTL4E?t=1771
8) It is Python, point-free, composable, reversible, and we can do interpretation by tier with multiple levels of tail continuation. https://youtu.be/xrbyC4ZTL4E?t=2290

Some closing remarks (1-8): https://youtu.be/xrbyC4ZTL4E?t=2865

9) Data composition from functional composition:  https://www.youtube.com/watch?v=IzbsDTRmHrE

