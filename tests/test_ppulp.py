import numpy as np

from ppulp import *


def test_linearize():
    x = LpVariable("x", cat="Binary")
    y = LpVariable("y", cat="Binary")
    z = LpVariable("z", lowBound=2, upBound=4, cat="Integer")

    prob = LpProblem(sense=LpMinimize)
    prob += x * y * z
    prob += x + y >= 2

    prob.solve()
    assert prob.getObjectiveValue() == 2
    assert x.value() == 1
    assert y.value() == 1
    assert z.value() == 2


def test_And():
    x = LpVariable("x", cat="Binary")
    y = LpVariable("y", cat="Binary")

    prob = LpProblem(sense=LpMinimize)
    prob += -And(x, y)

    prob.solve()
    assert prob.getObjectiveValue() == -1
    assert x.value() == 1
    assert y.value() == 1


def test_Or():
    x = LpVariable("x", cat="Binary")
    y = LpVariable("y", cat="Binary")

    prob = LpProblem(sense=LpMinimize)
    prob += Or(x, y)

    prob.solve()
    assert prob.getObjectiveValue() == 0
    assert x.value() == 0 or y.value() == 0


def test_Abs():

    x = LpVariable("x", lowBound=-5, upBound=-1, cat="Integer")

    prob = LpProblem(sense=LpMinimize)
    prob += Abs(x)

    prob.solve()
    assert prob.getObjectiveValue() == 1
    assert x.value() == -1


def test_PiecewiseLinear():
    prob = LpProblem(sense=LpMinimize)
    f = PiecewiseLinear(np.log, 1, 10)  # 1 <= x <= 10
    x = LpVariable("x")
    prob += f(x)
    prob.solve()
    print(x.value())
