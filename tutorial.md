title: "Vertex AI Search と ADK を用いた RAG Agent 作成ハンズオン"
description: "Vertex AI Search を用いて RAG を構築し, ADK を使って AI Agent を開発するハンズオンです"
duration: 60
level: Beginner
tags: [Vertex AI Search, ADK, AI Agent, Python, RAG]
---

# Vertex AI Search と ADK を用いた RAG Agent 作成ハンズオン

このハンズオンでは, Vertex AI Search を用いて RAG を構築し, RAG を用いた AI Agent 開発を ADK を用いて行います.

## Step 1. Google Cloud 環境のセットアップ

- Google アカウント認証
- プロジェクトの設定
- リージョンの設定
- 必要な API の有効化

## Step 1-1. Google アカウント 認証

以下のコマンドで現在の認証情報を確認します

```bash
gcloud auth list
```

想定しているログインアカウントが表示されれば OK です. もしアカウントが認証されていない場合は,

```bash
gcloud auth application-default login --no-launch-browser
```

を実行してログインを行います (ログイン URL が出てくるので, URL をクリック, verification code を入力しましょう)

### Step 1-2. プロジェクト ID とリージョンの設定

次に, 使用する Google Cloud プロジェクト ID とリージョンを設定します.

```bash
gcloud config set project PLEASE_SPECIFY_YOUR_PROJECT_ID
gcloud config set run/region us-central1
```

`PLEASE_SPECIFY_YOUR_PROJECT_ID` の部分は, ご自身のプロジェクト ID に置き換えてください.

設定したプロジェクト ID とリージョンは, 後ほど使用するため環境変数に設定しておきます.

```bash
export GOOGLE_CLOUD_PROJECT=$(gcloud config get-value project)
export GOOGLE_CLOUD_LOCATION=us-central1
```

### Step 1-3. 必要な API の有効化

このハンズオンで利用する Google Cloud の API を有効化します.

```bash
gcloud services enable aiplatform.googleapis.com \
    discoveryengine.googleapis.com \
    run.googleapis.com \
    cloudbuild.googleapis.com
```

## Step 2. Vertex AI Search のためのデータ準備

Vertex AI Search で RAG を行うためのデータを準備します. 今回は Google Cloud の利用規約 (日本語) の PDF をデータソースとして利用します.

### Step 2-1. データソースのダウンロード

まず, データソースとなる PDF ファイルをダウンロードします.

```bash
wget https://services.google.com/fh/files/misc/ja-google-cloud-terms-of-service.pdf -O gcp_tos_jp.pdf
```

### Step 2-2. Google Cloud Storage (GCS) バケットの作成

ダウンロードしたファイルをアップロードするための GCS バケットを作成します. バケット名は全世界でユニークである必要があるため, プロジェクト ID を含めた名前にします.

```bash
export BUCKET_NAME="${GOOGLE_CLOUD_PROJECT}-adk-vais-bucket"
gcloud storage buckets create gs://${BUCKET_NAME} --location=${GOOGLE_CLOUD_LOCATION}
```

### Step 2-3. GCS へのファイルアップロード

作成したバケットに, 先ほどダウンロードした PDF ファイルをアップロードします.

```bash
gcloud storage cp gcp_tos_jp.pdf gs://${BUCKET_NAME}/
```

## Step 3. Vertex AI Search の設定

次に, アップロードしたデータを元に Vertex AI Search のデータストアとアプリ (RAG Engine) を作成します.

### Step 3-1. データストアの作成

まず, GCS にアップロードした PDF ファイルを読み込むためのデータストアを作成します.

```bash
export DATA_STORE_ID="gcp-tos-jp-datastore"
gcloud alpha enterprise-search datastores create \
    --display-name="GCP Terms of Service (JP)" \
    --location=${GOOGLE_CLOUD_LOCATION} \
    --id=${DATA_STORE_ID} \
    --content-config=unstructured
```

### Step 3-2. データストアに GCS データをインポート

作成したデータストアに, GCS 上の PDF ファイルをインポートします.

```bash
gcloud alpha enterprise-search datastores import-documents \
    --location=${GOOGLE_CLOUD_LOCATION} \
    --data-store=${DATA_STORE_ID} \
    --gcs-uri="gs://${BUCKET_NAME}/gcp_tos_jp.pdf"
```

インポートには数分かかる場合があります.

### Step 3-3. RAG Engine (App) の作成

最後に, 作成したデータストアを利用する RAG Engine (App) を作成します.

```bash
export ENGINE_ID="gcp-tos-jp-engine"
gcloud alpha enterprise-search apps create \
    --display-name="GCP Terms of Service Engine (JP)" \
    --location=${GOOGLE_CLOUD_LOCATION} \
    --id=${ENGINE_ID} \
    --data-store-ids=${DATA_STORE_ID}
```

## Step 4. ADK Agent の作成と実行

次に, 作成した Vertex AI Search の RAG Engine を利用する ADK Agent を作成します.

### Step 4-1. Python 環境のセットアップ

まず, Agent を実行するための Python 仮想環境をセットアップします.

```bash
python3 -m venv .venv
source .venv/bin/activate
```

次に, 必要な Python ライブラリをインストールします.

```bash
pip install google-adk google-cloud-aiplatform
```

### Step 4-2. Agent のコード作成

`agents/agent.py` ファイルに以下のコードを記述します. この Agent は, ADK に組み込まれている `VertexAiSearchTool` を利用して, 先ほど作成した RAG Engine に問い合わせを行います.

```python
import os
from adk.adk import ADK
from adk.config import ToolConfig
from adk.tools import VertexAiSearchTool

engine_id = os.environ.get("ENGINE_ID")
if not engine_id:
    raise ValueError("ENGINE_ID environment variable must be set.")

tool_config = ToolConfig(
    [VertexAiSearchTool(engine_id=engine_id)]
)

if __name__ == "__main__":
    ADK(tool_config=tool_config).run()
```

### Step 4-3. Agent の実行

環境変数 `ENGINE_ID` に作成した RAG Engine の ID を設定し, Agent を起動します.

```bash
export ENGINE_ID="gcp-tos-jp-engine"
adk run .
```

## Step 5. Agent との対話

Agent が起動したら, 質問をしてみましょう. Google Cloud の利用規約に関する内容であれば, Agent が回答を生成します.

以下に質問の例を挙げます.

- "Google Cloud の利用規約について教えてください。"
- "料金はどのように発生しますか？"
- "サービスの終了に関する条項を教えてください。"

自由に質問をしてみてください.
