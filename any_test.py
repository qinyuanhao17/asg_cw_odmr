import sys
import ctypes
# a = "hello"
# b = bytes(a, encoding='utf-8')
# c = b'hello'
# if b == c:
#     print("the same")

# a = '0b1111'
# print(a[-2])

# if 0b11 == 0b0011:
#     print("equal")

# from scipy.special import comb, perm

# print(comb(4,2))

# def test(a,*args):
#     print(test.__code__.co_argcount)
#     print(a)
#     print(*args)

# test(1,2,3)

a = int(100)
b = ctypes.c_uint64(a)
print(b)