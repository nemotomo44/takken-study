# 宅建学習ダッシュボード + 毎日Discord通知

## 仕組み

- **GitHub Actions** が毎日 15:00（JST）に自動実行
- `scripts/notify.py` が `data.json` を読んで学習サマリーを生成
- **Discord Webhook** でスマホ・PCに通知が届く（PCがオフでも OK）
- **GitHub Pages** でダッシュボードをどのデバイスからでも閲覧可能

---

## セットアップ手順

### Step 1 — Discord Webhook URL を取得（2分）

1. Discordアプリでサーバーを開く（なければ自分用サーバーを1つ作成）
2. 通知を受け取りたいチャンネルを右クリック → **「チャンネルの編集」**
3. **「連携サービス」** → **「ウェブフック」** → **「新しいウェブフック」**
4. 名前を `宅建学習Bot` などに変更 → **「ウェブフックURLをコピー」**
5. コピーしたURL（`https://discord.com/api/webhooks/...`）をメモ帳に保存

### Step 2 — GitHubリポジトリを作成してプッシュ

1. https://github.com/new でリポジトリを作成
   - Repository name: `takken-study`
   - **Public**（GitHub Pagesを使うため）
2. このフォルダをプッシュ（`YOUR_USERNAME` を自分のGitHubアカウント名に変更）:
   ```powershell
   cd "C:\Users\user\OneDrive\デスクトップ\takken-study"
   git init
   git add .
   git commit -m "initial commit"
   git remote add origin https://github.com/YOUR_USERNAME/takken-study.git
   git push -u origin main
   ```

### Step 3 — GitHub Secrets に Webhook URL を登録

1. リポジトリ → **Settings** → **Secrets and variables** → **Actions**
2. **「New repository secret」** をクリック:

| Name | Value |
|---|---|
| `DISCORD_WEBHOOK_URL` | Step 1 でコピーした Webhook URL |

### Step 4 — GitHub Pages を有効化

1. リポジトリ → **Settings** → **Pages**
2. Source: `Deploy from a branch`、Branch: `main`、Folder: `/ (root)`
3. 保存すると `https://YOUR_USERNAME.github.io/takken-study/` が公開される

### Step 5 — 動作確認（手動テスト）

1. リポジトリ → **Actions** → **宅建学習 毎日LINE通知**
2. **「Run workflow」** → **「Run workflow」** をクリック
3. Discordのチャンネルに通知が届けば完了！

毎日 **15:00（JST）** に自動送信されます。

---

## 学習データの更新方法

新しいDAYを完了したら `data.json` の `days` 配列に追加します：

```json
{"day": 9, "topic": "テーマ名", "date": "2026-05-08", "correct": 7, "total": 9,
 "videos": ["https://lstep.app/xxxxx","https://lstep.app/yyyyy","https://lstep.app/zzzzz"]}
```

追加後に `git add data.json && git commit -m "DAY9追加" && git push` でOK。

---

## ファイル構成

```
takken-study/
├── index.html                   # GitHub Pages ダッシュボード
├── data.json                    # 学習データ（ここを更新）
├── scripts/
│   └── notify.py               # Discord通知スクリプト
└── .github/workflows/
    └── daily-notify.yml        # GitHub Actions（毎日15:00 JST）
```
