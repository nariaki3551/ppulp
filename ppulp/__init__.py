import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "../flopt"))
sys.path.append(os.path.join(os.path.dirname(__file__), "../pulp"))

from flopt.variable import VarElement


@property
def varValue(self):
    return self.value()


VarElement.varValue = varValue


from flopt import Variable as LpVariable
from flopt import Minimize as LpMinimize
from flopt import Maximize as LpMaximize
from flopt import VarContinuous as LpContinuous
from flopt import VarInteger as LpInteger
from flopt import VarBinary as LpBinary
from flopt import Value as value
from flopt import Sum as lpSum
from flopt import Prod as lpProd

from pulp import LpStatus, makeDict, allcombinations

from ppulp.problem import LpProblem
from ppulp.utils import (
    And,
    Or,
    Xor,
    Abs,
    PiecewiseLinear,
    maxValue,
    minValue,
)
