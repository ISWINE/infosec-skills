# infosec-skills

信息安全技能集——逆向分析、流量取证、样本分析等方向的 ZCode（AI 编码代理）技能仓库。每个技能是一个可直接投产的 `SKILL.md` 工作流，沉淀"在本机踩平的坑"。

## 技能清单

| 技能 | 说明 |
|---|---|
| [ida-re](skills/ida-re/) | IDA Pro 9.1 + ida-pro-mcp 逆向分析工作台：加载目标 → MCP 静态分析 → 反编译 → 注释落库，含 ScyllaHide 反反调试动态加载与完整性自检 |

## 本地安装

把技能目录整棵拷到 ZCode 的用户级技能目录即可被发现：

```bash
# Windows
xcopy /E /I skills\ida-re "%USERPROFILE%\.agents\skills\ida-re"

# 或类 Unix
cp -r skills/ida-re ~/.agents/skills/ida-re
```

## 注意

- 技能内的绝对路径（如 `D:\tools\ida\...`）是作者本机布局，换机器需要按 `SKILL.md` 里的环境表改成自己的路径。
- [ida-re](skills/ida-re/) 依赖：IDA Pro 9.x + [ida-pro-mcp](https://github.com/mrexodia/ida-pro-mcp) 2.0.0，且 ZCode 已配置对应 MCP 服务器（工具前缀 `mcp__ida-pro-mcp__*`）。
