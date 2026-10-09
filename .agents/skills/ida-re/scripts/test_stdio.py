#!/usr/bin/env python3
"""ida-pro-mcp stdio 桥完整性测试（2026-10-09 重建）。

模拟 ZCode 的 stdio MCP 客户端：spawn server.py → initialize 握手 → tools/list。
IDA 未运行时握手仍应成功（桥本身能起）；tools/list 需要 IDA 在 13337 提供服务。
"""
import json
import os
import subprocess
import sys
import threading
import time

IDA_DIR = r"D:\tools\ida\IDA Professional 9.1"
PYTHON = os.path.join(IDA_DIR, "python311", "python.exe")
SERVER = os.path.join(IDA_DIR, "python311", "Lib", "site-packages", "ida_pro_mcp", "server.py")


def read_msgs(proc, out, stop):
    for line in proc.stdout:
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            out.append({"_raw": line})
        if stop[0]:
            break


def main():
    proc = subprocess.Popen(
        [PYTHON, SERVER],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        text=True, encoding="utf-8",
    )
    out, stop = [], [False]
    t = threading.Thread(target=read_msgs, args=(proc, out, stop), daemon=True)
    t.start()

    def send(obj):
        proc.stdin.write(json.dumps(obj) + "\n")
        proc.stdin.flush()

    def wait_for(id_, timeout=15):
        deadline = time.time() + timeout
        seen = 0
        while time.time() < deadline:
            for m in out[seen:]:
                seen += 1
                if m.get("id") == id_:
                    return m
            time.sleep(0.1)
        return None

    send({"jsonrpc": "2.0", "id": 1, "method": "initialize",
          "params": {"protocolVersion": "2025-03-26", "capabilities": {},
                     "clientInfo": {"name": "test_stdio", "version": "1"}}})
    init = wait_for(1)
    if not init:
        print("[FAIL] initialize 无响应")
        print("stderr:", proc.stderr.read() if proc.poll() is not None else "(进程仍活着)")
        proc.kill()
        return 1
    info = init.get("result", {}).get("serverInfo", {})
    print(f"[OK] initialize: {info.get('name')} v{info.get('version')}")

    send({"jsonrpc": "2.0", "method": "notifications/initialized"})
    send({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
    tools = wait_for(2)
    if not tools:
        print("[WARN] tools/list 无响应（IDA 未运行时属预期，桥本身健康）")
        proc.kill()
        return 0
    if "error" in tools:
        print(f"[WARN] tools/list 报错: {tools['error'].get('message')}（IDA 未运行时属预期）")
        proc.kill()
        return 0
    names = [t["name"] for t in tools.get("result", {}).get("tools", [])]
    print(f"[OK] tools/list: {len(names)} 个工具")
    print("     样例:", ", ".join(names[:8]), "...")
    stop[0] = True
    proc.kill()
    return 0


if __name__ == "__main__":
    sys.exit(main())
