---
name: ida-re
description: IDA Pro 逆向分析工作台。用户说 逆向/反编译/看这个 exe、dll、sys、so/二进制分析/查壳/脱壳/找算法/IDA 分析 的时候使用——驱动本机 IDA Pro 9.1 + ida-pro-mcp（66 个 MCP 工具）完成加载、静态分析、反编译阅读、重命名/注释落库的全流程；带反调试检测的目标先查指纹再动态挂 ScyllaHide。ZCode 已接好 MCP，工具名前缀 mcp__ida-pro-mcp__*。
---

# IDA 逆向分析工作台

本机 IDA Pro 9.1（绿色版）+ ida-pro-mcp 2.0.0，ZCode 用户级 MCP 已配置（stdio 桥），**会话里直接调用 `mcp__ida-pro-mcp__*` 工具即可**，无需任何安装步骤。

## 环境

| 组件 | 位置 |
|---|---|
| IDA 主程序 | `D:\tools\ida\IDA Professional 9.1\ida.exe` |
| MCP 服务 | 插件随 IDA 自启，监听 `127.0.0.1:13337`（streamable HTTP） |
| 完整性测试 | `D:\tools\ida\mcp-test\test_stdio.py`（本技能 scripts/ 有同款） |
| 详细说明 | `D:\tools\ida\IDA-MCP-本机使用说明.md` |
| **避坑大全** | **[references/pitfalls.md](references/pitfalls.md)——新机器部署 + 全量 21 条坑（部署/使用/实战三段），换机先读它** |
| MCP 客户端 | `scripts/mcp_call.py`（HTTP 直连；多实例改 `MCP_URL` 环境变量） |

## 标准工作流

**1. 拉起 IDA 加载目标**（分析副本，别污染原目录）：

```bash
mkdir -p /tmp/ida-work && cp <目标文件> /tmp/ida-work/target.bin
cd /tmp/ida-work && ("/d/tools/ida/IDA Professional 9.1/ida.exe" -A target.bin &)
# 轮询端口，最长 90s（大文件自动分析更久）：
for i in $(seq 1 45); do sleep 2; netstat -ano | grep -q "13337.*LISTENING" && break; done
```

`-A` = 自主模式不弹对话框（License 首启对话框本机已过掉，不会再弹）。

**2. 等 MCP 就绪再干活**——先调 `server_health`，看到 `auto_analysis_ready: true` 和 `hexrays_ready: true` 才开始批量分析（没就绪就 sleep 后重查）。

**3. 分析套路**（按需组合）：

- 入口摸底：`imports` / `imports_query` 看导入表 → `list_funcs` / `func_query` 列函数
- 字符串/常量定位：strings 相关工具 + `lookup_funcs` 按名找函数
- 读代码：`decompile` 出 Hex-Rays 伪代码（比汇编快得多，优先用）
- 交叉引用顺藤摸瓜：xref 类工具
- 成果落库：`set_comment` 写注释、重命名工具改掉 sub_XXXX、最后 `idb_save`（**不落库白干**）

**4. 收尾**：分析完告诉用户 `.i64` 数据库在哪；临时目录问一句要不要留。

## 坑（都踩过）

- **`list_funcs` 参数是 `queries`**，不是 offset/count——传错会报 Invalid params，这不是故障。
- MCP 要有数据，**IDA 必须开着且有数据库加载**；工具报 "Did you run Edit -> Plugins -> MCP" = IDA 没开或没加载文件。
- 端口 13337 被占：多个 IDA 实例时第一个占 13337，后续自动换端口（发现文件在 `%APPDATA%\Hex-Rays\IDA Pro\mcp\instances\`）。
- curl 直接打 `http://127.0.0.1:13337/mcp`：GET 返回 405 是正常，必须 POST。
- 大文件自动分析期间 `server_health` 的 `auto_analysis_ready` 为 false，等它翻 true。

## 带反调试检测的目标（壳/保护/恶意样本）

1. **先静态查指纹**再决定要不要上工具：导入表有 `IsDebuggerPresent` / `NtQueryInformationProcess` / `NtSetInformationThread`，或反编译里见 `rdtsc` 时间差、`DR0-7` 读取 → 目标会检测调试器。
2. 需要动态调试时**动态加载 ScyllaHide**（已下载未安装，用户零操作）：

```bash
cp /d/tools/ida/ScyllaHideForIDA9.0/{ScyllaHideIDAProPlugin.dll,ScyllaHideIDAServerx64.exe,scylla_hide.ini} \
   "/d/tools/ida/IDA Professional 9.1/plugins/"
# 重启 IDA 生效；配置档（vmprotect/themida 等）直接改 scylla_hide.ini
# 卸载 = 删掉这三个文件，完全可逆
```

用户正开着 IDA 干活的话，重启前先说一声。

## 完整性自检（怀疑 MCP 坏了时）

```bash
"/d/tools/ida/IDA Professional 9.1/python311/python.exe" <本技能>/scripts/test_stdio.py
```

预期：initialize OK + tools/list 报 66 个工具（IDA 未开时 tools/list 报 ConnectionRefused 属正常——桥本身健康）。全链路金标准 = 拉起 IDA 后 `server_health` 返回 `status: ok`。

## 深挖细节

多实例端口发现、py_eval 闭包坑、Delphi 目标套路、破解补丁桩识别、签名审计定位篡改、安装器解包工具链——全部在 [references/pitfalls.md](references/pitfalls.md)（部署/使用/实战三段 21 条，2026-10 实战沉淀）。
