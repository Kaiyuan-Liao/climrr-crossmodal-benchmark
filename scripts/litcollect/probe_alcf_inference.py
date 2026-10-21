#!/usr/bin/env python3
"""Probe the ALCF inference endpoints: reachability, token, model lists, one tiny completion.

Run on a Polaris login node (or the Mac) after `pip install --user alcf-tokens openai`
and `alcf-tokens login inference` (one-time browser flow). Prints facts only; writes
probe_alcf_inference.json next to this script. Nothing project-specific is sent: the
test prompt is a fixed arithmetic question.
"""
import json, sys, time, urllib.request, urllib.error

HOST = "https://inference-api.alcf.anl.gov"
CLUSTERS = {
    "sophia": "/resource_server/sophia/vllm/v1",
    "metis": "/resource_server/metis/api/v1",
    "minerva": "/resource_server/minerva/api/v1",
}
out = {"host": HOST, "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "clusters": {}}

import os
tok = os.environ.get("TOKEN") or os.environ.get("ALCF_INFERENCE_TOKEN")
if tok:
    out["token"] = "ok from env (%d chars)" % len(tok)
else:
    try:
        from alcf_tokens.auth import get_access_token
        tok = get_access_token("inference")
        out["token"] = "ok from alcf_tokens (%d chars)" % len(tok)
    except Exception as e:  # noqa: BLE001
        out["token"] = f"FAILED: no TOKEN env var and alcf_tokens unavailable: {type(e).__name__}: {e}"
        print(json.dumps(out, indent=2)); sys.exit(1)


def get(url, timeout=30):
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {tok}"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.status, r.read().decode("utf-8", "replace")


def post(url, body, timeout=120):
    req = urllib.request.Request(url, data=json.dumps(body).encode(), method="POST",
                                 headers={"Authorization": f"Bearer {tok}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.status, r.read().decode("utf-8", "replace")


# Global job/status listing, if exposed.
for path in ("/resource_server/jobs", "/resource_server/sophia/jobs", "/resource_server/metis/jobs"):
    try:
        st, body = get(HOST + path)
        out.setdefault("jobs", {})[path] = body[:4000]
    except Exception as e:  # noqa: BLE001
        out.setdefault("jobs", {})[path] = f"ERR {type(e).__name__}: {getattr(e, 'code', '')} {e}"

for name, base in CLUSTERS.items():
    c = out["clusters"][name] = {"base_url": HOST + base}
    try:
        st, body = get(HOST + base + "/models")
        try:
            ids = [m.get("id") for m in json.loads(body).get("data", [])]
        except Exception:  # noqa: BLE001
            ids = body[:2000]
        c["models"] = ids
    except Exception as e:  # noqa: BLE001
        c["models"] = f"ERR {type(e).__name__}: {getattr(e, 'code', '')} {e}"

# One tiny completion on Metis gpt-oss-120b (documented example model), then on the first Sophia model if any.
tests = [("metis", "gpt-oss-120b")]
sm = out["clusters"]["sophia"].get("models")
if isinstance(sm, list) and sm:
    tests.append(("sophia", sm[0]))
for cl, model in tests:
    t0 = time.time()
    try:
        st, body = post(HOST + CLUSTERS[cl] + "/chat/completions",
                        {"model": model, "temperature": 0, "max_tokens": 16,
                         "messages": [{"role": "user", "content": "What is 17*3? Answer with the number only."}]})
        txt = json.loads(body)["choices"][0]["message"]["content"]
        out.setdefault("completions", {})[f"{cl}:{model}"] = {"status": st, "seconds": round(time.time() - t0, 1), "answer": txt.strip()[:80]}
    except urllib.error.HTTPError as e:
        out.setdefault("completions", {})[f"{cl}:{model}"] = {"error": f"HTTP {e.code}", "body": e.read().decode('utf-8', 'replace')[:500], "seconds": round(time.time() - t0, 1)}
    except Exception as e:  # noqa: BLE001
        out.setdefault("completions", {})[f"{cl}:{model}"] = {"error": f"{type(e).__name__}: {e}", "seconds": round(time.time() - t0, 1)}

print(json.dumps(out, indent=2))
json.dump(out, open("probe_alcf_inference.json", "w"), indent=2)
