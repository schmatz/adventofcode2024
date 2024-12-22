* We know that at the end of the program, register A *must* contain 0 for the program to terminate

* Program assembly

bst 4 (2,4)
bxl 7 (1,7)
cdv 5 (7,5)
bxl 7 (1,7)
bxc 6 (4,6)
adv 3 (0,3)
out 5 (5,5)
jnz 0 (3,0)

* Program high-level-assembly
B = A % 8
B = B ^ 7
C = A // (2 ** B)
B = B ^ 7
B = B ^ C
A = A // 8
output(B % 8)
jump if A not 0

* Binary style (slightly reordered)
B = A & 0b111 (get lower three bits of A, store in B)
B = B ^ 0b111 (negate B)
C = A >> B (shift A by B)
B = B ^ 0b111 (negate B, returning it to original in instruction 1)
B = B ^ C (XOR B and C)
output(B % 8)
A = A >> 3
jump if A not 0

```python
a = 66245665 # Whatever value
output = []
while a > 0:
    b = a & 0b111
    b = b ^ 0b111
    c = a >> b
    b = b ^ 0b111
    b = b ^ c
    output.append(b & 0b111)
    a = a >> 3
return output
```
* Now try to reverse it.
* We know that at the end of the program, A must be equal to 0, and only the last 3 binary digits were possibly nonzero.

