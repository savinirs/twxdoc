import os
import sys

if not __package__:
    path = os.path.join(os.path.dirname(__file__), os.pardir)
    sys.path.insert(0, path)

print("hello world")

print("executing in __main__.py")
