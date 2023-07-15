from ping3 import ping


res = ping("http://localhost:80", timeout=5)
print(res)