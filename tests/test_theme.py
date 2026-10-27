import json
import shutil
import subprocess

import pytest

from fasthtml_basecoat.assets import THEME_INIT

NODE = shutil.which("node")
pytestmark = pytest.mark.skipif(
    NODE is None, reason="Node.js is only used to test the browser theme bootstrap"
)


@pytest.mark.parametrize("mode", [None, "dark", "light", "invalid", "blocked"])
@pytest.mark.parametrize("system_dark", [False, True])
def test_theme_bootstrap_respects_saved_mode_and_system_preference(mode, system_dark):
    assert NODE is not None
    expected = {"dark": True, "light": False}.get(mode, system_dark)
    program = """
const vm = require('node:vm');
const input = JSON.parse(require('node:fs').readFileSync(0, 'utf8'));
let dark = input.initial;
vm.runInNewContext(input.code, {
  localStorage: { getItem() {
    if (input.mode === 'blocked') throw new Error('Storage unavailable');
    return input.mode;
  } },
  matchMedia: () => ({ matches: input.system_dark }),
  document: { documentElement: { classList: { toggle(name, value) {
    if (name !== 'dark') throw new Error('Unexpected class');
    dark = value;
  } } } },
});
process.stdout.write(JSON.stringify(dark));
"""
    result = subprocess.run(
        [NODE, "-e", program],
        input=json.dumps(
            {
                "mode": mode,
                "system_dark": system_dark,
                "initial": not expected,
                "code": THEME_INIT,
            }
        ),
        text=True,
        capture_output=True,
        check=True,
        timeout=5,
    )
    assert json.loads(result.stdout) is expected
