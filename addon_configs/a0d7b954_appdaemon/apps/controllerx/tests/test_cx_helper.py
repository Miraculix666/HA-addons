import pytest

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from cx_helper import _all_subclasses

def test_all_subclasses_empty():
    class BaseWithoutSubclasses:
        pass

    assert _all_subclasses(BaseWithoutSubclasses) == []

def test_all_subclasses_single_level():
    class BaseSingleLevel:
        pass

    class Sub1(BaseSingleLevel):
        pass

    class Sub2(BaseSingleLevel):
        pass

    result = _all_subclasses(BaseSingleLevel)
    assert len(result) == 2
    assert set(result) == {Sub1, Sub2}

def test_all_subclasses_multi_level():
    class BaseMultiLevel:
        pass

    class SubA(BaseMultiLevel):
        pass

    class SubB(BaseMultiLevel):
        pass

    class SubAA(SubA):
        pass

    class SubAB(SubA):
        pass

    class SubBA(SubB):
        pass

    result = _all_subclasses(BaseMultiLevel)
    assert len(result) == 5
    assert set(result) == {SubA, SubB, SubAA, SubAB, SubBA}

def test_all_subclasses_multiple_inheritance():
    class BaseMI:
        pass

    class Mixin:
        pass

    class Sub1(BaseMI):
        pass

    class Sub2(BaseMI, Mixin):
        pass

    class Sub3(Sub2):
        pass

    result = _all_subclasses(BaseMI)
    assert len(result) == 3
    assert set(result) == {Sub1, Sub2, Sub3}

def test_all_subclasses_diamond():
    class BaseDiamond:
        pass

    class Left(BaseDiamond):
        pass

    class Right(BaseDiamond):
        pass

    class Bottom(Left, Right):
        pass

    result = _all_subclasses(BaseDiamond)
    assert len(result) == 3
    assert set(result) == {Left, Right, Bottom}
