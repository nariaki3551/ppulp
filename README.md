# ppulp

P(retty)PuLP is an extension of PuLP, linear programming problem modeling tool.

You can use the basic features of pulp plus the following useful extensions to make modeling simpler.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

<br>

## Install

**PyPI**

```
pip install ppulp
```

**GitHub**

```
git clone https://github.com/nariaki3551/ppulp.git
```

<br>

## Features

- Variable product
- If-then constraints
- Absolute values
- Piecewise linear approximation of nonlinear functions
- Logical operations (And, Or, Xor)
- Reduction (Sum, Prod)


## Examples

### Variables productions

```python
# from pulp import *
from ppulp import *

# create variables
x = LpVariable("x", cat="Binary")
y = LpVariable("y", cat="Binary")

# create variable production
z = x * y
```

### If-then constriant

```python
from ppulp import *

x = LpVariable("x", lowBound=-1)
y = LpVariable("y", lowBound=-1)

prob = LpProblem(sense="Minimize")

# add if-then constraints
prob += (x <= 0) >> (y >= 0)  # if (x <= 0) then (y >= 0)
prob += (y <= 0) >> (x >= 0)  # if (y <= 0) then (x >= 0)
```

### Absolution value

```python
x = LpVariable("x")
y = LpVariable("y")
Abs(x+y)
```

### Approximation of nonlinear functions

```python
from ppulp import *
import math

x = LpVariable("x", lowBound=3)
y = LpVariable("y", lowBound=4)

# create non-linear function
f = PiecewiseLinear(math.log, xl=7, xu=100, num=3)

prob = LpProblem()
prob += f(x + y)
prob += f(x) >= 10
```


### Reduction

```python
from ppulp import *

x = [LpVariable(name=f"x{i}", ini_value=2) for i in range(5)]

# summation
lpSum(x)

# production
lpProd(x)
```
