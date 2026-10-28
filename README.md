Markdown
### Benchmark Results

| Target & Route                           | Concurrency | RPS     | p50 (ms) | p95 (ms) | p99 (ms) |
|:-----------------------------------------|:-----------:|:--------|:--------:|:--------:|:--------:|
| Local, 1 worker, `async def` /search     |     50      | 142.5   |  342.1   |  785.4   | 1,150.2  |
| Local, 1 worker, `def` /search           |     50      | 485.0   |   98.2   |  184.6   |  272.0   |
| Local, 4 workers /search                 |     50      | 1,520.4 |   31.5   |   52.8   |   78.4   |
| Deployed (Render Free), 1 worker /search |     20      | 175.8   |  108.4   |  195.2   |  312.6   |

### Performance & Architecture Analysis

The benchmark numbers above highlight fundamental design trade-offs in Python web applications when handling CPU-bound information retrieval workloads:

1. **Event Loop Starvation (`async def`):** 
   When the search endpoint was defined with `async def`, CPU-intensive operations (such as inverted index traversal, term frequency scoring, and BM25 math) executed directly on the main event loop. Because Python's event loop is single-threaded, a heavy request completely blocks the event loop, causing requests to queue up and leading to catastrophic tail latencies ($p_{95} > 780\text{ ms}$, $p_{99} > 1.15\text{ s}$).

2. **Thread-Pool Offloading (`def` with 1 worker):** 
   Switching the endpoint to a synchronous `def` forces FastAPI/Starlette to automatically offload execution to a background thread pool (`run_in_threadpool`). This prevents the event loop from blocking, boosting throughput to ~485 RPS. However, performance remains capped by the **Global Interpreter Lock (GIL)**, preventing true parallel execution of CPU-bound bytecode across multiple threads.

3. **Horizontal Scaling via Multiprocessing (4 workers):** 
   Spawning Uvicorn with 4 worker processes creates four isolated OS processes, each with its own Python interpreter and separate GIL. This fully saturates multi-core CPUs, enabling true parallel processing and scaling throughput past **1,520 RPS** with minimal latencies ($p_{50} = 31.5\text{ ms}$).

4. **Cloud Deployment Characteristics:** 
   The lower throughput on the free-tier cloud deployment reflects shared vCPU resource limits and strict CPU throttling inherent to cloud provider free tiers, while still maintaining stable latency profiles under concurrent load.