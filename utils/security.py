# -*- coding: utf-8 -*-

import hashlib
import os
import platform
import subprocess
import binascii
from Crypto.Cipher import AES  # 需要安装pycryptodome库: pip install pycryptodome
from Crypto.Util.Padding import pad, unpad
from binascii import hexlify, unhexlify

def get_disk_serial_windows():
    import wmi
    c = wmi.WMI()
    for disk in c.Win32_PhysicalMedia():
        return disk.SerialNumber.strip()

def get_disk_serial_macos():
    try:
        result = subprocess.run(['ioreg', '-l'], capture_output=True, text=True)
        serial_number = None
        for line in result.stdout.splitlines():
            if "IOPlatformSerialNumber" in line:
                serial_number = line.split('=', 1)[1].strip('" ')
                break
        return serial_number
    except Exception as e:
        print(f"Error getting disk serial on macOS: {e}")
        return None

def generate_key_from_serial():
    os_platform = platform.system()
    serial_number = None

    if os_platform == "Windows":
        serial_number = get_disk_serial_windows()
    elif os_platform == "Darwin":  # macOS
        serial_number = get_disk_serial_macos()
    if not serial_number:
        print("Failed to retrieve disk serial number on macOS.")
        return None
    
    # 使用SHA-256生成固定长度的密钥
    sha256_hash = hashlib.sha256()
    sha256_hash.update(serial_number.encode('utf-8'))
    return sha256_hash.digest()

def encrypt_string(plaintext):
    key = generate_key_from_serial() 
    if not key:
        return None
    cipher = AES.new(key, AES.MODE_EAX)
    ciphertext, tag = cipher.encrypt_and_digest(pad(plaintext.encode(), AES.block_size))
    return binascii.hexlify(cipher.nonce + tag + ciphertext).decode()

def decrypt_string(encrypted_data_hex):
    try:
        encrypted_data = unhexlify(encrypted_data_hex)
        key = generate_key_from_serial() 
        if not key:
            return None
        nonce, tag, ciphertext = encrypted_data[:16], encrypted_data[16:32], encrypted_data[32:]
        cipher = AES.new(key, AES.MODE_EAX, nonce=nonce)
        try:
            decrypted_data = cipher.decrypt_and_verify(ciphertext, tag)
            return unpad(decrypted_data, AES.block_size).decode()
        except:
            return None
    except:
        return None