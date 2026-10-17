
import statistics
import time
import urllib.error
import urllib.request
import json

BASE_URL = "http://127.0.0.1:8000"
REQUESTS = 50

payload = {
    "tx_id": "tx-test-001",
    "customer_id": "customer-001",
    "counterparty_id": "customer-002",
    "amount": 125.50,
    "type": "TRANSFER",
    "step": 1
}

latencies_ms = []

for i in range(REQUESTS):
    request = urllib.request.Request(
        f"{BASE_URL}/score",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    start = time.perf_counter()

    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            response.read()
            elapsed = (time.perf_counter() - start) * 1000
            latencies_ms.append(elapsed)
    except (urllib.error.URLError, TimeoutError) as exc:
        print(f"Request {i + 1} failed: {exc}")

if latencies_ms:
    ordered = sorted(latencies_ms)
    p95_index = min(len(ordered) - 1, int(0.95 * len(ordered)))

    print(f"Successful requests: {len(latencies_ms)}/{REQUESTS}")
    print(f"Average latency: {statistics.mean(latencies_ms):.2f} ms")
    print(f"Median latency: {statistics.median(latencies_ms):.2f} ms")
    print(f"P95 latency: {ordered[p95_index]:.2f} ms")
else:
    print("No successful requests. Check that the API is running.")

