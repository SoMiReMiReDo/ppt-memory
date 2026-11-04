# 安装、跨平台与数据迁移

## 安装到 DSH 用户目录

找到 Python 3.9+（可先运行 `python --version` / `python3 --version` / `py -3 --version`），然后执行：

```text
python "<解压目录>/ppt-memory/scripts/ppt_memory.py" install
```

默认复制到 `~/.dsh/skills/ppt-memory`，并在 `~/.dsh/AGENTS.md` 添加有起止标记的规则块，保留其他内容。`--agent-home "<宿主配置目录>"` 可以指定已确认的宿主用户级配置目录；不要猜测或修改未选择的宿主。目标已有 skill 时拒绝覆盖；从已安装副本运行 install 可重新刷新规则块。

然后运行已安装副本：

```text
python "<用户目录>/.dsh/skills/ppt-memory/scripts/ppt_memory.py" init
python "<用户目录>/.dsh/skills/ppt-memory/scripts/ppt_memory.py" show --root "<项目目录>"
```

Windows 可将 `python` 换成 `py -3`；所有含空格的路径用双引号。不需要 shell 启动器、环境激活脚本或额外依赖。脚本内部使用 Path.home() / pathlib 解析系统路径，UTF-8 写入。若旧终端无法显示中文，先切换终端为 UTF-8；不是更换记忆编码。

安装后新建一个宿主会话，在另一项目请求制作 PPT：应先读本 SKILL.md，再执行 show，输出同一个长期目录。若宿主没有读取此全局 AGENTS.md，需按该宿主文档把 skill 注册到可发现目录，或手动引用 SKILL.md；不能据安装成功宣称宿主已触发。不修改其他 PPT skill。

## 存储配置

长期目录优先级：`--global-root "<绝对目录>"` > 环境变量 `PPT_MEMORY_HOME` > `~/.dsh/ppt-memory`。自定义配置应在所有项目使用同一绝对路径；`--root` 只影响项目层。自定义目录配置不存入分发包，也不会随 install 自动迁移。

`init` 默认仅建长期 preferences，`init --scope project --root "<项目>"` 建项目三文件，已有文件保留。`show` / `check` 默认读取两层；可用 `--scope global` 或 `--scope project` 指定单层。全新项目没有项目记忆可正常继承长期偏好。

同一账户在本机跨项目共享，不自动跨电脑同步。换电脑时自行将长期目录复制到新机相同默认位置或配置的目录；不将私人记忆上传到公开 skill 仓库。不同用户安装同一包，各自从空白长期记忆开始。

## 分发与更新

只打包整个 ppt-memory skill 目录；排除 `__pycache__`、`*.pyc`、`.DS_Store`。不包含 `.ppt-memory`、用户级长期记忆、用户全局 AGENTS.md、DSH 运行时、项目材料、其他第三方 skill 或 node_modules。原有模板都为空白。明确发布权属与许可证后再公开分发。

更新：替换已安装 skill 的程序、模板和说明，不动长期目录和任何项目记忆；从更新后的安装目录执行 install 刷新有标记的触发规则。不要复制别人已安装的全局 AGENTS.md。

写入采用临时文件原子替换和目录锁，避免正常并发写入丢条目。若进程异常退出留下 `.write.lock`，先确认没有写入进程，再手动删除锁。不要把长期存储放在 skill 目录内，以免更新时丢失。
