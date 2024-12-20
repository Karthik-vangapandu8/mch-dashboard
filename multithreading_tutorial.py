import threading
import time
import queue
from concurrent.futures import ThreadPoolExecutor

"""
Multi-threaded Programming Tutorial
=================================

What is Multi-threading?
-----------------------
Multi-threading is a programming concept where multiple threads (lightweight processes) 
run concurrently within a single program. Each thread represents an independent path 
of execution, allowing different parts of a program to run simultaneously.

Key Concepts:
1. Thread: A lightweight unit of execution within a process
2. Parallelism: Running multiple tasks simultaneously
3. Concurrency: Managing multiple tasks in overlapping time periods
4. Synchronization: Coordinating access to shared resources
5. Thread Safety: Ensuring code works correctly with multiple threads

Benefits:
1. Improved Performance
2. Better Resource Utilization
3. Enhanced Responsiveness
4. Efficient I/O Operations
"""

# Example 1: Basic Threading
def basic_thread_example():
    def worker(thread_id):
        print(f"Thread {thread_id} starting")
        time.sleep(2)  # Simulate some work
        print(f"Thread {thread_id} finished")

    # Create multiple threads
    threads = []
    for i in range(3):
        thread = threading.Thread(target=worker, args=(i,))
        threads.append(thread)
        thread.start()

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

# Example 2: Thread Synchronization with Lock
def thread_synchronization_example():
    counter = 0
    counter_lock = threading.Lock()

    def increment_counter():
        nonlocal counter
        for _ in range(100000):
            with counter_lock:  # Thread synchronization using Lock
                counter += 1

    threads = [
        threading.Thread(target=increment_counter) for _ in range(5)
    ]
    
    for thread in threads:
        thread.start()
    
    for thread in threads:
        thread.join()
        
    print(f"Final counter value: {counter}")

# Example 3: Producer-Consumer Pattern
def producer_consumer_example():
    task_queue = queue.Queue(maxsize=10)
    
    def producer():
        for i in range(5):
            time.sleep(0.5)  # Simulate production time
            task_queue.put(f"Task {i}")
            print(f"Produced: Task {i}")

    def consumer():
        while True:
            try:
                task = task_queue.get(timeout=2)
                time.sleep(1)  # Simulate processing time
                print(f"Consumed: {task}")
                task_queue.task_done()
            except queue.Empty:
                break

    # Create producer and consumer threads
    producer_thread = threading.Thread(target=producer)
    consumer_thread = threading.Thread(target=consumer)

    producer_thread.start()
    consumer_thread.start()

    producer_thread.join()
    consumer_thread.join()

# Example 4: Thread Pool
def thread_pool_example():
    def process_task(task_id):
        print(f"Processing task {task_id}")
        time.sleep(1)
        return f"Result of task {task_id}"

    with ThreadPoolExecutor(max_workers=3) as executor:
        tasks = range(5)
        results = executor.map(process_task, tasks)
        
        for result in results:
            print(result)

# Example 5: Real-world Application - Parallel File Processing
def parallel_file_processing():
    def process_file(filename):
        print(f"Processing file: {filename}")
        time.sleep(1)  # Simulate file processing
        return f"Processed {filename}"

    files = [f"file_{i}.txt" for i in range(5)]
    
    with ThreadPoolExecutor(max_workers=3) as executor:
        future_to_file = {executor.submit(process_file, file): file for file in files}
        
        for future in future_to_file:
            file = future_to_file[future]
            try:
                result = future.result()
                print(result)
            except Exception as e:
                print(f"Error processing {file}: {e}")

if __name__ == "__main__":
    print("\n1. Basic Threading Example:")
    basic_thread_example()

    print("\n2. Thread Synchronization Example:")
    thread_synchronization_example()

    print("\n3. Producer-Consumer Pattern Example:")
    producer_consumer_example()

    print("\n4. Thread Pool Example:")
    thread_pool_example()

    print("\n5. Parallel File Processing Example:")
    parallel_file_processing()

"""
Common Challenges and Best Practices:
-----------------------------------
1. Race Conditions:
   - Use locks, semaphores, or other synchronization mechanisms
   - Be careful with shared resources

2. Deadlocks:
   - Avoid circular dependencies
   - Use timeouts
   - Implement proper lock ordering

3. Thread Safety:
   - Use thread-safe data structures
   - Minimize shared state
   - Use atomic operations when possible

4. Resource Management:
   - Properly close/join threads
   - Use context managers
   - Implement proper error handling

5. Performance Considerations:
   - Don't create too many threads
   - Consider using thread pools
   - Balance thread count with system resources

When to Use Multi-threading:
---------------------------
1. I/O-bound tasks (file operations, network requests)
2. GUI applications (responsive user interface)
3. Parallel processing of independent tasks
4. Background tasks in web applications
5. Real-time data processing

When Not to Use Multi-threading:
------------------------------
1. CPU-bound tasks (use multiprocessing instead)
2. Simple sequential tasks
3. When code complexity outweighs benefits
4. When synchronization overhead is too high
"""
