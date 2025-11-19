import time
import queue
import threading

BUCKET_CAPACITY = 10  # Max requests the bucket can hold
LEAK_RATE = 1  # Seconds between requests processing (was 1000ms)

class LeakyBucket:
    def __init__(self, capacity):
        # Python's queue.Queue is thread-safe and handles size limits
        self.requests = queue.Queue(maxsize=capacity)

    def add_request(self, request_id):
        try:
            # non_blocking=True raises queue.Full if capacity is reached
            self.requests.put_nowait(request_id)
            print(f'📥 Request {request_id} added.')
            return True
        except queue.Full:
            print(f'❌ Bucket full. Request {request_id} dropped.')
            return False

    def process_request(self):
        try:
            # non_blocking=True raises queue.Empty if no items are present
            request_id = self.requests.get_nowait()
            print(f'✅ Processing Request {request_id}')
            # Mark the task as done for proper queue management
            self.requests.task_done() 
            return True
        except queue.Empty:
            return False

# Initialize the bucket
leaky_bucket = LeakyBucket(BUCKET_CAPACITY)

def handle_incoming_request(request_id):
    if not leaky_bucket.add_request(request_id):
        print('Request could not be processed. Try again later.')

def start_processing_loop():
    """
    This function runs in a separate thread to simulate the JavaScript setInterval
    leaking/processing requests at the defined LEAK_RATE.
    """
    while True:
        # Process one item every LEAK_RATE seconds
        if not leaky_bucket.process_request():
            # Optional: if the bucket is empty, we could sleep less time or break
            pass 
        time.sleep(LEAK_RATE)

# To run this example in a single script:

if __name__ == "__main__":
    # Start the background processing thread
    processor_thread = threading.Thread(target=start_processing_loop, daemon=True)
    processor_thread.start()

    # Simulate incoming requests over time in the main thread
    import random
    for i in range(20):
        handle_incoming_request(f'req-{i}')
        # Simulate variable arrival times
        time.sleep(random.uniform(0.1, 0.5))

    # Keep the main thread alive long enough to process the queue
    print("\nFinished sending requests. Waiting for queue to empty...")
    leaky_bucket.requests.join() # Wait until all queued tasks are processed
    print("All requests processed.")
