'''
Author: your name
Date: 2021-07-15 10:05:16
LastEditTime: 2025-09-25 08:00:00
LastEditors: wdfk_prog
Description: Packages a binary patch file into an RBL package, using the new firmware file for header metadata.
FilePath: /pkg/package_tool.py
'''
import os
import struct
import zlib
import sys

# --- C语言宏定义对应的Python常量 ---

# 加密算法
QBOOT_ALGO_CRYPT_NONE = 0

# 压缩算法 (用于告知Bootloader包体类型是差分补丁)
QBOOT_ALGO_CMPRS_HPATCHLITE = (4 << 8)

# 校验算法
QBOOT_ALGO2_VERIFY_CRC = 1


def crc32(bytes_obj):
    """计算字节对象的CRC32校验和"""
    return zlib.crc32(bytes_obj) & 0xFFFFFFFF


def create_firmware_header(new_fw_obj, patch_obj, algo, algo2, timestamp, part_name_str, fw_ver_str, prod_code_str):
    """
    根据 fw_info_t 结构创建固件头部
    :param new_fw_obj: 新版本固件的完整数据 (用于 raw_size 和 raw_crc)
    :param patch_obj:  补丁文件的数据 (包的主体, 用于 pkg_size 和 pkg_crc)
    """
    # u8 type[4];
    type_name = b'RBL\x00'
    type_4 = struct.pack('4s', type_name)
    # u16 algo; u16 algo2;
    algo_pack = struct.pack('<H', algo)
    algo2_pack = struct.pack('<H', algo2)
    # u32 time_stamp;
    time_stamp_pack = struct.pack('<I', int(timestamp))
    # u8 part_name[16];
    part_name = struct.pack('16s', part_name_str.encode('utf-8'))
    # u8 fw_ver[24];
    fw_ver = struct.pack('24s', fw_ver_str.encode('utf-8'))
    # u8 prod_code[24];
    prod_code = struct.pack('24s', prod_code_str.encode('utf-8'))
    
    # u32 pkg_crc; -> 使用补丁文件计算
    pkg_crc_pack = struct.pack('<I', crc32(patch_obj))
    # u32 raw_crc; -> 使用新版本文件计算
    raw_crc_pack = struct.pack('<I', crc32(new_fw_obj))
    # u32 raw_size; -> 使用新版本文件计算
    raw_size_pack = struct.pack('<I', len(new_fw_obj))
    # u32 pkg_size; -> 使用补丁文件计算
    pkg_size_pack = struct.pack('<I', len(patch_obj))

    # 组装除头部CRC外的所有字段
    header_no_crc = (type_4 + algo_pack + algo2_pack + time_stamp_pack +
                     part_name + fw_ver + prod_code +
                     pkg_crc_pack + raw_crc_pack + raw_size_pack + pkg_size_pack)
    # u32 hdr_crc;
    hdr_crc_pack = struct.pack('<I', crc32(header_no_crc))
    return header_no_crc + hdr_crc_pack

def package_patch(patch_file, new_file, output_file):
    """为一个二进制补丁文件添加RBL头部"""
    print(f"--- Packaging Patch File: '{patch_file}' ---")
    
    # 1. 读取新版本文件 (new_fw_obj) 以获取 raw_size 和 raw_crc
    with open(new_file, "rb") as f:
        new_fw_obj = f.read()
    print(f"Read new file '{new_file}' for header info, size: {len(new_fw_obj)}")

    # 2. 读取补丁文件 (patch_obj)，它将作为包的主体
    with open(patch_file, "rb") as f:
        patch_obj = f.read()
    print(f"Read patch file (package body) '{patch_file}', size: {len(patch_obj)}")

    # 3. 创建头部
    algo = QBOOT_ALGO_CMPRS_HPATCHLITE
    algo2 = QBOOT_ALGO_CRYPT_NONE
    timestamp = os.path.getmtime(patch_file)

    my_head = create_firmware_header(
        new_fw_obj=new_fw_obj,
        patch_obj=patch_obj,
        algo=algo,
        algo2=algo2,
        timestamp=timestamp,
        part_name_str='app',
        fw_ver_str='v1.00',
        prod_code_str='00010203040506070809'
    )
    print(f"Generated header size: {len(my_head)}")
    
    # 4. 写入最终文件 (头部 + 原始补丁数据)
    with open(output_file, "wb") as f:
        f.write(my_head)
        f.write(patch_obj)
    print(f"Successfully created RBL patch package: '{output_file}'")


if __name__ == "__main__":
    # 检查命令行参数数量
    if len(sys.argv) < 3 or len(sys.argv) > 4:
        print(f"\nUsage: python {os.path.basename(sys.argv[0])} <patch_file> <new_file> [output_file]")
        print("\n  <patch_file>: The binary patch data (e.g., from hdiffi).")
        print("  <new_file>:   The new version file, used for header metadata (raw_size, raw_crc).")
        sys.exit(1)

    # 获取输入文件
    patch_file = sys.argv[1]
    new_file = sys.argv[2]
    
    if not os.path.exists(patch_file):
        print(f"Error: Patch file not found at '{patch_file}'")
        sys.exit(1)
    if not os.path.exists(new_file):
        print(f"Error: New file not found at '{new_file}'")
        sys.exit(1)
        
    # 决定输出文件
    if len(sys.argv) == 4:
        output_file = sys.argv[3]
    else:
        # 默认输出文件名 (e.g., light_patch.bin -> light_patch.rbl)
        base_name = os.path.splitext(patch_file)[0]
        output_file = f"{base_name}.rbl"
        
    # 执行打包
    package_patch(patch_file, new_file, output_file)