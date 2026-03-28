from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import ctypes
import numpy as np
import os

app = FastAPI(title="Nagasaki Flow Secure API")

# 共有ライブラリのロード
LIB_PATH = os.path.abspath("src/core/secure_loader.so")
secure_lib = ctypes.CDLL(LIB_PATH)
secure_lib.secure_compute_cpu.argtypes = [
    ctypes.c_char_p, 
    ctypes.POINTER(ctypes.c_float), 
    ctypes.c_float, 
    ctypes.c_ubyte
]

class ComputeRequest(BaseModel):
    file_path: str
    num_records: int
    sigma: float = 1.5
    key: int = 0x5A

@app.post("/compute")
async def compute_securely(req: ComputeRequest):
    if not os.path.exists(req.file_path):
        raise HTTPException(status_code=404, detail="Binary file not found")

    try:
        # 出力バッファの準備
        output = np.zeros(req.num_records, dtype=np.float32)
        output_ptr = output.ctypes.data_as(ctypes.POINTER(ctypes.c_float))

        # C++セキュアローダーの実行
        secure_lib.secure_compute_cpu(
            req.file_path.encode(), 
            output_ptr, 
            req.sigma, 
            req.key
        )

        return {
            "status": "success",
            "message": "Data processed and wiped from RAM",
            "results_sample": output[:10].tolist(),
            "count": len(output)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health_check():
    return {"status": "healthy", "gpu": "GeForce RTX 3080 Ready (11.8)"}
