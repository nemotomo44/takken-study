"""
宅建学習 毎日 15:00 Discord通知スクリプト
GitHub Actions の daily-notify.yml から実行される
環境変数:
  DISCORD_WEBHOOK_URL ... Discord チャンネルの Webhook URL
"""
import json
import os
import urllib.request
from datetime import date

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data.json")
DASHBOARD_URL = os.environ.get("DASHBOARD_URL", "https://YOUR_GITHUB_USERNAME.github.io/takken-study/")

def load_data():
    with open(DATA_PATH, encoding="utf-8") as f:
        return json.load(f)

def score_emoji(correct, total):
    rate = correct / total * 100
    if rate >= 89:
        return "🟢"
    elif rate >= 67:
        return "🟡"
    else:
        return "🔴"

def build_embed(data):
    days = data["days"]
    cats = data["course"]["categories"]
    total_days = 90
    done = len(days)
    today = date.today().strftime("%m/%d")

    total_correct = sum(d["correct"] for d in days)
    total_q = sum(d["total"] for d in days)
    overall_rate = round(total_correct / total_q * 100, 1) if total_q else 0

    # カテゴリー別進捗フィールド
    fields = []
    for cat in cats:
        lo, hi = cat["range"]
        cat_days = [d for d in days if lo <= d["day"] <= hi]
        total_in_cat = hi - lo + 1
        done_in_cat = len(cat_days)
        prog_pct = round(done_in_cat / total_in_cat * 100)
        bar = "█" * (prog_pct // 10) + "░" * (10 - prog_pct // 10)
        fields.append({
            "name": f'{cat["icon"]} {cat["name"]}',
            "value": f"`{bar}` {done_in_cat}/{total_in_cat}日 ({prog_pct}%)",
            "inline": True
        })

    # 最新DAY情報
    if days:
        latest = days[-1]
        rate = round(latest["correct"] / latest["total"] * 100, 1)
        emoji = score_emoji(latest["correct"], latest["total"])
        video_link = latest["videos"][0] if latest.get("videos") else ""
        latest_value = (
            f'{emoji} {latest["correct"]}/{latest["total"]}問正解 ({rate}%)\n'
            + (f'[▶ 解説動画を見る]({video_link})' if video_link else '')
        )
        fields.append({
            "name": f'📖 最新 DAY{latest["day"]} {latest["topic"]}',
            "value": latest_value,
            "inline": False
        })

    # 苦手DAY
    weak_days = [d for d in days if d["correct"] / d["total"] < 0.67]
    if weak_days:
        weak_text = "、".join(f'DAY{d["day"]}({d["topic"]})' for d in weak_days[:3])
        if len(weak_days) > 3:
            weak_text += f" 他{len(weak_days)-3}件"
        fields.append({"name": "⚠️ 苦手DAY（正答率66%以下）", "value": weak_text, "inline": False})
    else:
        fields.append({"name": "✅ 苦手問題", "value": "現時点でなし", "inline": False})

    embed = {
        "title": f"📚 宅建学習リマインダー（{today} 15:00）",
        "description": (
            f"**全体進捗: {done}/{total_days}日完了**　|　正答率 **{overall_rate}%**\n"
            f"[📊 ダッシュボードを開く]({DASHBOARD_URL})"
        ),
        "color": 0x40c4ff,
        "fields": fields,
        "footer": {"text": "こざりえ宅建勉強合格講座 LINE学習アプリ 全90日コース"}
    }
    return embed

def send_discord(embed, webhook_url):
    webhook_url = webhook_url.strip().replace("discordapp.com", "discord.com")
    print(f"Webhook URL (masked): {webhook_url[:50]}...")
    payload = json.dumps({"embeds": [embed]}).encode("utf-8")
    req = urllib.request.Request(
        webhook_url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req) as res:
            print(f"Discord response: {res.status}")
            return res.status in (200, 204)
    except urllib.error.HTTPError as e:
        print(f"HTTP Error: {e.code} {e.reason}")
        print(f"Response body: {e.read().decode('utf-8')}")
        raise

def main():
    webhook_url = os.environ.get("DISCORD_WEBHOOK_URL")
    if not webhook_url:
        print("ERROR: DISCORD_WEBHOOK_URL が未設定です。")
        raise SystemExit(1)

    data = load_data()
    embed = build_embed(data)
    print("Sending to Discord...")
    ok = send_discord(embed, webhook_url)
    if not ok:
        raise SystemExit(1)
    print("Sent successfully.")

if __name__ == "__main__":
    main()
