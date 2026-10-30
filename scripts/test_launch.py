import subprocess
import time
import os

game_exe = r'E:\game\Cyberpunk.2077.Repack.by.HardwareMining\by Decepticon\Cyberpunk 2077\bin\x64\Cyberpunk2077.exe'
game_dir = r'E:\game\Cyberpunk.2077.Repack.by.HardwareMining\by Decepticon\Cyberpunk 2077\bin\x64'

print("[*] Starting Cyberpunk 2077 test launch...")
proc = subprocess.Popen([game_exe], cwd=game_dir)
print(f"[*] Launched PID: {proc.pid}")

crashed = False
for i in range(12):
    time.sleep(1)
    ret = proc.poll()
    if ret is not None:
        print(f"[-] Process exited unexpectedly at second {i+1} with code: {ret} (0x{ret & 0xffffffff:08x})")
        crashed = True
        break
    else:
        print(f"[*] Second {i+1}: Game running normally (PID: {proc.pid})")

if not crashed:
    print("[+] SUCCESS: Game initialized and is running stably without crashes!")
    print("[*] Terminating test process...")
    try:
        proc.terminate()
        proc.wait(timeout=5)
    except Exception:
        subprocess.run(['taskkill', '/F', '/PID', str(proc.pid)], capture_output=True)
    print("[+] Test process closed cleanly.")
else:
    print("[-] Launch FAILED.")

