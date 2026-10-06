from collections import defaultdict

import numpy as np


class UnionFind:
    def __init__(self):
        self.parent = {}

    def find(self, x):
        if self.parent.setdefault(x, x) != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]

    def union(self, x, y):
        self.parent[self.find(x)] = self.find(y)


# def merge_attractors(attractors):
#     attractor_sets = [set(attractor) for attractor in attractors]
#     uf = UnionFind()

#     for attractor in attractor_sets:
#         it = iter(attractor)
#         first = next(it)

#         for item in it:
#             uf.union(first, item)

#     merged_attractors = defaultdict(set)
#     for attractor in attractor_sets:
#         for state in attractor:
#             root = uf.find(state)
#             merged_attractors[root].add(state)

#     return [np.array(list(merged_attractor)) for merged_attractor in merged_attractors.values()]

# def merge_attractors(data, threshold=0.15):
#     attractors = set()

#     trajectory_len = len(data)
#     trajectory_count = len(data[0])
#     #state_size = len(data[0][0])

#     for trajectory in range(trajectory_count):
#         histogram = defaultdict(int)
#         for step in range(trajectory_len):
#             histogram[tuple(*data[step][trajectory])] += 1

#         attractors.update([node for node in histogram if histogram[node] >= threshold * trajectory_len])
#         attractors.add(tuple(*data[-1][trajectory]))

#     return [np.array(x) for x in attractors]


def merge_attractors(data, threshold=0.15):
    attractors = set()

    trajectory_len = len(data)
    trajectory_count = len(data[0])
    #state_size = len(data[0][0])

    histogram = defaultdict(int)
    for trajectory in range(trajectory_count):
        for step in range(trajectory_len):
            histogram[tuple(*data[step][trajectory])] += 1

        attractors.update([node for node in histogram if histogram[node] >= threshold * trajectory_len])
        # Potentially to be condsidered as an addition to the pseudo-attractor identification method:
        # attractors.add(tuple(*data[-1][trajectory]))

    return [np.array(x) for x in attractors]
