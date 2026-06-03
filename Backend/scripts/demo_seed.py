#!/usr/bin/env python3
"""
VoxPilot Demo Seed Script
Sends several synthesis requests to populate the database with sample data.
"""
import requests
import sys

API_URL = "http://localhost:8000"

SEED_REQUESTS = [
    {
        "text": "Welcome to VoxPilot, a TTS studio for speech generation workflows.",
        "voice": "default",
        "language": "en",
    },
    {
        "text": "This is a demonstration of text to speech synthesis.",
        "voice": "low",
        "language": "en",
    },
    {
        "text": "VoxPilot tracks latency, cache hits, and synthesis quality.",
        "voice": "mid",
        "language": "en",
    },
    {
        "text": "Evaluation feedback helps product teams compare generation quality.",
        "voice": "default",
        "language": "en",
    },
    {
        "text": "Thank you for exploring VoxPilot. Built with safety in mind.",
        "voice": "high",
        "language": "en",
    },
]


def main():
    print("🌱 VoxPilot Demo Seed")
    print("=" * 60)

    # Check API is running
    try:
        health = requests.get(f"{API_URL}/health", timeout=5)
        health.raise_for_status()
        print(f"✅ API is healthy: {health.json().get('status')}")
    except requests.ConnectionError:
        print("❌ Cannot connect to API. Is it running on port 8000?")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        sys.exit(1)

    print()
    results = []

    for i, req in enumerate(SEED_REQUESTS, 1):
        print(f"[{i}/{len(SEED_REQUESTS)}] Synthesizing: \"{req['text'][:50]}...\"")
        try:
            response = requests.post(f"{API_URL}/synthesize", data=req, timeout=30)
            data = response.json()

            if data.get("success"):
                results.append(data)
                print(f"  ✅ run_id={data['run_id']}")
                print(f"     latency={data['latency_ms']:.1f}ms | "
                      f"cache_hit={data['cache_hit']} | "
                      f"engine={data['engine']}")
            else:
                print(f"  ❌ Failed: {data.get('error', 'Unknown error')}")
        except Exception as e:
            print(f"  ❌ Error: {e}")

        print()

    # Summary
    print("=" * 60)
    print(f"📊 Seed Summary: {len(results)}/{len(SEED_REQUESTS)} successful")
    if results:
        avg_latency = sum(r["latency_ms"] for r in results) / len(results)
        print(f"   Average latency: {avg_latency:.1f}ms")
    print("🌱 Seed complete!")


if __name__ == "__main__":
    main()
