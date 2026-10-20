"""Build the portable SayedTech app folder from the checked-out release source."""
from pathlib import Path
import json
import os
import shutil
import subprocess
import sys
import sysconfig
import tempfile
from ensure_dependencies import ensure

ROOT = Path(__file__).resolve().parent


def clean_environment():
    env = dict(os.environ)
    for key in list(env):
        if key.upper().startswith(("PYTHON", "VIRTUAL_ENV", "QT_", "PYSIDE", "PLAYWRIGHT")):
            env.pop(key, None)
    windows = env.get("SystemRoot", r"C:\Windows")
    env["PATH"] = os.pathsep.join([windows, str(Path(windows) / "System32")])
    return env


def main():
    if sys.platform != "win32" or sysconfig.get_platform() != "win-amd64":
        raise RuntimeError("Build this release on Windows x64.")
    os.chdir(ROOT)
    ensure()
    subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller==6.22.3"], check=True)
    env = dict(os.environ, PLAYWRIGHT_BROWSERS_PATH="0")
    subprocess.run(
        [sys.executable, "-m", "playwright", "install", "firefox", "chromium"],
        env=env,
        check=True,
    )
    with tempfile.TemporaryDirectory(prefix="SayedTech-build-") as temp:
        stage = Path(temp)
        common = [
            sys.executable,
            "-m",
            "PyInstaller",
            "--noconfirm",
            "--clean",
            "--onedir",
            "--distpath",
            str(stage / "dist"),
            "--workpath",
            str(stage / "work"),
            "--specpath",
            str(stage),
            "--add-data",
            str(ROOT / "assets") + ";assets",
        ]
        subprocess.run(
            common
            + [
                "--windowed",
                "--name",
                "SayedTech",
                "--collect-all",
                "sqlce",
                str(ROOT / "app.py"),
            ],
            env=env,
            check=True,
        )
        subprocess.run(
            common
            + [
                "--console",
                "--name",
                "SayedTechLogin",
                "--collect-all",
                "playwright",
                str(ROOT / "login_worker.py"),
            ],
            env=env,
            check=True,
        )
        package = stage / "dist" / "SayedTech"
        helper = package / "helpers" / "SayedTechLogin"
        helper.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(stage / "dist" / "SayedTechLogin", helper)
        verify_env = clean_environment()
        for executable in (package / "SayedTech.exe", helper / "SayedTechLogin.exe"):
            subprocess.run(
                [str(executable), "--bundle-self-test"],
                env=verify_env,
                cwd=stage,
                check=True,
                timeout=120,
            )
        readme = ROOT / "README_PORTABLE_AR.txt"
        if readme.exists():
            shutil.copy2(readme, package / "README_AR.txt")
        verifier = ROOT / "VERIFY_PORTABLE_WINDOWS.bat"
        if verifier.exists():
            shutil.copy2(verifier, package / "VERIFY_PORTABLE_WINDOWS.bat")
        import core

        (package / "BUILD_INFO.json").write_text(
            json.dumps(
                {
                    "app": core.APP_VERSION,
                    "python": sys.version.split()[0],
                    "platform": "Windows x64",
                    "bundled_browsers": ["Firefox", "Chromium"],
                    "offline_smoke_checks": "passed",
                },
                indent=2,
            ),
            encoding="utf-8",
        )
        output = ROOT / "dist"
        output.mkdir(exist_ok=True)
        archive = shutil.make_archive(
            str(stage / "SayedTech-Windows-x64"), "zip", stage / "dist", "SayedTech"
        )
        temporary = output / "SayedTech-Windows-x64.new.zip"
        shutil.copy2(archive, temporary)
        os.replace(temporary, output / "SayedTech-Windows-x64.zip")
        print("Portable app package ready:", output / "SayedTech-Windows-x64.zip")


if __name__ == "__main__":
    main()
