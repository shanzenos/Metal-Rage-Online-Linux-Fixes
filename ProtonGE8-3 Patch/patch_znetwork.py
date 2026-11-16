#!/usr/bin/env python3
"""ZNetwork.dll patch for Wine/Proton: close the socket after shutdown().

ZNetworkManager::Disconnect() -> FUN_107f9760 calls shutdown(sock, SD_BOTH) and only releases
the socket (closesocket + 'disconnected' flag that Tick() polls) if shutdown() fails. On Windows
the release normally happens later through the FD_CLOSE network event. Under Wine that event is
never delivered after a local shutdown, so the socket handle stays open, Disconnect_Complete never
runs and the client never opens the next connection (game server / retry login).

Fix: NOP the 'jnz' after shutdown so the release path always runs (2 bytes at RVA 0xF9772).
Usage: python3 patch_znetwork.py [path/to/data/System/ZNetwork.dll]
"""
import os, shutil, sys

OFF = 0xF9760  # function start, file offset == RVA for this DLL's .text
CTX = bytes.fromhex("568bf18b46206a0250ff15f4be9110" "83f8ff")  # push esi .. cmp eax,-1
JNZ = OFF + len(CTX)
ORIG = bytes.fromhex("7508")
NEW = bytes.fromhex("9090")

path = sys.argv[1] if len(sys.argv) > 1 else os.path.join("data", "System", "ZNetwork.dll")
data = bytearray(open(path, "rb").read())
if bytes(data[OFF:JNZ]) != CTX:
    print("Unexpected ZNetwork.dll (function bytes differ)"); sys.exit(1)
cur = bytes(data[JNZ:JNZ + 2])
if cur == NEW:
    print("Already patched"); sys.exit(0)
if cur != ORIG:
    print("Unexpected bytes at 0x%X: %s" % (JNZ, cur.hex())); sys.exit(1)
if not os.path.exists(path + ".original"):
    shutil.copy2(path, path + ".original")
data[JNZ:JNZ + 2] = NEW
open(path, "wb").write(data)
print("Patched", path)
