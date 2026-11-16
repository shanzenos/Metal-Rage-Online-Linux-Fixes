#!/usr/bin/env python3
"""Applies the DxDiag-skip patch to D3D9Drv.dll (same 8 bytes as the Win11 bundle copy).
Needed under Wine/Proton: dxdiagn enumeration fails, the engine gets NULL and crashes in
FMallocWindows::Free (MetalRage.exe+0x4505 'General protection fault').
Usage: python3 patch_d3d9drv.py [path/to/data/System/D3D9Drv.dll]
"""
import os, shutil, sys

OFF = 0xF040
ORIG = bytes.fromhex("83EC105 66A008BF1".replace(" ", ""))
NEW = bytes.fromhex("B001C2040090 9090".replace(" ", ""))

path = sys.argv[1] if len(sys.argv) > 1 else os.path.join("data", "System", "D3D9Drv.dll")
data = bytearray(open(path, "rb").read())
cur = bytes(data[OFF:OFF + 8])
if cur == NEW:
    print("Already patched"); sys.exit(0)
if cur != ORIG:
    print("Unexpected bytes at 0xF040:", cur.hex()); sys.exit(1)
if not os.path.exists(path + ".original"):
    shutil.copy2(path, path + ".original")
data[OFF:OFF + 8] = NEW
open(path, "wb").write(data)
print("Patched", path)
