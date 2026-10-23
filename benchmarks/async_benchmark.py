"""Standalone script comparing synchronous vs. asynchronous execution performance in Graphinate."""

import asyncio
import sys
import time

from loguru import logger

import graphinate
from graphinate.builders import NetworkxBuilder

# Suppress debug logs during performance runs
logger.remove()
logger.add(sys.stderr, level="WARNING")


def benchmark_cpu_in_memory(n_items: int = 10_000) -> tuple[float, float]:
    """Measure pure in-memory execution: sync generator vs async generator."""
    print("\n========================================================")
    print(f" 1. In-Memory CPU-Bound Traversal ({n_items:,} items)")
    print("========================================================")

    # 1. Synchronous
    sync_model = graphinate.model(name="Sync CPU Benchmark")

    @sync_model.node()
    def sync_nodes():
        yield from range(n_items)

    @sync_model.edge()
    def sync_edges():
        for i in range(n_items - 1):
            yield {"source": i, "target": i + 1}

    builder_sync = NetworkxBuilder(sync_model)
    t0 = time.perf_counter()
    g_sync = builder_sync.build()
    t_sync = time.perf_counter() - t0
    n_nodes = len(g_sync.nodes)
    n_edges = len(g_sync.edges)
    print(f"Sync build():                 {t_sync * 1000:7.2f} ms  ({n_nodes:,} nodes, {n_edges:,} edges)")

    # 2. Asynchronous
    async def run_async():
        async_model = graphinate.model(name="Async CPU Benchmark")

        @async_model.node()
        async def async_nodes():
            for i in range(n_items):
                yield i

        @async_model.edge()
        async def async_edges():
            for i in range(n_items - 1):
                yield {"source": i, "target": i + 1}

        t0 = time.perf_counter()
        g_async = await graphinate.abuild(NetworkxBuilder, async_model)
        t_async = time.perf_counter() - t0
        a_nodes = len(g_async.nodes)
        a_edges = len(g_async.edges)
        print(f"Async abuild():               {t_async * 1000:7.2f} ms  ({a_nodes:,} nodes, {a_edges:,} edges)")
        ratio = (t_async / t_sync - 1.0) * 100
        print(f"Async Protocol Overhead:      +{ratio:5.1f}%")
        return t_sync, t_async

    return asyncio.run(run_async())


def benchmark_io_concurrency(
    n_graphs: int = 5,
    batches_per_graph: int = 4,
    latency_per_batch: float = 0.05,
) -> tuple[float, float]:
    """Simulate fetching multiple graphs from remote APIs or databases with network latency."""
    lat_ms = latency_per_batch * 1000
    print("\n========================================================")
    print(f" 2. Concurrent I/O-Bound Traversal ({n_graphs} graphs x {batches_per_graph} batches @ {lat_ms:.0f}ms)")
    print("========================================================")

    # 1. Sequential Sync
    def make_sync_model(idx: int):
        m = graphinate.model(name=f"Sync I/O {idx}")

        @m.node()
        def nodes():
            for b in range(batches_per_graph):
                time.sleep(latency_per_batch)
                for i in range(50):
                    yield f"g{idx}_b{b}_n{i}"

        return m

    t0 = time.perf_counter()
    sync_graphs = []
    for idx in range(n_graphs):
        m = make_sync_model(idx)
        sync_graphs.append(NetworkxBuilder(m).build())
    t_sync = time.perf_counter() - t0
    total_nodes = sum(len(g.nodes) for g in sync_graphs)
    print(f"Sequential Sync build():      {t_sync:7.2f} s   ({n_graphs} graphs, {total_nodes} nodes total)")

    # 2. Concurrent Async
    def make_async_model(idx: int):
        m = graphinate.model(name=f"Async I/O {idx}")

        @m.node()
        async def nodes():
            for b in range(batches_per_graph):
                await asyncio.sleep(latency_per_batch)
                for i in range(50):
                    yield f"g{idx}_b{b}_n{i}"

        return m

    async def run_concurrent():
        t0 = time.perf_counter()
        tasks = [
            graphinate.abuild(NetworkxBuilder, make_async_model(idx))
            for idx in range(n_graphs)
        ]
        async_graphs = await asyncio.gather(*tasks)
        t_async = time.perf_counter() - t0
        total_async_nodes = sum(len(g.nodes) for g in async_graphs)
        speedup = t_sync / t_async
        print(f"Concurrent Async abuild():    {t_async:7.2f} s   ({n_graphs} graphs, {total_async_nodes} nodes total)")
        print(f"Async Concurrency Speedup:    {speedup:7.2f}x faster")
        return t_sync, t_async

    return asyncio.run(run_concurrent())


if __name__ == "__main__":
    benchmark_cpu_in_memory(n_items=20_000)
    benchmark_io_concurrency(n_graphs=5, batches_per_graph=4, latency_per_batch=0.05)
