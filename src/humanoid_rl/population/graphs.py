from __future__ import annotations

from collections import deque


def make_graph(num_nodes: int, graph_type: str) -> dict[int, set[int]]:
    if num_nodes <= 0:
        raise ValueError("num_nodes must be positive")
    graph = {i: set() for i in range(num_nodes)}
    if graph_type == "complete":
        for i in range(num_nodes):
            graph[i].update(j for j in range(num_nodes) if j != i)
    elif graph_type == "ring":
        if num_nodes > 1:
            for i in range(num_nodes):
                graph[i].add((i - 1) % num_nodes)
                graph[i].add((i + 1) % num_nodes)
    elif graph_type == "line":
        for i in range(num_nodes - 1):
            graph[i].add(i + 1)
            graph[i + 1].add(i)
    elif graph_type == "star":
        for i in range(1, num_nodes):
            graph[0].add(i)
            graph[i].add(0)
    else:
        raise ValueError(f"Unsupported graph type '{graph_type}'.")
    return graph


def gamma_neighborhoods(graph: dict[int, set[int]], gamma: int) -> dict[int, set[int]]:
    if gamma < 0:
        raise ValueError("gamma must be non-negative")
    neighborhoods: dict[int, set[int]] = {}
    for src in graph:
        seen = {src}
        q = deque([(src, 0)])
        while q:
            node, dist = q.popleft()
            if dist == gamma:
                continue
            for nxt in graph[node]:
                if nxt not in seen:
                    seen.add(nxt)
                    q.append((nxt, dist + 1))
        neighborhoods[src] = seen
    return neighborhoods
