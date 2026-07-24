# MyNewsPaper

Python + GitHub Actions で毎朝 06:00 JST に Discord へ投稿するパーソナル朝刊システムです。

## 構成

- `src/collectors/`: 天気、投資信託、株式、指数、公開 Google カレンダー、ヘルスチェック、音声日記、RSS
- `src/services/discord.py`: Discord Webhook 投稿
- `src/services/google_drive.py`: Google Drive 読み取り
- `src/services/openai_client.py`: 文字起こしと要約
- `src/formatters/morning_report.py`: Discord 向け整形
- `src/formatters/public_page.py`: GitHub Pages / Echo 読み上げ向け整形
- `src/storage/json_store.py`: JSON 状態保存
- `data/funds_high_watermark.json`: 投資信託の過去最高基準価額
- `doc/`: GitHub Pages で公開するEcho読み上げ向けページ、RSS、テキスト
- `.github/workflows/morning-report.yml`: JST 06:00 実行、公開ページ生成、状態ファイル自動コミット、Pagesデプロイ

## GitHub Secrets

- `DISCORD_WEBHOOK_URL`: Discord Webhook URL
- `OPENAI_API_KEY`: RSS 要約、音声日記文字起こし/分析で使用
- `GOOGLE_SERVICE_ACCOUNT_JSON`: Google Drive API 用サービスアカウント JSON 全体
- `WEATHER_LATITUDE`: 天気予報取得用の緯度
- `WEATHER_LONGITUDE`: 天気予報取得用の経度

## 設定

`config/*.json` を自分用に編集します。

- `weather.json`: Open-Meteo 用のタイムゾーン設定。緯度経度はGitHub Secretsで管理します。
- `funds.json`: 投資信託ごとの Web ページ URL と基準価額を含む span の class
- `stocks.json`: yfinance の株式ティッカー
- `indexes.json`: yfinance の指数ティッカー
- `google_calendar.json`: 公開 Google カレンダーの iCal URL
- `audio_diary.json`: Google Drive の音声日記フォルダ ID
- `rss.json`: RSS フィード一覧

投資信託は、各ページの `<span class="h3 font-weight-bold">` に表示されている基準価額を取得します。
過去最高基準価額は `data/funds_high_watermark.json` に保存され、GitHub Actions 実行後に自動コミットされます。

GitHub Pages はワークフローで `doc/` をデプロイします。リポジトリ設定の Pages source は GitHub Actions にしてください。

## ローカル実行

```powershell
pip install -r requirements.txt
python -m src.main --dry-run
```
