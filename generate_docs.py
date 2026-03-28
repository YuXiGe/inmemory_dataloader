import os

# フォーマット崩れを防ぐための記号定義
B3 = '`' * 3  # バックテック3つ
T3 = '"' * 3  # ダブルクォート3つ

# 1. .gitignore の内容
gitignore_content = f"""# Pixi environments
.pixi/
pixi.lock

# Python
__pycache__/
*.py[cod]
*$py.class
.pytest_cache/

# Compiled C++ / Shared Libraries
*.so
*.o
src/core/secure_loader.so

# Data / Generated files (Do not commit sensitive or dummy data)
*.bin
nagasaki_sample.bin
nagasaki_flow_data.bin

# OS generated files
.DS_Store
Thumbs.db
"""

# 2. README.md の内容
readme_content = f"""# 長崎街なか回遊促進 - セキュア・インメモリ・ローダー

本リポジトリは、「長崎街なか回遊促進」プロジェクトにおけるデータ分析基盤のプロトタイプです。
機密性の高い回遊データを安全に処理するため、ディスクに生データを一切保存せず、**メインメモリ（RAM）上でのみ復号・演算・破棄を完結させる「完全インメモリ・ローダー」** を実装しています。

## 🛡️ セキュリティ設計と実装のポイント

本ローダーのC++実装（{B3}src/core/secure_loader.cpp{B3}）では、データ漏洩リスクを最小化するため、以下の厳密なメモリ管理を行っています。これらは開発初期のレビューにおいて重要性が確認された設計指針です。

- **最適化による「証跡抹消」の無効化防止**
    - 通常の {B3}std::fill{B3} 等によるメモリのゼロクリアは、コンパイラ（GCCの {B3}-O3{B3} など）の「Dead Store Elimination（不要な書き込みの削除）」によって最適化で消されてしまうリスクがあります。
    - **対策:** 本実装では、ポインタを {B3}volatile unsigned char*{B3} にキャストして上書きすることで、コンパイラに書き込みを強制し、確実な証跡抹消を保証しています。
- **メモリスワップ（ページアウト）の防止**
    - OSのメモリ管理機能により、RAM上のデータがディスクのSwap領域（スワップファイル）に書き出されてしまうと、物理的なディスク上に生データの痕跡が残る可能性があります。
    - **対策:** {B3}mlock(){B3} 関数を使用して確保したバッファを物理メモリに固定（ロック）し、スワップアウトをOSレベルで禁止しています。処理後は {B3}munlock(){B3} で安全に解除します。

---

## 🚀 環境構築 (Pixiの利用)

本プロジェクトでは、依存関係の競合（特にCUDA 11.8とGCCコンパイラのバージョン管理）を完全に制御するため、パッケージマネージャとして **[Pixi](https://pixi.sh/)** を採用しています。

### 1. Pixi のインストール
システムにPixiがインストールされていない場合は、公式ドキュメント（[Installation](https://pixi.prefix.dev/latest/installation/)）に従い、以下のコマンドでインストールしてください。

{B3}bash
curl -fsSL https://pixi.sh/install.sh | bash
{B3}

### 2. 環境のセットアップ ({B3}pixi install{B3})
リポジトリのルートディレクトリで以下のコマンドを実行します。

{B3}bash
pixi install
{B3}

**{B3}pixi install{B3} の役割:**
{B3}pixi.toml{B3} に定義された依存パッケージ（Python 3.11, FastAPI, CUDA 11.8, GCC 11等）を、システム環境を汚すことなく {B3}.pixi/{B3} フォルダ内に隔離してインストールします。

---

## 💻 実行タスク

Pixiのタスク機能を使って各工程を実行します。

1. **セキュア・ローダーのビルド**
   {B3}bash
   pixi run build-secure-loader
   {B3}
   - サーバーのGPU（Ampere世代: sm_86）とCUDA 11.8に適合するよう、Pixi内のGCC 11を用いてビルドします。

2. **FastAPI サーバーの起動**
   {B3}bash
   pixi run start-api
   {B3}
   - 秘匿計算を実行するバックエンドAPI（ポート8000）を起動します。

3. **Streamlit GUI の起動**
   {B3}bash
   pixi run run-gui
   {B3}
   - 地図上（Pydeck）に演算結果を可視化するダッシュボード（ポート8501）を起動します。

---

## 🛠️ 開発者
- yukishige.kawaguchi
"""

def create_file(filename, content):
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"✨ Successfully created: {{filename}}")

if __name__ == "__main__":
    create_file(".gitignore", gitignore_content)
    create_file("README.md", readme_content)
