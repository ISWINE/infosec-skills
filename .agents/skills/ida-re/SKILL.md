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

## 实战经验（2026-10-09 IObit 破解版一案）

- **多目标并行**：第二个 IDA 实例自动换端口，发现文件在 `%APPDATA%\Hex-Rays\IDA Pro\mcp\instances\instance_<port>.json`；MCP 调用端点跟着换。10MB Delphi 程序自动分析约 8 分钟（CPU ~260s）。
- **py_eval 的 exec 闭包坑**：回调函数里引用外层变量会 NameError，必须用默认参数绑定（`def cb(ea,name,ord_,c=c,m=m):`）。
- **Delphi 目标套路**：方法名大多不进符号表，字符串 xrefs 常为空（窗体流间接引用）；先用 python 在文件偏移找串，再 `idaapi.get_fileregion_ea(off)` 转 VA。破解补丁识别：扫 `B8 xx 00 00 00 C2/C3` 单值桩（`mov eax,imm; ret`），注意区分正常 Delphi getter（plain `ret`）与 stdcall 导出桩（`ret N`）。
- **授权类 DLL 定位**：先看导出表——名字含 Check/Active/Validate/License/Days 的导出直接反编译；HashMismatch（签名坏）文件优先级最高，overlay 里的 PKCS#7 残留 = 原来是签名的官方文件被改。
- **解包工具链**：`D:\tools\7zip\`（x86/x64 完整版 + 7za，26.04 能开 Inno 6.2+ 新格式）、`D:\tools\innoextract\`（只到 Inno 6.0.5）。安装器先看 overlay：BOM+`;!@Install@!` = Inno 6.2+ 直接用 7z 全功能版解。
- 顺手写的 HTTP MCP 客户端可复用（urllib POST /mcp，解析 content[0].text 二次 JSON），比 bash 拼 curl 稳。
