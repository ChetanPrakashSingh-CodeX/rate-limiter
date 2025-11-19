import time
import asyncio

MAX_TOKENS = 5
REFILL_RATE = 5  # Seconds between token refills

class TokenBucket:
    def __init__(self, max_tokens, refill_rate):
        self.tokens = max_tokens
        self.max_tokens = max_tokens
        self.refill_rate = refill_rate
        self.last_refill = time.time()

    def has_tokens(self):
        # Update tokens based on time passed since last check (leaky bucket algorithm)
        now = time.time()
        time_passed = now - self.last_refill
        if time_passed >= self.refill_rate:
            tokens_to_add = int(time_passed // self.refill_rate)
            self.tokens = min(self.max_tokens, self.tokens + tokens_to_add)
            self.last_refill = now
        
        return self.tokens > 0

    def consume_token(self):
        if self.has_tokens():
            self.tokens -= 1
            return True
        return False

# Initialize the bucket
bucket = TokenBucket(MAX_TOKENS, REFILL_RATE)

async def handle_incoming_request(request_id):
    if not bucket.consume_token():
        print(f'Out of tokens! Please try again later {request_id}')
        return

    print(f'✅ Processing Request... {request_id}')
    await asyncio.sleep(2)  # Simulate a fake wait time with asyncio
    return True

# Example of how to use it (e.g., in a simple asynchronous event loop)
async def main():
    # Simulate multiple requests coming in quickly
    requests = [f'req-{i}' for i in range(10)]
    
    # Process requests asynchronously
    await asyncio.gather(*[handle_incoming_request(req_id) for req_id in requests])

if __name__ == "__main__":
    asyncio.run(main())