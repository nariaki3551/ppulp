import types

import numpy as np
import flopt
from flopt import Variable, Sum, Dot, VarContinuous, VarBinary
from flopt.constants import SolverTerminateState, array_classes
from flopt.env import create_variable_mode, is_create_variable_mode, get_variable_id


def maxValue(exp):
    """Calculate max value of expression

    Parameters
    ----------
    exp : flopt.ExpresionElement or flopt.VarElement

    Returns
    -------
    float or str
        maximum value of this expression can take
    """
    if exp.isLinear():
        solver = flopt.Solver("ScipyMilpSearch")
    elif exp.isQuadratic():
        solver = flopt.Solver("CvxoptQpSearch")
    else:
        return "Unknown"
    prob = flopt.Problem(sense=flopt.Maximize)
    prob += exp
    status, logs = prob.solve(solver, msg=False)
    if status == SolverTerminateState.Normal:
        return prob.getObjectiveValue()
    elif status == SolverTerminateState.Unbounded:
        return "Unbounded"
    else:
        return "Unknown"


def minValue(exp):
    """Calculate max value of expression

    Parameters
    ----------
    exp : flopt.ExpresionElement or flopt.VarElement

    Returns
    -------
    float or str
        minimum value of this expression can take
    """
    if exp.isLinear():
        solver = flopt.Solver("ScipyMilpSearch")
    elif exp.isQuadratic():
        solver = flopt.Solver("CvxoptQpSearch")
    else:
        return "Unknown"
    prob = flopt.Problem(sense=flopt.Minimize)
    prob += exp
    status, logs = prob.solve(solver, msg=False)
    if status == SolverTerminateState.Normal:
        return prob.getObjectiveValue()
    elif status == SolverTerminateState.Unbounded:
        return "Unbounded"
    else:
        return "Unknown"


class VarElementWithConsts:
    """VarElemet class has constrains

    Attributes
    ----------
    constrains : list of flopt.Constraint
    add_consts_prob : set of LpProblem
    """

    def hasAddConsts(self, prob):
        return prob in self.add_consts_prob

    def addConstsTo(self, prob):
        """add constraints to problem

        Parameters
        ----------
        prob : LpProblem
            problem
        """
        if not self.hasAddConsts(prob):
            self.add_consts_prob.add(prob)
            prob.addConstraints(self.constraints)


class VarContinuousWithConsts(flopt.variable.VarContinuous, VarElementWithConsts):
    def __init__(self, name, *args, **kwargs):
        self.constraints = list()
        self.add_consts_prob = set()
        if is_create_variable_mode():
            assert name is not None
            name = f"__{get_variable_id()}_" + name
        super().__init__(name, *args, **kwargs)


class VarBinaryWithConsts(flopt.variable.VarBinary, VarElementWithConsts):
    def __init__(self, name, *args, **kwargs):
        self.constraints = list()
        self.add_consts_prob = set()
        if is_create_variable_mode():
            assert name is not None
            name = f"__{get_variable_id()}_" + name
        super().__init__(name, *args, **kwargs)


def And(x, y):
    """x & y

    Parameters
    ----------
    x : flopt.VarBinary
    y : flopt.VarBinary

    Returns
    -------
    VarBinaryWithConsts
    """
    assert isinstance(x, flopt.variable.VarBinary) and isinstance(
        y, flopt.variable.VarBinary
    )

    with create_variable_mode():
        z = VarBinaryWithConsts("and")

    z.constraints = [
        x + y - 1 <= z,
        x >= z,
        y >= z,
    ]

    return z


def Or(x, y):
    """x | y

    Parameters
    ----------
    x : flopt.VarBinary
    y : flopt.VarBinary

    Returns
    -------
    VarBinaryWithConsts
    """
    assert isinstance(x, flopt.variable.VarBinary) and isinstance(
        y, flopt.variable.VarBinary
    )

    with create_variable_mode():
        z = VarBinaryWithConsts("or")

    z.constraints = [
        x + y >= z,
        x <= z,
        y <= z,
    ]

    return z


def Xor(x, y):
    """x ^ y

    Parameters
    ----------
    x : flopt.VarBinary
    y : flopt.VarBinary

    Returns
    -------
    VarBinaryWithConsts
    """
    assert isinstance(x, flopt.variable.VarBinary) and isinstance(
        y, flopt.variable.VarBinary
    )

    with create_variable_mode():
        z = VarBinaryWithConsts("xor")

    z.constraints = [
        x + y >= z,
        x - y <= z,
        -x + y <= z,
        x + y - 2 <= -z,
    ]

    return z


def Abs(x):
    """Absolute variable

    Parameters
    ----------
    x : flopt.VarElement

    Returns
    -------
    VarBinaryWithConsts
    """

    with create_variable_mode():
        y = VarContinuousWithConsts(
            "abs",
            lowBound=0,
            upBound=None,
            ini_value=abs(x.value()),
        )

    y.constraints = [
        y >= x,
        y >= -x,
    ]

    return y


class PiecewiseLinear:
    """Non linear function approximator

    .. code-block:: python

        from ppulp import *
        import math

        prob = LpProblem(sense="Minimize")

        x = LpVariable("x", lowBound=3, cat="Continuous")
        y = LpVariable("y", lowBound=4, cat="Continuous")

        f = PiecewiseLinear(math.log, xl=7, xu=100, num=3)

        prob += f(x + y)
        prob += f(x) >= 10

    Parameters
    ----------
    f : function
        python function return the value
    xl : float
        lower bound of domain
    xu : float
        upper bound of domain
    num : int
        number of samples
    """

    def __init__(self, f, xl, xu, num=10):
        self.f = f
        self.xl = xl
        self.xu = xu
        self.num = num

    def __call__(self, x):
        name = "PL"
        n = self.num
        x_points = np.linspace(self.xl, self.xu, n)
        y_points = [self.f(xi) for xi in x_points]

        with create_variable_mode():
            y = VarContinuousWithConsts(f"y_{name}")
            t = Variable.array(f"t_{name}", n, lowBound=0)

        y.constraints = [
            x == Dot(t, x_points),
            y == Dot(t, y_points),
            Sum(t) == 1,
        ]

        # SOS2
        with create_variable_mode():
            z = Variable.array(f"z_{name}", n - 1, cat=VarBinary)

        y.constraints += [Sum(z) == 1]
        y.constraints += [t[0] <= z[0]]
        y.constraints += [t[i] <= z[i - 1] + z[i] for i in range(1, n - 2)]
        y.constraints += [t[n - 1] <= z[n - 2]]

        return y
