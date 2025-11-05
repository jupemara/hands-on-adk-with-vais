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

## Step 1-2. プロジェクト ID の設定

次に, 使用する Google Cloud プロジェクト ID を設定します.

```bash
gcloud config set project PLEASE_SPECIFY_YOUR_PROJECT_ID
```

`PLEASE_SPECIFY_YOUR_PROJECT_ID` の部分は, ご自身のプロジェクト ID に置き換えてください.
念の為, 正しく設定されているか確認しましょう.

```bash
gcloud config get-value project
```

設定したプロジェクト ID は, 後ほど使用するため環境変数に設定しておきます.

```bash
export GOOGLE_CLOUD_PROJECT=$(gcloud config get-value project)
```

## Step 1-3. 必要な API の有効化

このハンズオンで利用する Google Cloud の API を有効化します.

```bash
gcloud services \
  enable aiplatform.googleapis.com \
  discoveryengine.googleapis.com
```

## Step 2. Vertex AI Search のためのデータ準備

### Step 2-1. Google Cloud Storage Bucket の作成

PDF ファイルを格納するための GCS バケットを作成します.

```bash
export BUCKET_NAME=gs://${GOOGLE_CLOUD_PROJECT}-adk-vais-bucket-$(date +%s%N)
gcloud storage buckets create ${BUCKET_NAME} --location=us-central1
```

### Step 2-3. GCS へのファイルアップロード

作成したバケットに, PDF ファイル ( Google Cloud の利用規約 ) をアップロードします.

```bash
gcloud storage cp ja-google-cloud-terms-of-service.pdf ${BUCKET_NAME}/
```

## Step 3. Vertex AI Search の設定

アップロードした PDF を元に Vertex AI Search のデータストアと検索インデックスを作成します.
( 手順としては [https://cloud.google.com/generative-ai-app-builder/docs/create-data-store-es?hl=ja#cloud-storage](https://cloud.google.com/generative-ai-app-builder/docs/create-data-store-es?hl=ja#cloud-storage) こちらを使います )

### Step 3-1. AI Applications へ移動

[https://console.cloud.google.com/gen-app-builder/?hl=ja](https://console.cloud.google.com/gen-app-builder/?hl=ja) Google Cloud コンソールの "AI Applications" のページに飛びます

### Step 3-2. データストアの作成

1. 画面左側の "データストア" をクリックします
    - [https://console.cloud.google.com/gen-app-builder/data-stores?hl=ja](https://console.cloud.google.com/gen-app-builder/data-stores?hl=ja) こちらのリンクからも飛べます
2. "データストアを作成" をクリックします
3. ソースから Cloud Storage を選択します ( "Cloud Storage のデータをインポート" という画面になります )
    - 特殊データのインポート: `非構造化ドキュメント（PDF、HTML、TXT など）`
    - 同期の頻度: `1 回限り`
    - インポートするフォルダまたはファイルを選択します: "前の手順でアップロードした GCS のファイルへのパスを参照"
    - "続行" をクリック
4. "構成" ページ
    - データストアのロケーション: `global`
    - データストア名: "任意のものをご入力ください"
    - `ドキュメント処理オプション` をクリック
        - ドキュメントチャンキング
            - 高度なチャンク構成を有効にする: `true`
            - チャンクサイズの上限: 500
            - チャンクに上位の見出しを含める: `true`
    - "作成" をクリック
5. 作成したデータストアのページに飛ぶと, インポートの詳細や進捗について確認できます

## Step 4. ADK Agent の作成と実行

ドキュメントのインポート ( インデクシング/チャンク化 ) には少々時間がかかるので, その間にそのデータストアを RAG として問い合わせができる AI Agent 作成を行います

### Step 4-1. Python 環境のセットアップ

PATH を通して `adk` コマンドを叩くために仮想環境を用意します

```bash
python -m venv .venv
```

```bash
source .venv/bin/activate
```

必要な Python ライブラリをインストールします.

```bash
pip install google-adk
```

### Step 4-2. Agent のコード作成

`agents/agent.py` に今回利用する AI Agent のコードがあります.
ざっくり読んでみて雰囲気を感じ取ってみてください...

```bash
cloudshell edit agents/agent.py
```

## Step 4-3. Agent の実行

読んでみたら, 非常にシンプルなことがわかったと思います.
Vertex AI Search で Data Store を作成するとたった 20 行ほどで, 任意のドキュメントを RAG する AI Agent の作成が可能です!!

```python
data_store_id="REPLACE_WITH_YOUR_DATASTORE_ID"
```

の部分を先程作成したご自身の ID と置き換えてください

```bash
adk web --port 8080
```

右上の Web Preview から 8080 番を見に行きましょう!!

## Step 5. Agent との対話

Agent が起動したら, 質問をしてみましょう. Google Cloud の利用規約に関する内容であれば, Agent が回答を生成します.
また, 関係のない質問をするとどうなるでしょうか??
