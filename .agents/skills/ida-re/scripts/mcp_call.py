#!/usr/bin/env python3
"""ida-pro-mcp HTTP 极简客户端（零依赖，标准库直连）。

用法:
    python mcp_call.py <tool> '<json参数>'
    MCP_URL=http://127.0.0.1:13338/mcp python mcp_call.py server_health '{}'

响应超 8KB 的工具（decompile 大函数）会完整打印，不截断。
"""
import sys, os, json, urllib.request

URL = os.environ.get("MCP_URL", "http://127.0.0.1:13337/mcp")

def call(name, args, timeout=300):
    payload = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "tools/call",
                          "params": {"name": name, "arguments": args}}).encode()
    req = urllib.request.Request(URL, data=payload, headers={
        "Content-Type": "application/json", "Accept": "application/json, text/event-stream"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        body = r.read().decode()
    try:
        d = json.loads(body)
    except json.JSONDecodeError:
        for line in body.splitlines():
            if line.startswith("data:"):
                d = json.loads(line[5:])
                break
        else:
            raise
    res = d.get("result", {})
    if res.get("isError"):
        return {"ERROR": res["content"][0]["text"]}
    txt = res["content"][0]["text"]
    try:
        return json.loads(txt)
    except (json.JSONDecodeError, TypeError):
        return txt

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    name = sys.argv[1]
    args = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
    out = call(name, args)
    if isinstance(out, str):
        print(out)
    else:
        print(json.dumps(out, ensure_ascii=False, indent=1))
