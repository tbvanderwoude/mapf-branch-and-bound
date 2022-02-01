from copy import copy, deepcopy
from typing import Optional
from ortools.linear_solver import pywraplp

from mapf_branch_and_bound.assignment_problem import AssignmentProblem
from ortools.graph import pywrapgraph
from ortools.linear_solver import pywraplp


def solve_problem(costs, problem: AssignmentProblem) -> int:
    rows = len(costs)
    cols = len(costs[0])

    assignment = pywrapgraph.LinearSumAssignment()
    for worker in range(rows):
        for task in problem.team_tasks[problem.team_ids[worker]]:
            assignment.AddArcWithCost(worker, task, costs[worker][task])
    solve_status = assignment.Solve()
    if solve_status == pywraplp.Solver.OPTIMAL:
        total_cost = assignment.OptimalCost()
        return total_cost
    elif solve_status == assignment.INFEASIBLE:
        print("No assignment is possible.")
    elif solve_status == assignment.POSSIBLE_OVERFLOW:
        print("Some input costs are too large and may cause an integer overflow.")


if __name__ == "__main__":
    costs = [
        [90, 80, 75, 70],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
    ]
    team_id = [0, 1, 1, 1]
    team_tasks = [{0, 1, 2, 3}, {2}, {3}]
    problem = AssignmentProblem(team_id, team_tasks, 3, 4, 4)
    solve_problem(costs, problem)
    for subproblem in problem.generate_subproblems():
        print(subproblem)
        solve_problem(costs, subproblem)
