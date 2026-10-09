# IDA Pro + ida-pro-mcp 避坑大全

按阶段整理的全部已踩坑（2026-10 两轮实战沉淀）。新机器照"部署段"装完后，"使用段"当手册查。路径以 `SKILL.md` 环境表为准。

## 一、部署段（新机器从零装）

1. **idapyswitch 必须绑定 Python**：绿色版 IDA 自带 python311 时，确认注册表 `HKCU\Software\Hex-Rays\IDA\Python3TargetDLL` 指向其 `python311.dll`，否则 IDAPython 全挂。
2. **ida-pro-mcp 用 pip 装 2.0.0+**：压缩包自带的旧版（1.3.0）`Scripts\ida-pro-mcp.exe` 常因打包者路径失效；2.0.0 起 pip 重生成的 exe 已修好，且支持插件自启。
3. **首启 License 对话框必须 GUI 手动过**：批处理 `-A` 模式遇到 "License not yet accepted" 会直接静默退出；过一次（连同快捷键对话框）后 `-A` 才可用。
4. **插件位置**：`%APPDATA%\Hex-Rays\IDA Pro\plugins\ida_mcp.py` + `ida_mcp\`，随 IDA 自启监听 `127.0.0.1:13337`；不要往 IDA 安装目录的 plugins 里塞。
5. **ZCode 接入**（用户级 MCP，stdio）：
   ```json
   {"command": "<IDA目录>/python311/python.exe",
    "args": ["<IDA目录>/python311/Lib/site-packages/ida_pro_mcp/server.py"]}
   ```
6. **装完自检**：跑 `scripts/test_stdio.py`——initialize OK + tools/list 恰好 66 个工具（2.0.0 基准）；IDA 未开时 tools/list 报 ConnectionRefused 属正常（桥本身健康）。

## 二、使用段（MCP 日常）

7. **`list_funcs` 参数是 `queries`**，不是 offset/count——传错报 Invalid params，别误判成故障。
8. **HTTP 探活必须 POST**：GET `http://127.0.0.1:13337/mcp` 返回 405 是正常。Accept 头要带 `application/json, text/event-stream`。
9. **等就绪再批量干活**：先 `server_health`，`auto_analysis_ready:true` + `hexrays_ready:true` 才开始；大文件期间 ready 为 false 是在分析不是卡死（10MB Delphi 约 8 分钟，CPU ~260s）。UI"定格"≠死机。
10. **MCP 要有数据的前提**：IDA 开着且有数据库加载。工具报 "Did you run Edit -> Plugins -> MCP" = 没开/没加载。
11. **多实例端口漂移**：第二个 IDA 实例自动换端口（13338...），发现文件在 `%APPDATA%\Hex-Rays\IDA Pro\mcp\instances\instance_<port>.json`；MCP 客户端端点跟着换。端口被占会在 Output 窗口报 "Port 13337 is already in use"。
12. **py_eval 的 exec 闭包坑**：回调/嵌套函数引用外层变量必 NameError，用默认参数绑定：`def cb(ea,name,ord_,c=c,m=m):`。
13. **响应可能超 8KB**：decompile 大函数的 JSON 会被截断，客户端要落盘/分页，别 head 硬切。
14. **认证/凭据**：镜像/第三方代理不附带任何凭据（公网代理池有中间人能力），git 走 ghproxy 镜像时 credential 只对 github.com 白名单生效。

## 三、逆向实战段（目标分析套路）

15. **Delphi 目标**：方法名大多不进符号表；组件/字符串 xrefs 常为空（窗体流间接引用）。路径：python 按文件偏移找串 → `idaapi.get_fileregion_ea(off)` 转 VA → 再查引用。
16. **破解补丁识别**：扫 `B8 xx 00 00 00 C2/C3`（`mov eax,imm; ret`）单值桩。区分：正常 Delphi getter 用 plain `ret`（C3），被砍的 stdcall 导出桩带参数清理 `ret N`（C2 xx 00）。授权类 DLL 先看导出表——名字含 Check/Active/Validate/License/Days 的直接反编译。
17. **签名审计定位篡改**：`Get-AuthenticodeSignature` 全目录扫；HashMismatch（签名在但坏）= 官方文件被改字节；NotSigned + overlay 全零 = 被改后剥签名；overlay 出现 PKCS#7 DER（`30 82 .. 06 09 2a 86 48 86 f7 0d 01 07 02`）= 签名残留。
18. **Windows 侧坑**：7z 解包忠实还原属性——文件可能带 Hidden，PowerShell `Get-ChildItem` 不带 `-Force` 会"看不见"（bash/python 不受影响），签名审计务必加 `-Force`。
19. **安装器解包**：overlay 见 `EF BB BF ;!@Install@!` = Inno Setup 6.2+，innoextract 1.9 不认；7-Zip 26.04 全功能版直接开（便携工具箱见环境表）。
20. **官方对照**：无原版就没法字节 diff；官方安装器若是自有 BootStrap 封装（7z 开不了），在虚拟机里装一份提取原文件再比。
21. **反调试目标**：先静态查指纹（IsDebuggerPresent/NtQueryInformationProcess/rdtsc/DR 寄存器），确有再挂 ScyllaHide（动态加载流程见 SKILL.md），不要上来就装。

## 四、工具脚本

- `scripts/test_stdio.py` —— stdio 桥完整性测试（部署自检用）
- `scripts/mcp_call.py` —— HTTP MCP 极简客户端；多实例时 `MCP_URL=http://127.0.0.1:13338/mcp python mcp_call.py <tool> '<json>'`
