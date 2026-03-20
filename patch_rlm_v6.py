#!/usr/bin/env python3
"""
patch_rlm_v6.py - Live2D Cubism 5.3 RLM 授权绕过补丁

原理：对 rlm1603.dll 的 6 个 JNI 导出函数入口写入 mov eax, N; ret (6 字节)，
使 Java 层认为 checkout 成功、授权有效、剩余 9999 天。

用法：python patch_rlm_v6.py rlm1603.dll
"""
import struct, sys, os, shutil

def read_u16(d, o): return struct.unpack_from('<H', d, o)[0]
def read_u32(d, o): return struct.unpack_from('<I', d, o)[0]

def run(target):
    with open(target, 'rb') as f:
        data = bytearray(f.read())

    e_lfanew = read_u32(data, 0x3C)
    opt_hdr_size = read_u16(data, e_lfanew + 20)
    num_sects = read_u16(data, e_lfanew + 6)
    so_off = e_lfanew + 24 + opt_hdr_size
    sects = []
    for i in range(num_sects):
        so = so_off + i * 40
        sects.append({
            'va': read_u32(data, so + 12),
            'size': read_u32(data, so + 16),
            'ptr': read_u32(data, so + 20),
        })

    def rva2off(rva):
        for s in sects:
            if s['va'] <= rva < s['va'] + s['size']:
                return rva - s['va'] + s['ptr']
        return -1

    magic = read_u16(data, e_lfanew + 24)
    export_dir_offset = 112 if magic == 0x20B else 96  # PE32+ vs PE32
    opt_rva = read_u32(data, e_lfanew + 24 + export_dir_offset)
    eo = rva2off(opt_rva)
    num_names = read_u32(data, eo + 24)
    funcs_off = rva2off(read_u32(data, eo + 28))
    names_off = rva2off(read_u32(data, eo + 32))
    ords_off  = rva2off(read_u32(data, eo + 36))

    exports = {}
    for i in range(num_names):
        n_rva = read_u32(data, names_off + i * 4)
        name = data[rva2off(n_rva):].split(b'\x00')[0].decode('ascii')
        ordinal = read_u16(data, ords_off + i * 2)
        f_rva = read_u32(data, funcs_off + ordinal * 4)
        off = rva2off(f_rva)
        if off >= 0:
            exports[name] = off

    patches = {
        'Java_com_reprisesoftware_rlm_RlmLicense_rlmCheckout': 0,
        'Java_com_reprisesoftware_rlm_RlmLicense_rlmCheckoutProduct': 0,
        'Java_com_reprisesoftware_rlm_RlmLicense_rlmLicenseStat': 0,
        'Java_com_reprisesoftware_rlm_RlmHandle_rlmStat': 0,
        'Java_com_reprisesoftware_rlm_RlmLicense_rlmAuthCheck': 0,
        'Java_com_reprisesoftware_rlm_RlmLicense_rlmLicenseExpDays': 9999,
    }

    cnt = 0
    for func_name, ret_val in patches.items():
        if func_name in exports:
            off = exports[func_name]
            asm = b'\xB8' + struct.pack('<i', ret_val) + b'\xC3'
            data[off:off+6] = asm
            print(f"  [+] {func_name} -> return {ret_val}")
            cnt += 1
        else:
            print(f"  [-] {func_name} NOT FOUND")

    with open(target, 'wb') as f:
        f.write(data)
    print(f"\n  Done! {cnt} functions patched.")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python patch_rlm_v6.py <path_to_rlm1603.dll>")
        sys.exit(1)
    target = sys.argv[1]
    if not os.path.exists(target):
        print(f"Error: {target} not found")
        sys.exit(1)
    if not os.path.exists(target + ".bak"):
        shutil.copy2(target, target + ".bak")
        print(f"  Backup: {target}.bak")
    run(target)
