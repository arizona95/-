#!/usr/bin/env python3
# aar-r6mdev harmless test stdio MCP server (temporary; removed after the experiment).
# tools: echo(text) -> same text ; fetch_url(url) -> HTTP status and first 120 chars.
import json, sys, urllib.request

TOOLS = [
    {"name": "echo", "description": "Echo back the given text (aar-r6mdev local MCP test).",
     "inputSchema": {"type": "object", "properties": {"text": {"type": "string"}}, "required": ["text"]}},
    {"name": "fetch_url", "description": "GET a URL and return the HTTP status and the first 120 characters (aar-r6mdev test).",
     "inputSchema": {"type": "object", "properties": {"url": {"type": "string"}}, "required": ["url"]}},
]

def call(name, args):
    if name == "echo":
        return "MDEV-LMCP echo: " + str(args.get("text", ""))
    if name == "fetch_url":
        try:
            with urllib.request.urlopen(args.get("url", ""), timeout=15) as r:
                return "status %s: %s" % (r.status, r.read(120).decode("utf-8", "replace"))
        except Exception as e:
            return "error: %s" % e
    raise ValueError("unknown tool")

for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    msg = json.loads(line)
    mid, method = msg.get("id"), msg.get("method")
    if mid is None:
        continue
    if method == "initialize":
        res = {"protocolVersion": msg.get("params", {}).get("protocolVersion", "2024-11-05"),
               "capabilities": {"tools": {}}, "serverInfo": {"name": "aar-r6mdev-cloudlocal", "version": "1.0"}}
    elif method == "tools/list":
        res = {"tools": TOOLS}
    elif method == "tools/call":
        p = msg.get("params", {})
        try:
            res = {"content": [{"type": "text", "text": call(p.get("name"), p.get("arguments") or {})}]}
        except Exception as e:
            res = {"content": [{"type": "text", "text": "error: %s" % e}], "isError": True}
    else:
        sys.stdout.write(json.dumps({"jsonrpc": "2.0", "id": mid, "error": {"code": -32601, "message": "not found"}}) + "\n"); sys.stdout.flush(); continue
    sys.stdout.write(json.dumps({"jsonrpc": "2.0", "id": mid, "result": res}) + "\n"); sys.stdout.flush()
