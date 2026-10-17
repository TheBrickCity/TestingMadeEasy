'''
This file is used to generate student specific rng seeds and to use that seeding
to generate a student's test based off of their name and the test id
'''
from random import Random

import models
import schemas
from problems import REGISTRY


def generate_problems(test: models.Test, seed_key: str) -> list[schemas.GeneratedProblem]:
    results = []
    for number, tp in enumerate(test.problems, start=1):
        problem_type = REGISTRY.get(tp.problem_type)
        if problem_type is None:
            raise ValueError(f"Unknown stored problem type: {tp.problem_type}")

        rng = Random(f"{seed_key}:{tp.id}")
        problem = problem_type.generate(tp.params, rng)
        results.append(
            schemas.GeneratedProblem(
                number=number, question=problem.question, answer=problem.answer
            )
        )
    return results


def student_seed_key(test: models.Test, student_name: str) -> str:
    return f"{test.id}:{student_name.strip()}"