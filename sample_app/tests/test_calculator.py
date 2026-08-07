import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from calculator import add, divide

def test_add():
    assert add(2, 3) == 5

def test_divide_intentional_failure():
    # Deliberately wrong expected value, to guarantee a failing build
    assert divide(10, 2) == 999
