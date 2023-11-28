import time
t1 = time.time()
s = 0
for i in range(1, 10000001):
    s += i
    
print(s)

expected = 50000005000000
if s != expected:
    print("Wrong answer: ", s)
    print("Expected: ", expected)
else:
    print("Correct!")

t2 = time.time()
print("Elapsed time: ", t2 - t1)