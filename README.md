AI Gmail Sorter (with GitHub Actions & Discord)
Gmailの未読メールをAI（Gemini）が自動で「対応要」「対応不要」に仕分けし、さらにプロモーションメールは自動既読化して、それぞれ指定したDiscordのチャンネルへ通知するシステムです。
GitHub Actionsを利用するため、サーバー不要・完全無料で24時間自動運用が可能です。

🛠 特徴スマートな仕分け: gemini-2.5-flash を使用し、メルマガや自動配信メールは「対応不要」、人間からの個別連絡は「対応要」に自動分類。ノイズの削減: 広告やメルマガ（プロモーションカテゴリ）はAIのトークンを消費せず、自動既読化して専用チャンネルへポイ活。
完全無料＆サーバーレス: ご自身のPCをつけっぱなしにする必要はありません。GitHubの環境のみで完結します。

📋 前提条件導入には以下の準備が必要です。
GitHub アカウントGoogle アカウント（自動化したいGmailアドレス）
Discord サーバー（通知を受け取る場所）

🚀 導入手順
Step 1. Discord Webhookの取得通知を飛ばしたい3つのチャンネル（対応要、対応不要、プロモーション）を用意し、それぞれのWebhook URLを取得します。チャンネルの編集（歯車マーク）＞ 連携サービス ＞ ウェブフックを作成 をクリック。URLをコピーして控えておきます。
Step 2. Google Cloud設定（Gmail APIの有効化）プログラムがGmailにアクセスするための認証情報を取得します。Google Cloud Console にアクセスし、新しいプロジェクトを作成。「Gmail API」を検索し、有効化 します。OAuth 同意画面 を設定します。User Typeは「外部」を選択。アプリ名やメールアドレスを入力。「テストユーザー」に自分のGmailアドレスを追加。認証情報 画面に移動し、「認証情報を作成」＞「OAuth クライアント ID」を選択。アプリケーションの種類は「デスクトップ アプリ」を選択。作成後、JSONファイルをダウンロードし、名前を credentials.json に変更します。
Step 3. 初回認証（token.json の作成）セキュアに自動ログインするための鍵（token.json）をご自身の手元で1度だけ生成します。本リポジトリの auth_gmail.py と、先ほどの credentials.json を同じフォルダに置きます。以下のコマンドでライブラリをインストールし、スクリプトを実行します。Bashpip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
python auth_gmail.py
ブラウザが立ち上がるので、対象のGoogleアカウントでログインし、権限を許可します。フォルダ内に token.json が生成されます。
（※このファイルは絶対にGitHubに公開しないでください）

Step 4. Google AI Studio（Gemini APIキーの取得）メールの仕分けを行うAIの鍵を取得します。Google AI Studio にアクセス。Get API key ＞ Create API key からAPIキーを発行し、コピーして控えておきます。
Step 5. GitHub Secrets（金庫）の設定リポジトリを「Private（非公開）」で作成し、取得した秘密の情報を登録します。GitHubリポジトリの Settings ＞ Secrets and variables ＞ Actions を開きます。New repository secret をクリックし、以下の5つの変数を登録します。変数名設定する内容GEMINI_API_KEYGeminiのAPIキーWEBHOOK_REQUIRED対応要チャンネルのDiscord Webhook URLWEBHOOK_UNNECESSARY対応不要チャンネルのDiscord Webhook URLWEBHOOK_PROMOTIONSプロモーションチャンネルのDiscord Webhook URLGMAIL_TOKEN_JSON手元の token.json の中身（テキスト）を丸ごとコピー＆ペースト
🏃‍♂️ 稼働テストリポジトリの Actions タブを開きます。左メニューから Gmail Auto Sorter ワークフローを選択。Run workflow ボタンを押すと、手動で即時実行テストが可能です。成功すると、指定した間隔（デフォルトは15分おき）でGitHub Actionsが裏で自動起動し、メールを捌き続けます。

📄 免責事項 / ライセンス本ツールは個人利用を想定しています。Gemini APIの無料枠を使用する場合、送信されたデータがモデルの学習に利用される可能性があります。機密情報や極めて重要な個人情報を含むメールへの適用は自己責任でお願いいたします
