#!/usr/bin/env python3
# ai-generated: patch the pinned Jitsi dependency for meet.egovm.ru builds.
import json
import pathlib
import shutil
import subprocess

module = "github.com/zarazaex69/j@v0.0.1"
info = json.loads(subprocess.check_output(["go", "mod", "download", "-json", module], text=True))
source = pathlib.Path(info["Dir"])
target = pathlib.Path(".jitsi-patch")
if target.exists():
    shutil.rmtree(target)
shutil.copytree(source, target)
# ai-generated: module cache files are read-only; make the copied patch writable.
path = target / "internal/xmpp/conn.go"
content = path.read_text()
needle = "cfg := fetchConfig(ctx, host, httpClient)"
assert content.count(needle) == 1, "Jitsi dependency changed; refusing unsafe patch"
replacement = needle + """
	// ai-generated: override XMPP virtualhost for meet.egovm.ru only.
	if host == "meet.egovm.ru" {
		cfg.xmppDomain = "meet.jitsi"
		cfg.mucDomain = "muc.meet.jitsi"
	}
"""
path.chmod(path.stat().st_mode | 0o200)
path.write_text(content.replace(needle, replacement, 1))
subprocess.run(["gofmt", "-w", str(path)], check=True)
subprocess.run(["go", "mod", "edit", "-replace=github.com/zarazaex69/j=./.jitsi-patch"], check=True)
print("Patched Jitsi XMPP domain for meet.egovm.ru")
