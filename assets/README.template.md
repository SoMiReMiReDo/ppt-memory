# 项目 PPT 记忆

本目录只保存当前项目的偏好与状态。跨项目长期偏好默认在用户目录 `.dsh/ppt-memory/preferences.md`，切换项目会继续读取。

- preferences.md：本项目要求、例外与待确认事项。
- state.md：本项目文件、版本、页数、设计参数与下一步。

优先级：本轮用户指令 > 项目偏好 > 长期偏好 > 工具默认规范。
由已安装的 ppt-memory skill 维护；修改本项目用 add --scope project，长期偏好用 add --scope global。推断只能进 open。不要将项目状态提升到长期层。
