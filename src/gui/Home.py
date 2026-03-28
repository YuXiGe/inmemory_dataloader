import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import requests

st.set_page_config(page_title="Nagasaki Flow Visualizer", layout="wide")

st.title("🌊 長崎街なか回遊促進 - 秘匿演算ダッシュボード")

with st.sidebar:
    st.header("⚙️ 設定")
    sigma = st.slider("波動パラメータ (sigma)", 0.1, 5.0, 1.5)
    key = st.number_input("復号鍵 (XOR Key)", value=90)
    if st.button("データ再計算"):
        st.rerun()

# 1. API を叩いて計算結果を取得
def get_secure_data():
    try:
        # テスト用ファイルの指定（本来はアップロード機能など）
        payload = {
            "file_path": "nagasaki_sample.bin",
            "num_records": 4,
            "sigma": sigma,
            "key": key
        }
        res = requests.post("http://0.0.0.0:8000/compute", json=payload)
        return res.json()
    except Exception as e:
        return None

data_res = get_secure_data()

if data_res and data_res.get("status") == "success":
    st.success(f"🔐 {data_res['message']}")
    
    # 2. 長崎市内のダミー座標にマッピング（デモ用）
    # 本来は演算結果(results_sample)を緯度経度として解釈
    n = data_res["count"]
    df = pd.DataFrame({
        "lat": np.random.uniform(32.74, 32.75, n),
        "lon": np.random.uniform(129.87, 129.88, n),
        "value": data_res["results_sample"]
    })

    # 3. Pydeck による 3D 可視化
    view_state = pdk.ViewState(latitude=32.745, longitude=129.875, zoom=14, pitch=45)
    
    layer = pdk.Layer(
        "ColumnLayer",
        df,
        get_position="[lon, lat]",
        get_elevation="value * 1000",
        elevation_scale=1,
        radius=20,
        get_fill_color="[255, value * 255, 150, 200]",
        pickable=True,
    )

    st.pydeck_chart(pdk.Deck(layers=[layer], initial_view_state=view_state))
    st.write("📋 演算結果サンプル:", df)
else:
    st.error("APIへの接続、または計算に失敗しました。")
