# Reproducible test: LiteLLM Router routing capabilities (open-source, MIT).
# Verifies load balancing, fallback-on-failure, and retry-then-fallback.
# Uses litellm's mock_response so no real API keys are required.
#
# Run:  pip install litellm && python benchmark/vendors/test_litellm_router.py
import json
import litellm

litellm.suppress_debug_info = True
litellm.set_verbose = False
results = {}


def check(name, cond, detail):
    results[name] = {"pass": bool(cond), "detail": detail}


# 1) Load balancing (simple-shuffle) — requests should spread across deployments.
router = litellm.Router(
    model_list=[
        {"model_name": "lb", "litellm_params": {"model": "gpt-4o", "mock_response": "A"}},
        {"model_name": "lb", "litellm_params": {"model": "gpt-4o", "mock_response": "B"}},
        {"model_name": "lb", "litellm_params": {"model": "gpt-4o", "mock_response": "C"}},
    ],
    routing_strategy="simple-shuffle",
    num_retries=0,
)
dist = {}
for _ in range(30):
    r = router.completion(model="lb", messages=[{"role": "user", "content": "hi"}])
    c = r.choices[0].message.content
    dist[c] = dist.get(c, 0) + 1
check("load_balancing", len(dist) > 1, dist)


# 2) Fallback on failure — a dead primary deployment should fall back to a working backup.
router_fb = litellm.Router(
    model_list=[
        {"model_name": "primary", "litellm_params": {"model": "openai/gpt-4o",
                                                    "api_base": "http://127.0.0.1:1/invalid", "api_key": "sk-dead"}},
        {"model_name": "backup", "litellm_params": {"model": "gpt-4o", "mock_response": "backup-ok"}},
    ],
    fallbacks=[{"primary": ["backup"]}],
    num_retries=0,
)
r = router_fb.completion(model="primary", messages=[{"role": "user", "content": "hi"}])
check("fallback_on_failure", r.choices[0].message.content == "backup-ok", r.choices[0].message.content)


# 3) Retry-then-fallback — with num_retries=2, primary is retried then falls back to backup.
router_rt = litellm.Router(
    model_list=[
        {"model_name": "p", "litellm_params": {"model": "openai/gpt-4o",
                                               "api_base": "http://127.0.0.1:1/invalid", "api_key": "sk-dead"}},
        {"model_name": "b", "litellm_params": {"model": "gpt-4o", "mock_response": "backup-ok"}},
    ],
    fallbacks=[{"p": ["b"]}],
    num_retries=2,
)
r = router_rt.completion(model="p", messages=[{"role": "user", "content": "hi"}])
check("retry_then_fallback", r.choices[0].message.content == "backup-ok", r.choices[0].message.content)


print(json.dumps(results, indent=2))
all_pass = all(v["pass"] for v in results.values())
print("\nRESULT:", "PASS" if all_pass else "FAIL")
