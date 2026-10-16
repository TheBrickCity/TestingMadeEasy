from random import Random

import sympy as sp

from .base import Param, Problem, ProblemType

x = sp.symbols("x")


def random_poly(rng: Random, num_terms: int, exp_max: int, coef_min: int, coef_max: int):
    poly = 0
    for e in rng.sample(range(1, exp_max + 1), num_terms):
        c = 0
        while c == 0:
            c = rng.randint(coef_min, coef_max)
        poly += c * x**e
    return poly

class DerivativePowerRule(ProblemType):
    id = "calculus.derivative.power_rule"
    topic = "Calculus"
    label = "Derivatives: Power Rule"
    params = [
        Param("num_terms", "Number of terms", 3),
        Param("coef_min", "Smallest coefficient", 1),
        Param("coef_max", "Largest coefficient", 9),
        Param("exp_max", "Largest exponent", 5),
    ]

    def check(self, params: dict) -> None:
        if not 1 <= params["num_terms"] <= 10: # 10 can be changed its just a reasonable limit
            raise ValueError("Number of terms must be between 1 and 10")
        if params["exp_max"] < params["num_terms"]:
            raise ValueError("Largest exponent must be at least the number of terms")
        if params["coef_min"] > params["coef_max"]:
            raise ValueError("Smallest coefficient can't be larger than the largest")
        if params["coef_min"] == 0 and params["coef_max"] == 0:
            raise ValueError("Coefficients can't all be zero")

    def generate(self, params: dict, rng: Random) -> Problem:
        f = random_poly(
            rng, params["num_terms"], params["exp_max"],
            params["coef_min"], params["coef_max"],
        )
        question = r"Find $" + sp.latex(sp.Derivative(f, x)) + r"$."
        answer = "$" + sp.latex(sp.diff(f, x)) + "$"
        return Problem(question=question, answer=answer)


class DerivativeProductRule(ProblemType):
    id = "calculus.derivative.product_rule"
    topic = "Calculus"
    label = "Derivatives: Product Rule"
    params = [
        Param("terms_per_factor", "Terms in each factor", 2),
        Param("coef_min", "Smallest coefficient", 1),
        Param("coef_max", "Largest coefficient", 5),
        Param("exp_max", "Largest exponent", 4),
    ]

    def check(self, params: dict) -> None:
        if not 1 <= params["terms_per_factor"] <= 4:
            raise ValueError("Terms per factor must be between 1 and 4")
        if params["exp_max"] < params["terms_per_factor"]:
            raise ValueError("Largest exponent must be at least the terms per factor")
        if params["coef_min"] > params["coef_max"]:
            raise ValueError("Smallest coefficient can't be larger than the largest")
        if params["coef_min"] == 0 and params["coef_max"] == 0:
            raise ValueError("Coefficients can't all be zero")

    def generate(self, params: dict, rng: Random) -> Problem:
        args = (
            params["terms_per_factor"], params["exp_max"],
            params["coef_min"], params["coef_max"],
        )
        f = random_poly(rng, *args)
        g = random_poly(rng, *args)

        question = r"Find $" + sp.latex(sp.Derivative(f * g, x)) + r"$."
        answer = "$" + sp.latex(sp.expand(sp.diff(f * g, x))) + "$"
        return Problem(question=question, answer=answer)