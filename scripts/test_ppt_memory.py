"""Isolated behavioral tests: no real user memory/configuration is read or changed."""
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).with_name('ppt_memory.py')


class MemoryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='ppt memory 中文 ')
        self.base = Path(self.temp.name)
        self.global_dir = self.base / 'long term'
        self.project_a = self.base / '项目 A'
        self.project_b = self.base / '项目 B'
        self.project_a.mkdir()
        self.project_b.mkdir()
        self.env = dict(os.environ, PPT_MEMORY_HOME=str(self.global_dir), PYTHONIOENCODING='utf-8')

    def tearDown(self):
        self.temp.cleanup()

    def run_cli(self, *args, cwd=None, code=0, script=SCRIPT):
        result = subprocess.run([sys.executable, str(script), *args], cwd=cwd or self.project_a,
                                env=self.env, capture_output=True, text=True, encoding='utf-8')
        self.assertEqual(result.returncode, code, result.stdout + result.stderr)
        return result.stdout + result.stderr

    def test_shared_memory_and_project_isolation(self):
        self.run_cli('add', '--section', 'aesthetics', '--text', '减少框型结构')
        self.run_cli('add', '--scope', 'project', '--text', '只读 A 的源文档')
        a = self.run_cli('show')
        b = self.run_cli('show', cwd=self.project_b)
        self.assertIn('减少框型结构', a)
        self.assertIn('减少框型结构', b)
        self.assertIn('只读 A 的源文档', a)
        self.assertNotIn('只读 A 的源文档', b)
        self.assertFalse((self.global_dir / 'state.md').exists())
        self.assertFalse((self.project_b / '.ppt-memory').exists())
        self.run_cli('check', cwd=self.project_b)

    def test_inference_rejected_and_pending_allowed(self):
        self.run_cli('add', '--source', 'inferred', '--text', '猜测', code=2)
        self.assertFalse(self.global_dir.exists())
        self.run_cli('add', '--source', 'inferred', '--section', 'open', '--text', '猜测')
        self.run_cli('check')

    def test_legacy_bad_inference_detected(self):
        self.run_cli('init', '--scope', 'project')
        path = self.project_a / '.ppt-memory' / 'preferences.md'
        path.write_text(path.read_text(encoding='utf-8').replace('## 一、内容偏好',
                        '## 一、内容偏好\n- [2026-11-04][inferred] 未确认'), encoding='utf-8')
        result = self.run_cli('check', '--scope', 'project', code=1)
        self.assertIn('推断越界', result)

    def test_exact_dedup_does_not_drop_shorter_rule(self):
        for value in ('不要卡片和阴影', '不要卡片', '不要卡片'):
            self.run_cli('add', '--text', value)
        raw = (self.global_dir / 'preferences.md').read_text(encoding='utf-8')
        self.assertEqual(raw.count('[user]'), 2)

    def test_init_preserves_existing_state(self):
        self.run_cli('init', '--scope', 'project')
        path = self.project_a / '.ppt-memory' / 'state.md'
        path.write_text('原始版本状态', encoding='utf-8')
        self.run_cli('init', '--scope', 'project')
        self.assertEqual(path.read_text(encoding='utf-8'), '原始版本状态')

    def test_relative_global_path_rejected(self):
        self.run_cli('add', '--global-root', 'relative', '--text', '不应写入', code=2)
        self.assertFalse((self.project_a / 'relative').exists())

    def test_explicit_storage_wins_over_environment(self):
        other = self.base / 'override'
        self.run_cli('add', '--global-root', str(other), '--text', '显式存储')
        self.assertTrue((other / 'preferences.md').exists())
        self.assertFalse(self.global_dir.exists())

    def test_installed_copy_and_global_trigger(self):
        home = self.base / 'DSH home'
        home.mkdir()
        agents = home / 'AGENTS.md'
        agents.write_text('# 已有规则\n保留内容\n', encoding='utf-8')
        self.run_cli('install', '--agent-home', str(home))
        installed = home / 'skills/ppt-memory/scripts/ppt_memory.py'
        self.run_cli('install', '--agent-home', str(home), script=installed)
        rule = agents.read_text(encoding='utf-8')
        self.assertIn('保留内容', rule)
        self.assertEqual(rule.count('<!-- ppt-memory:begin -->'), 1)
        self.assertIn(installed.as_posix(), rule)
        self.run_cli('add', '--text', '安装后长期偏好', script=installed)
        self.assertIn('安装后长期偏好', self.run_cli('show', cwd=self.project_b, script=installed))

    def test_concurrent_writes_keep_all_preferences(self):
        processes = [subprocess.Popen([sys.executable, str(SCRIPT), 'add', '--text', f'偏好 {i}'],
                     cwd=self.project_a, env=self.env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                     for i in range(6)]
        for process in processes:
            output, error = process.communicate(timeout=15)
            self.assertEqual(process.returncode, 0, output + error)
        raw = (self.global_dir / 'preferences.md').read_text(encoding='utf-8')
        for i in range(6):
            self.assertIn(f'偏好 {i}', raw)


if __name__ == '__main__':
    unittest.main()
