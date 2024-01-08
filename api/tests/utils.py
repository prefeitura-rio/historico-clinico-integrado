# -*- coding: utf-8 -*-
import random


def generate_cpf():
    cpf = [random.randint(0, 9) for x in range(9)]

    for _ in range(2):
        val = sum([(len(cpf) + 1 - i) * v for i, v in enumerate(cpf)]) % 11

        cpf.append(11 - val if val > 1 else 0)

    cpf = [str(x) for x in cpf]

    return "".join(cpf)


def generate_cns():
    cns = [random.randint(0, 9) for x in range(16)]
    cns = [str(x) for x in cns]

    return "".join(cns)
