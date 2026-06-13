import os
import json
import requests
import google.generativeai as genai
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# --- 各種設定（GitHubのSecretsから取得） ---
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']
WEBHOOK_REQUIRED = os.environ.get('WEBHOOK_REQUIRED')
WEBHOOK_UNNECESSARY = os.environ.get('WEBHOOK_UNNECESSARY')
WEBHOOK_PROMOTIONS = os.environ.get('WEBHOOK_PROMOTIONS')
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')

genai.configure(api_key=GEMINI_API_KEY)

def send_discord_notification(webhook_url, message):
    if not webhook_url: return
    data = {"content": message}
    try:
        requests.post(webhook_url, json=data)
    except Exception as e:
        print(f"Discord通知エラー: {e}")

def classify_email_with_ai(subject, body):
    model = genai.GenerativeModel('gemini-2.5-flash')
    prompt = f"""
    あなたは優秀なメール管理アシスタントです。ユーザーの受信トレイを整理するために、
    メールを「対応不要」または「返信したほうがいい」のどちらかに厳格に分類してください。

    【判断の基準】
    ■「返信したほうがいい」に分類するもの：
    - 人間から直接届いた、個別の連絡や質問
    - スケジュール調整、面談、ミーティングの誘い
    - 返信や何らかのアクションを明確に求められているもの

    ■「対応不要」に分類するもの：
    - システムからの自動配信メール（ログイン通知、決済完了、発送連絡など）
    - 各種サービスのセキュリティアラートやアップデート通知
    - 相手への返信が物理的に不可能な「送信専用アドレス」からのメール
    - 定期的なレポート、ニュース、技術系のメルマガ（メインに入ってしまったもの）

    【具体的な分類例】
    例1：
    件名: お打ち合わせの候補日について
    本文: お疲れ様です。来週のどこかでお時間をいただくことは可能でしょうか？候補日を…
    出力: 返信したほうがいい

    例2：
    件名: [GitHub] Security alert: temporary write access granted
    本文: We detected a security event on your repository...
    出力: 対応不要

    例3：
    件名: 【重要】ご利用料金確定のお知らせ
    本文: いつもご利用ありがとうございます。○月度のご利用料金が確定しました。詳細はマイページ…
    出力: 対応不要

    ーーー
    上記のルールと例を参考に、以下のメールを「対応不要」または「返信したほうがいい」のどちらかのみで出力してください。解説は不要です。

    件名: {subject}
    本文: {body[:500]}
    出力:
    """
    try:
        response = model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(temperature=0.1)
        )
        return response.text.strip()
    except Exception as e:
        print(f"AIエラー: {e}")
        return "判定不能"

def main():
    token_json_str = os.environ.get('GMAIL_TOKEN_JSON')
    if not token_json_str:
        print("エラー: GMAIL_TOKEN_JSONが設定されていません。")
        return

    token_info = json.loads(token_json_str)
    creds = Credentials.from_authorized_user_info(token_info, SCOPES)
    service = build('gmail', 'v1', credentials=creds)

    # ==========================================
    # 1. プロモーションメールの自動既読化 ＆ 通知処理
    # ==========================================
    promo_results = service.users().messages().list(userId='me', q="is:unread category:promotions").execute()
    promo_messages = promo_results.get('messages', [])
    
    if promo_messages:
        print(f"プロモーションメールを {len(promo_messages)} 件検出。処理を開始します。")
        for message in promo_messages:
            msg_id = message['id']
            msg = service.users().messages().get(userId='me', id=msg_id, format='full').execute()
            headers = msg['payload']['headers']
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), "件名なし")

            service.users().messages().modify(
                userId='me', id=msg_id, body={'removeLabelIds': ['UNREAD']}
            ).execute()
            
            send_discord_notification(WEBHOOK_PROMOTIONS, f"📦 【プロモーション/自動既読化】\n件名: {subject}")

    # ==========================================
    # 2. メイン（Primary）メールのAI判定・通知処理
    # ==========================================
    primary_results = service.users().messages().list(userId='me', q="is:unread category:primary").execute()
    messages = primary_results.get('messages', [])

    if not messages:
        print("メイン受信トレイに新しい未読メールはありません。")
        return

    for message in messages:
        msg_id = message['id']
        msg = service.users().messages().get(userId='me', id=msg_id, format='full').execute()
        
        headers = msg['payload']['headers']
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), "件名なし")
        body = msg['snippet'] 

        print(f"メインメール処理中: {subject}")
        classification = classify_email_with_ai(subject, body)

        if "対応不要" in classification:
            service.users().messages().modify(
                userId='me', id=msg_id, body={'removeLabelIds': ['UNREAD']}
            ).execute()
            send_discord_notification(WEBHOOK_UNNECESSARY, f"🟢 【対応不要/既読化】\n件名: {subject}")
        else:
            send_discord_notification(WEBHOOK_REQUIRED, f"🔴 【要確認/未読保持】\n件名: {subject}")

if __name__ == '__main__':
    main()
