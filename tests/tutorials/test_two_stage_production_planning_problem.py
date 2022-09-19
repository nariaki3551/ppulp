import numpy as np

from ppulp import *


def test_two_stage_production_planning_problem():
    r"""
    Author: Louis Luangkesorn <lugerpitt@gmail.com> 2019
    https://github.com/lluang

    Title: Gemstone Optimization problem

    Problem taken from Data, Models, and Decisions by Bertsimas and Freund, 4th Edition
    DMD 7.2

    ## 2 stage problem

    - **Scenarios:** $s \in S = (1, 2, 3, 4)$
    - **Probability scenario occuring:** $p^s$
    - **Cost of steel:** $c$
    - **Total steel:** $cap_{steel}$
    - **Total molding and assembly hours:** $cap_{molding}, cap_{assembly}^s$
    - **Wrench and plier earnings by scenario:** $w^s, p^s$
    - **Max demand wrenches and pliers:** $UB_w, UB_p$
    - **Decision variables**
      - $(W_{t+1}^s, P_{t+1}^s)$
    - **Objective**   $Max \sum_s (p^s * (w^s W_{t+1}^s + p^s P_{t+1}^s) - c$
    - **Steel Constraint:** $1.5W_{t+1}^1 + P_{t+1}^1 - C \le 0$
    - **Molding Constraint:** $W_{t+1}^1 + P_{t+1}^1 \le cap_{molding}$
    - **Assembly Constraint:** $0.3 W_{t+1}^1 + 0.5 P_{t+1}^1  \le cap_{molding}^s$
    - **Demand Limit W:** $W \le UB_w$
    - **Demand Limit P:** $P \le UB_p$
    - **Nonnegativity:** $W, P \ge 0$
    """

    # parameters
    products = ["wrenches", "pliers"]
    price = [130, 100]
    steel = [1.5, 1]
    molding = [1, 1]
    assembly = [0.3, 0.5]
    capsteel = 27
    capmolding = 21
    LB = [0, 0]
    capacity_ub = [15, 16]
    steelprice = 58
    scenarios = [0, 1, 2, 3]
    pscenario = [0.25, 0.25, 0.25, 0.25]
    wrenchearnings = [160, 160, 90, 90]
    plierearnings = [100, 100, 100, 100]
    capassembly = [8, 10, 8, 10]

    production = [(j, i) for j in scenarios for i in products]
    pricescenario = [[wrenchearnings[j], plierearnings[j]] for j in scenarios]
    priceitems = [item for sublist in pricescenario for item in sublist]

    # create dictionaries for the parameters
    price_dict = dict(zip(production, priceitems))
    capacity_dict = dict(zip(products, capacity_ub * 4))
    steel_dict = dict(zip(products, steel))
    molding_dict = dict(zip(products, molding))
    assembly_dict = dict(zip(products, assembly))

    # Create variables and parameters as dictionaries
    production_vars = LpVariable.dicts(
        "production", (scenarios, products), lowBound=0, cat="Continuous"
    )
    steelpurchase = LpVariable("steelpurchase", lowBound=0, cat="Continuous")

    # Create the 'gemstoneprob' variable to specify
    gemstoneprob = LpProblem("The_Gemstone_Tool_Problem", LpMaximize)

    # The objective function is added to 'gemstoneprob' first
    gemstoneprob += (
        lpSum(
            np.array(
                [
                    pscenario[j] * (price_dict[(j, i)] * production_vars[j][i])
                    for (j, i) in production
                ],
                dtype=object,
            )
            - steelpurchase * steelprice
        ),
        "Total cost",
    )

    for j in scenarios:
        gemstoneprob += lpSum(
            [steel_dict[i] * production_vars[j][i] for i in products]
        ) - steelpurchase <= 0, ("Steel_capacity" + str(j))
        gemstoneprob += lpSum(
            [molding_dict[i] * production_vars[j][i] for i in products]
        ) <= capmolding, ("molding_capacity" + str(j))
        gemstoneprob += lpSum(
            [assembly_dict[i] * production_vars[j][i] for i in products]
        ) <= capassembly[j], ("assembly_capacity" + str(j))
        for i in products:
            gemstoneprob += production_vars[j][i] <= capacity_dict[i], (
                "capacity_" + str(i) + str(j)
            )

    # Print problem
    print(gemstoneprob)

    # The problem data is written to an .lp file
    gemstoneprob.writeLP("gemstoneprob.lp")
    # The problem is solved using PuLP's choice of Solver
    gemstoneprob.solve()
    # The status of the solution is printed to the screen
    print("Status:", LpStatus[gemstoneprob.status])

    # OUTPUT

    # Each of the variables is printed with it's resolved optimum value
    for v in gemstoneprob.variables():
        print(v.name, "=", v.value())
    production = [v.varValue for v in gemstoneprob.variables()]

    # The optimised objective function value is printed to the console
    print("Total price = ", value(gemstoneprob.objective))
