#!/usr/bin/env python3
"""Portable PPT memory. Python 3.9+, standard library only."""
from __future__ import annotations

import argparse
import datetime as dt
import os
from pathlib import Path
import re
import shutil
import sys
import tempfile
import time
from contextlib import contextmanager

SKILL = Path(__file__).resolve().parent.parent
ASSETS = SKILL / 'assets'
SECTIONS = {'content': '内容偏好', 'aesthetics': '审美偏好',
            'deliverable': '结果偏好', 'workflow': '流程偏好',
            'open': '待确认', 'changelog': '变更记录'}
BEGIN = '<!-- ppt-memory:begin -->'
END = '<!-- ppt-memory:end -->'


def global_home(explicit=None):
    value = explicit or os.environ.get('PPT_MEMORY_HOME')
    if value:
        path = Path(value).expanduser()
        if not path.is_absolute():
            raise ValueError('长期记忆路径必须是绝对路径，避免切换项目后指向不同目录。')
        return path.resolve()
    return Path.home() / '.dsh' / 'ppt-memory'


def bounds(lines, title):
    start = next((i for i, s in enumerate(lines) if s.startswith('## ') and title in s), None)
    if start is None:
        return None, None
    return start, next((i for i in range(start + 1, len(lines)) if lines[i].startswith('## ')), len(lines))


def atomic_write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp = tempfile.mkstemp(prefix='.ppt-memory-', dir=str(path.parent))
    try:
        with os.fdopen(fd, 'w', encoding='utf-8', newline='\n') as f:
            f.write(value)
        os.replace(temp, path)
    finally:
        if os.path.exists(temp):
            os.unlink(temp)


@contextmanager
def locked(directory):
    directory.mkdir(parents=True, exist_ok=True)
    lock = directory / '.write.lock'
    deadline = time.monotonic() + 5
    while True:
        try:
            fd = os.open(str(lock), os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
            os.close(fd)
            break
        except FileExistsError:
            if time.monotonic() >= deadline:
                raise ValueError(f'记忆正在被写入：{lock}；若写入进程已退出，请手动移除遗留锁。')
            time.sleep(.05)
    try:
        yield
    finally:
        lock.unlink()


def initialize(directory, project=False):
    with locked(directory):
        names = ['preferences.md'] + (['state.md', 'README.md'] if project else [])
        for name in names:
            path = directory / name
            if not path.exists():
                atomic_write(path, (ASSETS / name.replace('.md', '.template.md')).read_text(encoding='utf-8'))
    print(f'记忆已就绪（保留已有内容）：{directory}')


def normalize(value):
    return re.sub(r'\s+', ' ', value).strip()


def entry_text(line):
    match = re.match(r'^- \[\d{4}-\d{2}-\d{2}\]\[(user|feedback|inferred)\] (.*)$', line)
    return normalize(match[2].split('（证据：', 1)[0]) if match else None


def add(directory, section, value, source, evidence):
    value = normalize(value)
    if not value:
        raise ValueError('--text 不能为空')
    if source == 'inferred' and section != 'open':
        raise ValueError('inferred 只能写入 open；确认后以 user 来源写入正式分区。')
    initialize(directory)
    path = directory / 'preferences.md'
    with locked(directory):
        lines = path.read_text(encoding='utf-8').splitlines()
        start, end = bounds(lines, SECTIONS[section])
        if start is None:
            lines += ['', f'## {SECTIONS[section]}', '']
            start, end = len(lines) - 2, len(lines)
        if any(entry_text(s) == value for s in lines[start + 1:end]):
            print('相同分区已有完全相同偏好，未重复添加。')
            return
        entry = f'- [{dt.date.today().isoformat()}][{source}] {value}'
        if evidence.strip():
            entry += f'（证据：{normalize(evidence)}）'
        block = [s for s in lines[start + 1:end] if s.strip()]
        lines[start + 1:end] = [''] + block + [entry, '']
        atomic_write(path, '\n'.join(lines).rstrip() + '\n')
    print(f'已写入 {path} [{SECTIONS[section]}]：{value}')


def targets(args):
    if args.scope in ('global', 'both'):
        yield '长期', global_home(args.global_root), False
    if args.scope in ('project', 'both'):
        yield '项目', Path(args.root).expanduser().resolve() / '.ppt-memory', True


def check(directory, project):
    errors = []
    required = ['preferences.md'] + (['state.md'] if project else [])
    for name in required:
        if not (directory / name).is_file():
            errors.append(f'缺少 {name}')
    path = directory / 'preferences.md'
    if path.is_file():
        lines = path.read_text(encoding='utf-8').splitlines()
        for key, title in SECTIONS.items():
            start, end = bounds(lines, title)
            if start is None:
                errors.append(f'缺少分区：{title}')
            elif key != 'open':
                for line in lines[start + 1:end]:
                    if re.match(r'^- \[[^]]+\]\[inferred\]', line):
                        errors.append(f'推断越界 [{title}]：{line}')
    for error in errors:
        print(f'  - {error}')
    return not errors


def install(args):
    # Host selection is explicit; do not modify other agents' configuration.
    home = Path(args.agent_home).expanduser().resolve()
    destination = home / 'skills' / 'ppt-memory'
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.resolve() != SKILL:
        if destination.exists():
            raise ValueError(f'安装目标已存在，未覆盖：{destination}')
        shutil.copytree(SKILL, destination, ignore=shutil.ignore_patterns('__pycache__', '*.pyc', '.DS_Store'))
    agents = home / 'AGENTS.md'
    script = (destination / 'scripts' / 'ppt_memory.py').as_posix()
    skill = (destination / 'SKILL.md').as_posix()
    block = f'''{BEGIN}
## PPT 长期记忆（ppt-memory）
制作、修改或评审 PPT / 幻灯片 / 演示文稿时，先读取 `{skill}`。
使用可用的 Python 3.9+ 运行 `"{script}" show --root "<当前项目绝对路径>"`，读取长期与项目记忆；再调用实际 PPT 制作工具。
可复用且明确的偏好写入长期层；本项目源文件、版本、页数和专用设计留在项目层。
用户本轮指令 > 项目偏好 > 长期偏好 > 制作工具默认规范。推断只能进 open。
本协议不授权额外生成 PPT，也不自动安装制作依赖。
{END}'''
    with locked(home):
        old = agents.read_text(encoding='utf-8') if agents.exists() else ''
        if (BEGIN in old) != (END in old):
            raise ValueError('全局 AGENTS.md 的 ppt-memory 标记不完整，请修复后重试。')
        if BEGIN in old:
            new = old[:old.index(BEGIN)] + block + old[old.index(END) + len(END):]
        else:
            new = old.rstrip() + '\n\n' + block + '\n'
        atomic_write(agents, new)
    print(f'已安装：{destination}\n已配置触发入口：{agents}\n新会话由宿主读取全局规则；本命令不证明宿主已实际触发。')


def main(argv=None):
    # UTF-8 also when invoked through Windows redirected pipes.
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, 'reconfigure'):
            stream.reconfigure(encoding='utf-8')
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('command', choices=['init', 'show', 'add', 'check', 'install'])
    ap.add_argument('--root', default='.', help='当前项目根目录，不影响长期记忆路径')
    ap.add_argument('--global-root', help='长期存储目录；其次 PPT_MEMORY_HOME；默认 ~/.dsh/ppt-memory')
    ap.add_argument('--scope', choices=['global', 'project', 'both'], default=None)
    ap.add_argument('--section', choices=SECTIONS, default='content')
    ap.add_argument('--text', default='')
    ap.add_argument('--source', choices=['user', 'feedback', 'inferred'], default='user')
    ap.add_argument('--evidence', default='')
    ap.add_argument('--agent-home', default=str(Path.home() / '.dsh'), help='宿主全局配置目录，默认 ~/.dsh')
    args = ap.parse_args(argv)
    args.scope = args.scope or ('both' if args.command in ('show', 'check') else 'global')
    try:
        if args.command == 'install':
            install(args)
            return 0
        if args.command == 'add' and args.scope == 'both':
            raise ValueError('add 必须选择 global 或 project，不能双写。')
        good = True
        for label, directory, project in targets(args):
            if project and directory.resolve() == global_home(args.global_root).resolve():
                raise ValueError('长期目录不能与当前项目 .ppt-memory 相同。')
            if args.command == 'init':
                initialize(directory, project)
            elif args.command == 'add':
                if project:
                    # Validate before initialization so invalid requests do not write.
                    if args.source == 'inferred' and args.section != 'open':
                        raise ValueError('inferred 只能写入 open。')
                    initialize(directory, True)
                add(directory, args.section, args.text, args.source, args.evidence)
            elif args.command == 'show':
                print(f'===== {label}记忆：{directory} =====')
                for name in ['preferences.md'] + (['state.md'] if project else []):
                    path = directory / name
                    print(f'--- {name} ---\n' + (path.read_text(encoding='utf-8') if path.exists() else '(尚未建立；不影响读取另一层记忆)'))
                print('优先级：本轮用户指令 > 项目偏好 > 长期偏好 > 工具默认规范；open 不视为已确认偏好。')
            else:
                if not directory.exists() and project and args.scope == 'both':
                    print(f'项目记忆尚未建立，跳过：{directory}')
                    continue
                ok = check(directory, project)
                print(f'{label}记忆结构与来源检查：' + ('通过' if ok else '未通过'))
                good = good and ok
        if args.command == 'check':
            print('本检查不验证 PPT 内容、排版、字体或渲染结果。')
        return 0 if good else 1
    except (OSError, ValueError) as exc:
        print(f'错误：{exc}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
