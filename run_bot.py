#!/usr/bin/env python3
"""
Chartwise Auto-Updater
Checks GitHub for new bot versions every hour and restarts automatically.
Run this instead of chartwise_bot.py
"""
import subprocess
import sys
import os
import time
import json
from pathlib import Path

REPO = "CryptoTTrades/chartwise-bot"
BOT_FILE = Path(__file__).parent / "chartwise_bot.py"
VERSION_FILE = Path(__file__).parent / "chartwise_version.json"
CHECK_INTERVAL = 3600  # 1 hour

def get_remote_sha():
    try:
        result = subprocess.run(
            ["git", "ls-remote", "origin", "HEAD"],
            capture_output=True, text=True, cwd=Path(__file__).parent, timeout=15
        )
        if result.returncode == 0:
            return result.stdout.split()[0]
    except Exception as e:
        print(f"[UPDATER] Could not check remote: {e}")
    return None

def get_local_sha():
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True, text=True, cwd=Path(__file__).parent, timeout=10
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except:
        pass
    return None

def pull_update():
    try:
        result = subprocess.run(
            ["git", "pull", "origin", "main"],
            capture_output=True, text=True, cwd=Path(__file__).parent, timeout=30
        )
        print(f"[UPDATER] Pull result: {result.stdout.strip()}")
        return result.returncode == 0
    except Exception as e:
        print(f"[UPDATER] Pull failed: {e}")
        return False

def run_bot():
    print(f"[UPDATER] Starting Chartwise bot...")
    return subprocess.Popen([sys.executable, str(BOT_FILE)])

def main():
    print("=" * 50)
    print("  Chartwise Auto-Updater")
    print("  Bot will auto-update and restart hourly")
    print("=" * 50)

    proc = run_bot()
    last_check = time.time()

    try:
        while True:
            time.sleep(30)

            # Check if bot crashed
            if proc.poll() is not None:
                print(f"[UPDATER] Bot exited with code {proc.returncode}. Restarting in 10s...")
                time.sleep(10)
                proc = run_bot()
                last_check = time.time()
                continue

            # Check for updates every hour
            if time.time() - last_check >= CHECK_INTERVAL:
                last_check = time.time()
                print("[UPDATER] Checking for updates...")

                remote_sha = get_remote_sha()
                local_sha = get_local_sha()

                if remote_sha and local_sha and remote_sha != local_sha:
                    print(f"[UPDATER] New version available! Updating...")
                    if pull_update():
                        print("[UPDATER] Update downloaded. Restarting bot...")
                        proc.terminate()
                        proc.wait(timeout=10)
                        proc = run_bot()
                        print("[UPDATER] Bot restarted with new version.")
                    else:
                        print("[UPDATER] Update failed, continuing with current version.")
                else:
                    print("[UPDATER] Already up to date.")

    except KeyboardInterrupt:
        print("\n[UPDATER] Shutting down...")
        proc.terminate()
        proc.wait(timeout=10)
        print("[UPDATER] Stopped.")

if __name__ == "__main__":
    main()
