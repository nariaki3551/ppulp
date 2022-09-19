Tutorial
========

.. contents::
    :depth: 2

Variable product
----------------

Often variable products appear in the formulation of optimization problems.

Notation
^^^^^^^^

The creation of an object representing a variable product is simply the product of a variable or expression object.

::

  (variable or expression) * (variable or expression)

Example
^^^^^^^

The following is the simple example of problem using variable product.

.. code-block:: python

  """
  maximize z
  s.t.     z = x * y
  """

  from ppulp import *
  
  # create variables
  x = LpVariable("x", cat="Binary")
  y = LpVariable("y", cat="Binary")

  # create variable production
  z = x * y
  
  # create problem
  prob = LpProblem(sense="Maximize")
  prob += z

  # solve
  status = prob.solve(msg=True)

  # show status of solving
  print(LpStatus[status])

  # show the objective value and solutions
  print("objective value", value(prob.objective))
  print("x", value(x))
  print("y", value(y))
  
In ppulp, the linearization process is performed when we call the solve() function.
To understand this process, let us observe the problem performed the linearization function.

.. code-block:: python

  prob.linearize()  # linearize
  print(prob.show())  # show the problem information

  >>> Name: None
  >>>   Type         : Problem
  >>>   sense        : Maximize
  >>>   objective    : __25_mul
  >>>   #constraints : 3
  >>>   #variables   : 3 (Binary 3)
  >>> 
  >>>   C 0, name for___0_mul_1, __0_mul-x <= 0
  >>>   C 1, name for___0_mul_2, __0_mul-y <= 0
  >>>   C 2, name for___0_mul_3, x+y-1-__0_mul <= 0

A variable `__0_mul` has created, which corresponds to the variable :math:`z = x y`.

Generally, when we formulate the following problem, we use `lpProd` function.


.. code-block:: python

  """
  maximize z
  s.t.     z = x_1 * x_2 * ... * x_n
  """

  from ppulp import *
  
  n = 4
  x = LpVariable.array("x", n, cat="Binary")  # create variable array whose length is n
  # x = [LpVariable(f"x{i}", cat="Binary") for i in range(n)]  # is same above
  
  prob = LpProblem(sense="Maximize")
  prob += lpProd(x)
  
  print(prob.show())

  >>> Name: None
  >>>   Type         : Problem
  >>>   sense        : Maximize
  >>>   objective    : x_0*x_1*x_2*x_3
  >>>   #constraints : 0
  >>>   #variables   : 4 (Binary 4)

If-then constraint
------------------

ppulp also supports if-then constraints such as :math:`y >= 0` must be satisfied only when :math:`x >= 0` is satisfied.

Notation
^^^^^^^^

The notation of adding constraint B if constraint A is satisfied is as follows.

::

  (constraint A) >> (constraint B)
  
Both equality and inequality constraints both can be used as A and B.

.. note::

  If-then constraints cause an error of 1e-5 per variable. That is, if x = 1 is the optimal solution, there will be an error of :math:`x = 1 \pm 10^{-5}`.

Example 1
^^^^^^^^^

.. code-block:: python

  """
  maximize x + y
  s.t.     x <= 0  -->  y >= 0
           y <= 0  -->  x >= 0
           x >= -1
           y >= -1
  """

  x = LpVariable("x", lowBound=-1)
  y = LpVariable("y", lowBound=-1)
  
  prob = LpProblem(sense="Minimize")
  prob += x + y

  # add if-then constraints
  prob += (x <= 0) >> (y >= 0)
  prob += (y <= 0) >> (x >= 0)
  

Example 2
^^^^^^^^^

.. code-block:: python

  """
  maximize x + y
  s.t.     x == 0  -->  y >= 2
           x == 1  -->  y >= 0
           y >= -2
           x in {0, 1}
  """

  from ppulp import *

  x = LpVariable("x", cat="Binary")
  y = LpVariable("y", lowBound=-1)
  
  prob = LpProblem(sense="Minimize")
  prob += x + y

  # add if-then constraints
  prob += (x == 0) >> (y >= 2)
  prob += (x == 1) >> (y >= 0)
  

Absolution value
----------------

Notation
^^^^^^^^

::
  
  ppulp.Abs(variable or expression)

Example
^^^^^^^

.. code-block:: python

  """
  minimize Abs(x+y)
  s.t.     x >= 3
           y >= -4
  """

  from ppulp import *
  
  x = LpVariable("x", lowBound=3)
  y = LpVariable("y", lowBound=-4)
  
  prob = LpProblem()
  prob += Abs(x+y)
  

Approximation of nonlinear functions
------------------------------------

ppulp allows you to approximate nonlinear functions such as log, x^2, and so on. `PiecewiseLinear` is used to create functions like object.

Notation
^^^^^^^^

::

  f = PiecewiseLinear(function, xl=(lower bound of domain), xu=(upper bound of domain), num=(number os samples))

This will approximate :math:`f(x)` in the domain of the function :math:`xl <= x <= xu`, and `num` is the number of sample points to approximate.
The larger `num`, the more accurate the approximation, but at the same time, the more slack variables and constraints are created and added to the problem.



Example
^^^^^^^

.. code-block:: python

  """
  minimize log(x + y)
  s.t.     log(x) >= 10
  s.t.     x >= 3
           y >= 4
  """
  
  from ppulp import *
  import math
  
  x = LpVariable("x", lowBound=3)
  y = LpVariable("y", lowBound=4)
  
  # create non-linear function
  f = PiecewiseLinear(math.log, xl=7, xu=100, num=3)
  
  prob = LpProblem()
  prob += f(x + y)
  prob += f(x) >= 10


.. note::

  xl and xu are currently need to be provided by the user.
  It is usefull to use `maxValue` and `minValue` to determin the xl and xu.
  These return the maximum and minimum values that the expression can take.

  >>> from ppulp import maxValue, minValue
  >>> print(maxValue(x+y))
  >>> print(minValue(x+y))


Logic operation
---------------

Binary variables can be regarded as logical values because binary variables take only two values, 0 or 1.

And, Or, Xor
^^^^^^^^^^^^

.. code-block:: python

  from ppulp import *

  x = LpVariable("x", cat="Binary")
  y = LpVariable("y", cat="Binary")
  z = And(x, y)
  z = Or(x, y)
  z = Xor(x, y)


Reduction
---------

Summation
^^^^^^^^^

:math:`\sum_i x_i`

Notaion
~~~~~~~

::

  lpSum(list, iteragor or generator of variable or expression)


.. code-block:: python

  from ppulp import *
  
  x = [LpVariable(name=f"x{i}", ini_value=2) for i in range(5)]
  print(lpSum(x))


Production
^^^^^^^^^^

:math:`\prod_i x_i`

Notaion
~~~~~~~

::

  lpProd(list, iteragor or generator of variable or expression)


.. code-block:: python

  from ppulp import *
  
  x = [LpVariable(name=f"x{i}", ini_value=2) for i in range(5)]
  print(lpProd(x))



