import pulp

from flopt import Problem
from flopt import Minimize
from flopt.convert.linearize import linearize
from flopt.convert._pulp import flopt_to_pulp

from ppulp.utils import VarElementWithConsts


class LpProblem(Problem):
    """Problem for linear programming

    .. code-block:: python

        from ppulp import *

        prob = LpProblem(sense=Lp.Maximize)

        x = LpVariable("x", cat="Binary")
        y = LpVariable("y", cat="Binary")
        z = x * y

        prob += z

    We can check the details of problem.

    .. code-block:: python

        print(prob.show())
        >>> Name: None
        >>>   Type         : Problem
        >>>   sense        : Maximize
        >>>   objective    : x*y
        >>>   #constraints : 0
        >>>   #variables   : 2 (Binary 2)

    We solve the problem with standard output.

    .. code-block:: python

        prob.solve(msg=True)

    Parameters
    ----------
    name : str
        name of problem
    sense : OptimizationType or str {"Minimize", "Maximize"}

    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pulp_lp = None
        self.pulp_vars = None
        self.has_set_pulp_lp = True
        self.status = None

    def solve(self, **kwargs):
        """solve this problem.

        We can use arguments same as PULP_CBC_CMD of pulp.
        `https://coin-or.github.io/pulp/technical/solvers.html#pulp.apis.PULP_CBC_CMD` shows the details of the arguments.
        """
        if self.has_set_pulp_lp:
            self.set_pulp()
            self.has_set_pulp_lp = False

        # solve
        try:
            self.status = self.pulp_lp.solve(**kwargs)
        except TypeError:
            solver = pulp.PULP_CBC_CMD(**kwargs)
            self.status = self.pulp_lp.solve(solver=solver)

        # decode result
        var_dict = {var.name: var for var in self.getVariables()}

        for pulp_var in self.pulp_vars:
            value = pulp_var.getValue()
            var_dict[pulp_var.name].setValue(value)
        return self.status

    def linearize(self):
        """linearize objective and constraints function"""
        linearize(self)

    def set_pulp(self):
        linearize(self)
        self.pulp_lp, self.pulp_vars = flopt_to_pulp(self)

    def setObjective(self, obj, *args, **kwargs):
        self.has_set_pulp_lp = True
        super().setObjective(obj, *args, **kwargs)
        for elm in obj.traverse():
            if isinstance(elm, VarElementWithConsts):
                elm.addConstsTo(self)

    def addConstraint(self, const, *args, **kwargs):
        self.has_set_pulp_lp = True
        super().addConstraint(const, *args, **kwargs)
        for elm in const.expression.traverse():
            if isinstance(elm, VarElementWithConsts):
                elm.addConstsTo(self)

    def variables(self):
        return self.getVariables()

    @property
    def objective(self):
        return self.obj

    def writeLP(self, *args, **kwargs):
        """overwarp of pulp.LpProblem.writeLP"""
        if self.has_set_pulp_lp:
            self.set_pulp()
        self.pulp_lp.writeLP(*args, **kwargs)

    def writeMPS(self, *args, **kwargs):
        """overwarp of pulp.LpProblem.writeMPS"""
        if self.has_set_pulp_lp:
            self.set_pulp()
        self.pulp_lp.writePS(*args, **kwargs)
