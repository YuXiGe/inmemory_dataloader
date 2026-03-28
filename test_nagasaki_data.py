import ctypes
import numpy as np
import os
import time

# 1. 共有ライブラリのロード
lib_path = os.path.abspath("src/core/secure_loader.so")
secure_lib = ctypes.CDLL(lib_path)

# 型定義
secure_lib.secure_compute_cpu.argtypes = [
    ctypes.c_char_p, 
    ctypes.POINTER(ctypes.c_float), 
    ctypes.c_float, 
    ctypes.c_ubyte
]

def generate_nagasaki_sample(filename, num_records=1000):
    """
    長崎の回遊データを模した暗号化バイナリを生成
    (例: 緯度, 経度, 滞在秒数, 属性フラグ のセットを想定)
    """
    print(f"📦 Generating {num_records} dummy records for Nagasaki movement...")
    # ランダムなfloatデータを作成
    data = np.random.rand(num_records).astype(np.float32)
    key = 0x5A  # プロジェクト指定の仮鍵
    
    # XOR暗号化して保存
    encrypted = (data.view(np.uint8) ^ key).tobytes()
    with open(filename, "wb") as f:
        f.write(encrypted)
    return key, num_records

def run_nagasaki_test():
    filename = "nagasaki_flow_data.bin"
    key, n = generate_nagasaki_sample(filename, 5000)
    
    # 結果格納用 (float32)
    output = np.zeros(n, dtype=np.float32)
    output_ptr = output.ctypes.data_as(ctypes.POINTER(ctypes.c_float))
    
    print(f"🔐 Executing Secure In-Memory Loader...")
    start_time = time.time()
    
    # C++側のセキュア計算呼び出し
    # sigma=1.5 (波動演算のパラメータ)
    secure_lib.secure_compute_cpu(filename.encode(), output_ptr, 1.5, key)
    
    end_time = time.time()
    
    print("-" * 30)
    print(f"⏱️  Processing Time: {end_time - start_time:.6f} sec")
    print(f"📊 First 5 results: {output[:5]}")
    print(f"🧹 Security Check: Raw file will be deleted now.")
    
    if os.path.exists(filename):
        os.remove(filename)
    print("✨ Nagasaki Data Test Completed.")

if __name__ == "__main__":
    run_nagasaki_test()
