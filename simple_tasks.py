import threading
import time

"""
Simple Multi-threading Example
============================

Think of it like your brain doing multiple things at once:
- Listening to music
- Writing notes
- Checking your phone

One program, multiple tasks running at the same time!
"""

def listen_to_music():
    """Task 1: Like listening to music"""
    for i in range(5):
        print("🎵 Playing music...")
        time.sleep(1)  # Pretend to listen for 1 second

def take_notes():
    """Task 2: Like writing notes"""
    for i in range(3):
        print("📝 Writing notes...")
        time.sleep(2)  # Takes 2 seconds to write notes

def check_phone():
    """Task 3: Like checking your phone"""
    for i in range(4):
        print("📱 Checking phone...")
        time.sleep(1.5)  # Takes 1.5 seconds to check phone

print("Running tasks one after another (Without Threading):")
print("------------------------------------------------")
# This is like doing one thing at a time
start_time = time.time()

listen_to_music()
take_notes()
check_phone()

print(f"Time taken without threading: {time.time() - start_time:.2f} seconds")

print("\nRunning tasks simultaneously (With Threading):")
print("-------------------------------------------")
# This is like doing multiple things at once
start_time = time.time()

# Create threads for each task
music_thread = threading.Thread(target=listen_to_music)
notes_thread = threading.Thread(target=take_notes)
phone_thread = threading.Thread(target=check_phone)

# Start all tasks at the same time
music_thread.start()
notes_thread.start()
phone_thread.start()

# Wait for all tasks to finish
music_thread.join()
notes_thread.join()
phone_thread.join()

print(f"Time taken with threading: {time.time() - start_time:.2f} seconds")

"""
See the difference?
- Without threading: Tasks run one after another (slower)
- With threading: Tasks run at the same time (faster)

Just like you can listen to music WHILE writing notes!
"""
