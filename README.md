# infosec-skills

信息安全方向的个人 ZCode 技能仓库（agent skills）。目录结构遵循 ZCode 技能发现规范：`.agents/skills/<name>/SKILL.md`——整个仓库克隆到任何项目目录下，里面的技能即可被 ZCode 项目级发现自动加载；本机则通过 junction 联接提供用户级发现。

姊妹仓库：[zcode-skills](https://github.com/ISWINE/zcode-skills)（通用技能），本仓库专注信息安全方向（逆向、取证、样本分析、攻防实验），两仓遵循同一套规则。

> **安全工具分支（`安全工具`）**：专门同步经一致性验证的安全工具源码，main 分支保持纯技能。当前收录：
>
> | 工具 | 位置 | 来源与指纹 |
> |---|---|---|
> | ARTEX v0.3.15 | `tools/ARTEX/` | `mhtsec/ARTEX`（2026-10-09 同步，HEAD `5c0dbd4bec94`，tree `9e4e5ee3f6bc`，458 提交全量保留；上游 Autumn-27/ARTEX 已删库，mhtsec 与 wangjingtiankl/ARTEX 字节级一致） |
>
> 注意：ARTEX ≤v0.3.14 存在预认证 RCE（TOCTOU，见 therustymate/ARTXploit），部署用 v0.3.15 血统并控制暴露面。

## 当前技能

| 技能 | 用途 | 触发方式 |
|---|---|---|
| `ida-re` | IDA Pro 9.1 + ida-pro-mcp 逆向分析工作台：副本加载（`-A` 无弹窗）→ 轮询 13337 → `server_health` 等自动分析就绪 → imports/list_funcs 摸底 → decompile 读伪码 → set_comment/重命名落库 → `idb_save`；带反调试检测的目标先静态查指纹再动态挂 ScyllaHide（已下载未安装，用时拷三件套进 plugins 重启 IDA）；含 stdio 桥完整性自检脚本 | 说"逆向/反编译/看这个 exe、dll、so/二进制分析/查壳/脱壳/找算法/IDA 分析"自动触发 |

## 本机部署方式（junction 联接）

真身在 `D:\projects\infosec-skills\.agents\skills\<name>`，用户级发现路径 `~/.agents/skills/<name>` 是指向它的 JUNCTION：

```cmd
mklink /J C:\Users\12696\.agents\skills\<name> D:\projects\infosec-skills\.agents\skills\<name>
```

改技能直接改本仓库文件即可（联接透明），改完记得 commit + push。

## 扩充新技能

1. 在 `.agents/skills/` 下新建 `<name>/SKILL.md`（frontmatter 必须含 `name` 和 `description`，name 与目录同名，kebab-case）
2. 可选挂 `scripts/`（可执行脚本）、`references/`（模型按需读的细节文档）、`assets/`（模板）
3. 需要用户级可用就在本机做联接（见上）；仅项目用则随仓库克隆自动生效
4. `SKILL.md` 控制在 500 行内，细节往 `references/` 拆

## 同步

```bash
cd /d/projects/infosec-skills
git add -A && git commit -m "..." && git push
```

## 注意

- `ida-re` 的 SKILL.md 含本机路径与工具布局（`D:\tools\ida` 等），仓库保持 **private**
- 技能入库前须过安全审查（参照 ida-re 的做法：来源可溯、与官方 diff、无网络指标）
