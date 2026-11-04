# ppt-memory

为 DSH 中的 PPT 制作保存跨项目长期偏好，并将当前项目的内容与版本状态单独管理。

- 长期偏好：默认保存在 `~/.dsh/ppt-memory/preferences.md`，切换项目继续读取。
- 项目记忆：保存在 `<项目>/.ppt-memory/`，用于源文件、专用设计与当前版本状态。
- 优先级：本轮用户指令 > 项目偏好 > 长期偏好 > 制作工具默认规范。
- 未确认推断只能写入待确认区；仅依赖 Python 3.9+ 标准库。

## 安装到 DSH

下载本仓库 ZIP 并解压，或执行：

```sh
git clone https://github.com/SoMiReMiReDo/ppt-memory.git
cd ppt-memory
python scripts/ppt_memory.py install
```

macOS/Linux 可将 `python` 换成 `python3`；Windows 可用 `py -3`。

安装会将 Skill 复制到 `~/.dsh/skills/ppt-memory`，并向 `~/.dsh/AGENTS.md` 添加有标记的 PPT 触发规则，保留原有规则。目标目录已经存在时不会覆盖；更新方式见 [移植说明](references/portability.md)。

安装后，用已安装副本初始化长期记忆（命令中的 `<用户目录>` 需替换为本机绝对路径）：

```text
python "<用户目录>/.dsh/skills/ppt-memory/scripts/ppt_memory.py" init
```

在新的 DSH 会话请求制作或修改 PPT，宿主应先读取本 Skill，再读取两层记忆。自动触发依赖宿主读取全局 AGENTS.md 或发现此 Skill；不是后台监听器。

## 记录与读取

下面使用仓库副本演示；长期存储与脚本所在目录无关：

```sh
python scripts/ppt_memory.py add --section aesthetics --text "减少框型结构" --source user
python scripts/ppt_memory.py show --root "<项目绝对路径>"
python scripts/ppt_memory.py add --scope project --root "<项目绝对路径>" --section content --text "本项目只读指定源文件" --source user
python scripts/ppt_memory.py check --root "<项目绝对路径>"
```

`add` 默认写长期层；项目限制必须指定 `--scope project`。可用环境变量 `PPT_MEMORY_HOME` 或 `--global-root` 指定长期存储绝对路径。项目状态不进入长期层。

`check` 只检查记忆结构与推断来源，不能证明 PPT 内容或版面正确。此 Skill 不包含 PPT 制作引擎，也不会额外授权生成或导出文件。

## 验证

```sh
python scripts/test_ppt_memory.py
```

包含 9 项隔离测试：跨项目继承、项目隔离、推断限制、旧数据检查、去重、状态保留、路径配置、安装规则和并发写入。已在 macOS 运行通过；Windows/Linux 尚未进行真机验证。

## 数据边界

本仓库只包含程序、说明和空模板，不包含个人偏好或实际项目材料。本机跨项目共享不等于跨电脑同步；迁移设备时单独迁移私人长期记忆目录。

详细协议见 [SKILL.md](SKILL.md)，安装与迁移见 [references/portability.md](references/portability.md)。
