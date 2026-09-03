from pathlib import Path
import subprocess

PROJECT_ROOT = Path("/content/lav-lab")


def run(command):
    result = subprocess.run(
        command,
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True
    )

    if result.returncode != 0:
        print("❌ Command failed:")
        print(result.stderr)
        raise RuntimeError("Save failed")

    return result.stdout.strip()


print("=" * 60)
print("💾 LAV LAB — SAVE & SYNC")
print("=" * 60)

# Check repository
if not (PROJECT_ROOT / ".git").exists():
    raise RuntimeError("❌ Git repository not found.")

# Check changes
status = run(["git", "status", "--short"])

if not status:
    print("✅ No changes to save.")
    print("☁️ GitHub is already up to date.")

else:
    print("\n📦 Changes detected:")
    print(status)

    # Stage everything
    print("\n📦 Staging changes...")
    run(["git", "add", "."])

    # Commit
    print("\n📝 Creating commit...")
    run([
        "git",
        "commit",
        "-m",
        "Update LAV LAB"
    ])

    # Push
    print("\n☁️ Pushing to GitHub...")
    run([
        "git",
        "push",
        "origin",
        "main"
    ])

    print("\n✅ Commit + Push successful.")


print("\n" + "=" * 60)
print("🎉 LAV LAB SAVED")
print("=" * 60)
