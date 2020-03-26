import numpy as np

a = np.array([1, 1, 1, 2])
b = a.copy() / 2
print(a)
print(b)

exp_a = np.exp(a)
exp_b = np.exp(b)
print(exp_a)
print(exp_b)
print(exp_a/np.sum(exp_a))
print(exp_b/np.sum(exp_b))

