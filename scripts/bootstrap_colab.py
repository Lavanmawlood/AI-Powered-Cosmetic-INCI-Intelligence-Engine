from pathlib import Path
import subprocess
import shutil

PROJECT_ROOT = Path("/content/lav-lab")
REPO_URL = "https://github.com/Lavanmawlood/AI-Powered-Cosmetic-INCI-Intelligence-Engine.git"


def run_command(command, cwd=None):
    result = subprocess.run(
        command,
        cwd=cwd,
        text=True,
        capture_output=True
    )

    if result.returncode != 0:
        print(result.stderr)
        raise RuntimeError("Command failed")

    return result.stdout.strip()


print("=" * 60)
print("🧪 LAV LAB — COLAB BOOTSTRAP")
print("=" * 60)

if not PROJECT_ROOT.exists():
    print("\n📥 Cloning LAV LAB...")
    run_command([
        "git", "clone", REPO_URL, str(PROJECT_ROOT)
    ])
    print("✅ Repository cloned.")

else:
    print("\n🔍 Checking LAV LAB workspace...")

    if not (PROJECT_ROOT / ".git").exists():
        print("⚠️ Git repository missing.")
        print("🧹 Restoring from GitHub...")

        shutil.rmtree(PROJECT_ROOT)

        run_command([
            "git", "clone", REPO_URL, str(PROJECT_ROOT)
        ])

        print("✅ Repository restored.")

    else:
        print("✅ Project already exists.")
        print("🔄 Pulling latest changes...")

        try:
            run_command(
                ["git", "pull", "--ff-only", "origin", "main"],
                cwd=PROJECT_ROOT
            )
            print("✅ Repository updated.")

        except Exception:
            print("⚠️ Pull failed. Local workspace preserved.")


print("\n🔍 Verifying project...")

required_files = [
    "README.md",
    ".gitignore",
    ".env.example",
    "requirements.txt",
]

for file_name in required_files:
    exists = (PROJECT_ROOT / file_name).exists()
    print(f"{'✅' if exists else '⚠️'} {file_name}")


print("\n📊 Git status:")

try:
    status = run_command(
        ["git", "status", "--short"],
        cwd=PROJECT_ROOT
    )

    print(status if status else "✅ Working tree clean.")

except Exception:
    print("⚠️ Git status unavailable.")


print("\n" + "=" * 60)
print("🎉 LAV LAB IS READY")
print("=" * 60)
