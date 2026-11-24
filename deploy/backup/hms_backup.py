#!/usr/bin/env python3
"""Encrypted backup helper for مستشفى سويد (AES-256-GCM, chunked).

Commands:
  keygen  KEYFILE                  create a new random 256-bit key (refuses to overwrite)
  encrypt SRC DST KEYFILE          encrypt SRC into DST, writes DST.sha256 (plaintext hash)
  decrypt SRC DST KEYFILE          decrypt SRC into DST and check DST.sha256 if present
  verify  SRC KEYFILE              decrypt to a temp file and check it is a readable pg_dump archive

File format: MAGIC(6) | prefix(8) | { len(4, big-endian) | last(1) | ciphertext+tag }*
Each chunk nonce = prefix(8) + chunk index(4). AAD = index(4) + last(1), so chunks
cannot be reordered, dropped, or truncated without the tag check failing.
"""
import base64
import hashlib
import os
import struct
import subprocess
import sys
import tempfile

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

MAGIC = b"HMSBK1"
CHUNK = int(os.environ.get("HMS_CHUNK", str(64 * 1024 * 1024)))


def load_key(path):
    with open(path, encoding="utf-8") as f:
        key = base64.b64decode(f.read().strip())
    if len(key) != 32:
        sys.exit("المفتاح يجب أن يكون 32 بايت (AES-256)")
    return key


def keygen(path):
    if os.path.exists(path):
        sys.exit("المفتاح موجود مسبقاً ولن يُستبدل")
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(base64.b64encode(os.urandom(32)).decode() + "\n")
    os.chmod(path, 0o600)


def encrypt(src, dst, key_path):
    aes = AESGCM(load_key(key_path))
    prefix = os.urandom(8)
    sha = hashlib.sha256()
    tmp = dst + ".tmp"
    with open(src, "rb") as fi, open(tmp, "wb") as fo:
        fo.write(MAGIC + prefix)
        idx = 0
        buf = fi.read(CHUNK)
        while True:
            nxt = fi.read(CHUNK)
            last = not nxt
            sha.update(buf)
            ct = aes.encrypt(prefix + struct.pack(">I", idx), buf,
                             struct.pack(">I?", idx, last))
            fo.write(struct.pack(">IB", len(ct), int(last)) + ct)
            idx += 1
            if last:
                break
            buf = nxt
    os.replace(tmp, dst)
    with open(dst + ".sha256", "w", encoding="utf-8") as f:
        f.write(sha.hexdigest() + "\n")
    return sha.hexdigest()


def decrypt(src, dst, key_path):
    aes = AESGCM(load_key(key_path))
    sha = hashlib.sha256()
    tmp = dst + ".tmp"
    with open(src, "rb") as fi:
        if fi.read(len(MAGIC)) != MAGIC:
            sys.exit("الملف ليس نسخة احتياطية من هذا النظام")
        prefix = fi.read(8)
        idx = 0
        saw_last = False
        with open(tmp, "wb") as fo:
            while not saw_last:
                hdr = fi.read(5)
                if len(hdr) != 5:
                    sys.exit("الملف مقطوع")
                n, last = struct.unpack(">IB", hdr)
                ct = fi.read(n)
                if len(ct) != n:
                    sys.exit("الملف مقطوع")
                try:
                    pt = aes.decrypt(prefix + struct.pack(">I", idx), ct,
                                     struct.pack(">I?", idx, bool(last)))
                except Exception:
                    sys.exit("فشل التحقق: المفتاح خاطئ أو الملف تالف")
                sha.update(pt)
                fo.write(pt)
                idx += 1
                saw_last = bool(last)
    os.replace(tmp, dst)
    manifest = src + ".sha256"
    if os.path.exists(manifest):
        with open(manifest, encoding="utf-8") as f:
            if f.read().strip() != sha.hexdigest():
                sys.exit("بصمة النسخة لا تطابق المسجّلة")
    return sha.hexdigest()


def verify(src, key_path):
    with tempfile.TemporaryDirectory() as d:
        out = os.path.join(d, "dump")
        decrypt(src, out, key_path)
        r = subprocess.run(["pg_restore", "--list", out],
                           stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        if r.returncode != 0:
            sys.exit("أرشيف pg_dump غير صالح: " + r.stderr.decode(errors="replace")[:300])
    print("verify ok")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    cmd, args = sys.argv[1], sys.argv[2:]
    if cmd == "keygen":
        keygen(args[0])
        print("key created")
    elif cmd == "encrypt":
        print("sha256", encrypt(args[0], args[1], args[2]))
    elif cmd == "decrypt":
        print("sha256", decrypt(args[0], args[1], args[2]))
    elif cmd == "verify":
        verify(args[0], args[1])
    else:
        sys.exit(__doc__)
