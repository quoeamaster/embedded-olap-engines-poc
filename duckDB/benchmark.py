import time
import psutil
import os
import functools

from colorama import Fore, Style, init

init(autoreset=True)

_process = psutil.Process(os.getpid())


def benchmark(func):
    """Measure execution time and memory usage of a function."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Memory before execution
        mem_before = _process.memory_info().rss

        # Track peak RSS during execution
        peak_memory = mem_before
        running = True

        import threading

        def monitor_memory():
            nonlocal peak_memory

            while running:
                try:
                    current = _process.memory_info().rss
                    peak_memory = max(peak_memory, current)
                except psutil.Error:
                    pass

                time.sleep(0.005)

        monitor = threading.Thread(
            target=monitor_memory,
            daemon=True,
        )
        monitor.start()

        # Measure execution time
        start = time.perf_counter()

        try:
            result = func(*args, **kwargs)
        finally:
            elapsed = time.perf_counter() - start

            # Stop monitoring
            running = False
            monitor.join()

            # Memory after execution
            mem_after = _process.memory_info().rss
            peak_memory = max(peak_memory, mem_after)

            # Print statistics
            print_statistics(
                func.__name__,
                elapsed,
                mem_before,
                mem_after,
                peak_memory,
            )

        return result

    return wrapper


def print_statistics(
    name,
    elapsed,
    mem_before,
    mem_after,
    peak_memory,
):
    """Print benchmark results in color."""

    to_mb = 1024 * 1024

    before = mem_before / to_mb
    after = mem_after / to_mb
    peak = peak_memory / to_mb
    delta = (mem_after - mem_before) / to_mb
    peak_delta = (peak_memory - mem_before) / to_mb

    print()
    print(Fore.CYAN + "=" * 50)
    print(Fore.CYAN + f" Benchmark: {name}")
    print(Fore.CYAN + "=" * 50)

    print(
        Fore.GREEN
        + f" Execution time : {elapsed:.4f} seconds"
    )

    print(f" Memory before : {before:.2f} MB")
    print(f" Memory after  : {after:.2f} MB")

    print(
        Fore.YELLOW
        + f" Memory change : {delta:+.2f} MB"
    )

    print(
        Fore.RED
        + f" Peak memory   : {peak:.2f} MB"
    )

    print(
        Fore.RED
        + f" Peak increase : {peak_delta:+.2f} MB"
    )

    print(Fore.CYAN + "=" * 50)
    print()