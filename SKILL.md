---
name: ppt-memory
description: 制作、修改或评审 PPT、幻灯片、演示文稿时，先读取跨项目长期偏好与当前项目记忆；捕捉用户反馈并按作用域写回。适用于持续改版和跨项目复用偏好，不代替 PPT 制作工具。
---

# PPT 长期记忆

使用 Python 3.9+，仅标准库，无需 DSH 专用 Python、Node 或 Office。脚本位置相对于本 SKILL.md：`scripts/ppt_memory.py`。下文 `<脚本>` 必须替换成这个脚本的绝对路径，并给路径加引号；`python` 代表实际检测到的 Python 3.9+ 命令（Windows 也可用 `py -3`，macOS/Linux 常用 `python3`）。不要把当前工作目录当成 skill 安装目录。

## 开始 PPT 任务

在读取 PPT 源文件、编排内容或调用制作工具之前运行：

```text
python "<脚本>" show --root "<当前项目绝对路径>"
```

`show` 同时读取两层，没有文件时只提示，不自动写入：

- **长期**：默认 `~/.dsh/ppt-memory/preferences.md`，与项目目录、skill 目录无关。仅存跨项目偏好，不存版本状态。
- **项目**：`<项目>/.ppt-memory/preferences.md` 与 `state.md`，存当前源文件边界、专用设计、输出规则和进度。兼容原有 Markdown 记忆。

优先级：**本轮明确指令 > 项目偏好 > 长期偏好 > 制作工具规范 > 模型默认**。冲突时说明覆盖哪条；本轮临时例外不修改长期偏好。`open` 只是待确认问题，不能当作已确认要求。长期层缺失时先 `init`；项目层仅在需要记录项目事实时 `init --scope project`。

使用宿主已提供且可用的 PPT 制作与渲染工具；本 skill 不绑定某个制作库、字体、配色或绝对路径，不授权额外生成/导出文件。

## 反馈立即写回

```text
python "<脚本>" add --scope global --section aesthetics --text "用户明确的跨项目审美偏好" --source user --evidence "用户原话"
python "<脚本>" add --scope project --root "<项目>" --section content --text "仅此项目的源文件边界" --source user
```

- `add` 默认写 **global**；项目限定信息必须显式指定 `--scope project`。不得将某一份汇报的字体、配色、主题、页数或文件名自动推广为全局规则。
- 明确可复用的用户要求、反复出现且可复用的反馈写长期层。一次性修改只执行，不记为偏好；范围不明则留在项目待确认区，不猜成全局规则。
- `--source`：`user`、`feedback`、`inferred`。推断只能写 `--section open`，脚本会拒绝其他分区。用户确认后记录为 `user`，并标记原待确认项已解决。
- 分区：`content`、`aesthetics`、`deliverable`、`workflow`、`open`、`changelog`。
- 同分区完全相同文本去重。语义去重与冲突需模型判断：保留历史，在旧条目标注“已被覆盖”，新增规则及 changelog；不要同时执行互斥条目。
- 旧项目迁移时，先将正式分区中的 inferred 移到项目 open；仅提升有依据且可复用的条目。不得整份复制到长期层。

## 结束前

```text
python "<脚本>" check --root "<项目>"
```

检查两层的文件、分区与推断来源；**不是 PPT 合规或视觉检查**。另用制作工具核对适用偏好、内容和逐页渲染；如无法渲染须说明，不能声称通过。需要项目状态时，先初始化项目层，再更新其 `state.md` 的版本、页数、设计参数和下一步；禁止把项目状态写入长期层。

## 安装与跨设备使用

首次安装、分享、升级或配置记忆位置时读 [references/portability.md](references/portability.md)。安装程序可将 skill 复制到用户级目录，并在宿主全局 AGENTS.md 增加 PPT 触发协议。**自动触发依赖宿主读取全局规则或发现 skill，不是后台监听器**；新会话验证后才报告已实际触发。换项目无需复制或重新初始化长期偏好；换电脑需单独迁移私人长期记忆，skill 分发包不含这些数据。
