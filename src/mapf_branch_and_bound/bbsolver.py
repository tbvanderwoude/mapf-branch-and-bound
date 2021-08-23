import heapq
from typing import List, Set, Optional, Callable

from mapfmclient import Problem, Solution, MarkedLocation

from .bbnode import BBNode
from .assignment_solver import solve_problem
from .assignment_problem import AssignmentProblem
from mapf_util.astar import astar
from mapf_util.maze import Maze
from mapf_util.compact_location import MarkedCompactLocation, compact_location

# Stand-alone generator of assignments in increasing order of cost
def murty_gen(costs, root):
    ls: List[BBNode] = [root]
    heapq.heapify(ls)
    seen: Set[BBNode] = set()
    while ls:
        n: BBNode = heapq.heappop(ls)
        if n not in seen:
            seen.add(n)
            if n.is_leaf():
                yield n
            else:
                children = n.problem.generate_subproblems()
                if len(children) == 1:
                    heapq.heappush(ls, BBNode(n, children[0], n.lower_bound))
                else:
                    for sub_problem in n.problem.generate_subproblems():
                        sub_cost = solve_problem(costs, sub_problem)
                        heapq.heappush(ls, BBNode(n, sub_problem, sub_cost))
        else:
            print("Already seen?")


# Constructs a branch-and-bound root node
def create_root(agents, goals, costs, K, k) -> BBNode:
    team_id = [x[1] for x in agents]
    team_tasks = [
        set([g[0] for g in enumerate(goals) if g[1][1] == team]) for team in range(K)
    ]
    root_problem = AssignmentProblem(team_id, team_tasks, K, k, k)
    print("Computing BB root cost")
    root_cost = solve_problem(costs, root_problem)
    root = BBNode(None, root_problem, root_cost)
    return root


# High-level function that takes an existing (bounded) MAPFM solver and uses it in a branch-and-bound approach
def solve_bb(
    problem: Problem, solver: Callable[[Problem, Optional[int]], Optional[Solution]]
):
    # translates MAPFM problem to assignment problem (relaxation)
    k = len(problem.starts)
    # makes sure that the K teams are numbered without gaps as 0...(K-1)
    reverse_map = enumerate(sorted(set(map(lambda x: x.color, problem.starts))))
    color_map = dict([(sub[1], sub[0]) for sub in reverse_map])
    K = len(color_map)
    agents: List[MarkedCompactLocation] = list(
        map(
            lambda marked: (
                compact_location(marked.x, marked.y),
                color_map[marked.color],
            ),
            problem.starts,
        )
    )
    goals: List[MarkedCompactLocation] = list(
        map(
            lambda marked: (
                compact_location(marked.x, marked.y),
                color_map[marked.color],
            ),
            problem.goals,
        )
    )
    maze: Maze = Maze(problem.grid, problem.width, problem.height)
    print("Computing shortest paths")
    costs = [[0 for _ in range(k)] for _ in range(k)]
    for (i, (al, ac)) in enumerate(agents):
        for (j, (gl, gc)) in enumerate(goals):
            if ac == gc:
                shortest_path = astar(maze, al, gl)
                c = len(shortest_path) - 1
                costs[i][j] = c

    root: BBNode = create_root(agents, goals, costs, K, k)

    min_sic = None
    min_sol = None
    print("Generating bb nodes")

    ls: List[BBNode] = [root]
    heapq.heapify(ls)
    seen: Set[BBNode] = set()

    leaf_p_goals = list(
        map(
            lambda marked: MarkedLocation(
                x=marked[1].x, y=marked[1].y, color=marked[0]
            ),
            enumerate(problem.goals),
        )
    )

    while ls:
        n: BBNode = heapq.heappop(ls)
        if n not in seen and (not min_sol or n.lower_bound < min_sic):
            seen.add(n)
            if n.is_leaf():
                print(n.problem.assignments, n.lower_bound, min_sic)
                leaf_p_agents = list(
                    map(
                        lambda marked: MarkedLocation(
                            x=marked[1].x, y=marked[1].y, color=marked[0]
                        ),
                        zip(n.problem.assignments, problem.starts),
                    )
                )
                leaf_p: Problem = Problem(
                    problem.grid,
                    problem.width,
                    problem.height,
                    leaf_p_agents,
                    leaf_p_goals,
                )
                sol: Solution = solver(leaf_p, min_sic)
                if sol:
                    c: int = compute_sol_cost(sol)
                    if not min_sic or min_sic > c:
                        min_sol = sol
                        min_sic = c
            else:
                children = n.problem.generate_subproblems()
                if len(children) == 1:
                    heapq.heappush(ls, BBNode(n, children[0], n.lower_bound))
                else:
                    for sub_problem in n.problem.generate_subproblems():
                        sub_cost = solve_problem(costs, sub_problem)
                        if not min_sol or sub_cost < min_sic:
                            heapq.heappush(ls, BBNode(n, sub_problem, sub_cost))
    return min_sol


# Computes the SIC of a solution
# Differs k from an alternative definition
def compute_sol_cost(sol: Solution) -> int:
    sic = 0
    for path in sol.paths:
        xs = path.route
        last = xs[-1]
        while xs[-1] == last:
            xs = xs[:-1]
        sic += len(xs)
    return sic
