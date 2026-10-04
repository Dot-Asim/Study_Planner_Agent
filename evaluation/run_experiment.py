import httpx
import time
import json
from pathlib import Path

models = ['openai/gpt-oss-120b', 'openai/gpt-oss-20b']
cases = [
    {
        "name": "Standard Scheduling",
        "request": {
            "task": "Schedule 2 hours of study for my math assignment on Wednesday",
            "external_context": [],
            "arena_config": {"max_steps": 6, "fault": "none"}
        }
    },
    {
        "name": "Needs Clarification",
        "request": {
            "task": "Schedule some time for my assignment",
            "external_context": [],
            "arena_config": {"max_steps": 6, "fault": "none"}
        }
    },
    {
        "name": "Requires Approval",
        "request": {
            "task": "Delete my math study session",
            "external_context": [],
            "arena_config": {"max_steps": 6, "fault": "none"}
        }
    }
]

def run_experiment():
    results = {}
    for model in models:
        print(f"\nEvaluating Model: {model}")
        model_results = []
        for case in cases:
            req = case["request"].copy()
            req["model"] = model
            # Note: /arena/run does not take model directly, it reads from config unless we use /chat
            # We will test using /chat, which accepts 'model' parameter
            chat_req = req.copy()
            chat_req["session_id"] = f"test-session-{time.time()}"
            
            try:
                start_time = time.perf_counter()
                response = httpx.post('http://127.0.0.1:8000/chat', json=chat_req, timeout=30)
                response.raise_for_status()
                res = response.json()
                latency = (time.perf_counter() - start_time)
                
                model_results.append({
                    "case": case["name"],
                    "status": res["status"],
                    "latency": f"{latency:.2f}s",
                    "input_tokens": res["metrics"].get("input_tokens"),
                    "output_tokens": res["metrics"].get("output_tokens")
                })
                print(f"  [PASS] {case['name']} - Status: {res['status']} ({latency:.2f}s)")
            except Exception as e:
                print(f"  [FAIL] {case['name']} - Error: {e}")
                
        results[model] = model_results
        
    print("\n--- Summary Table ---")
    print("| Model | Case | Status | Latency | In Tokens | Out Tokens |")
    print("|---|---|---|---|---|---|")
    for model, res_list in results.items():
        for res in res_list:
            print(f"| {model} | {res['case']} | {res['status']} | {res['latency']} | {res['input_tokens']} | {res['output_tokens']} |")

if __name__ == '__main__':
    run_experiment()
