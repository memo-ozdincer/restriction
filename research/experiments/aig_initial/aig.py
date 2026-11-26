"""Exact combinational AIG evaluator. Literals are 2*node + inversion."""
import random


def input_tables(n):
    if not 1 <= n <= 12:
        raise ValueError("expected 1..12 inputs")
    return [0] + [sum(((row >> i) & 1) << row for row in range(1 << n))
                  for i in range(n)]


def evaluate(n, gates, outputs):
    tables = input_tables(n)
    mask = (1 << (1 << n)) - 1

    def literal(x):
        if type(x) is not int or not 0 <= x < 2 * len(tables):
            raise ValueError(f"invalid literal: {x}")
        return tables[x // 2] ^ (mask if x % 2 else 0)

    for pair in gates:
        if not isinstance(pair, list) or len(pair) != 2:
            raise ValueError("expected two operands")
        tables.append(literal(pair[0]) & literal(pair[1]))
    return [literal(x) for x in outputs]


def verify(task, gates, outputs, prefix=None):
    prefix = [] if prefix is None else prefix
    all_gates = prefix + gates
    actual = evaluate(task["inputs"], all_gates, outputs)
    correct = actual == task["target"]
    return {"correct": correct, "gates": len(all_gates),
            "reward": int(correct and len(all_gates) <= task["budget"])}


def random_prefix(n, count, rng):
    return [[rng.randrange(2 * (n + 1 + i)), rng.randrange(2 * (n + 1 + i))]
            for i in range(count)]


class Builder:
    def __init__(self, n):
        self.n = n
        self.gates = []

    def AND(self, a, b):
        self.gates.append([a, b])
        return 2 * (self.n + len(self.gates))

    def OR(self, a, b):
        return self.AND(a ^ 1, b ^ 1) ^ 1

    def XOR(self, a, b):
        return self.OR(self.AND(a, b ^ 1), self.AND(a ^ 1, b))

    def majority(self, a, b, c):
        return self.OR(self.AND(a, b), self.AND(c, self.OR(a, b)))


def target_table(n, function, width):
    values = [function([(row >> i) & 1 for i in range(n)]) for row in range(1 << n)]
    return [sum(((v >> bit) & 1) << row for row, v in enumerate(values))
            for bit in range(width)]


def panel():
    tasks = []

    def add(name, b, outputs, function=None):
        target = evaluate(b.n, b.gates, outputs)
        if function is not None:
            assert target == target_table(b.n, function, len(outputs))
        tasks.append(dict(name=name, inputs=b.n, target=target, budget=len(b.gates),
                          witness={"gates": b.gates, "outputs": outputs}))

    b = Builder(2)
    add("xor2", b, [b.XOR(2, 4)], lambda x: x[0] ^ x[1])
    b = Builder(3)
    add("majority3", b, [b.majority(2, 4, 6)], lambda x: int(sum(x) >= 2))
    for n in (4, 6, 8):
        b = Builder(n)
        out = 2
        for i in range(2, n + 1):
            out = b.XOR(out, 2 * i)
        add(f"parity{n}", b, [out], lambda x: sum(x) % 2)
    for width in (2, 3, 4):
        b = Builder(2 * width)
        carry = 0
        outputs = []
        for i in range(width):
            a, c = 2 * (i + 1), 2 * (width + i + 1)
            p = b.XOR(a, c)
            if i == 0:
                outputs.append(p)
                carry = b.AND(a, c)
            else:
                outputs.append(b.XOR(p, carry))
                carry = b.OR(b.AND(a, c), b.AND(p, carry))
        outputs.append(carry)
        add(f"add{width}", b, outputs,
            lambda x: sum((x[i] + x[width + i]) << i for i in range(width)))
    rng = random.Random(42)
    for i in range(4):
        b = Builder(4)
        b.gates = random_prefix(4, 6 + i, rng)
        add(f"random{i}", b, [2 * (4 + len(b.gates))])
    return tasks
