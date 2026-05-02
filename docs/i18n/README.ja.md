# 🔮 Skill Aggregator

<p align="center">
  <img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License">
  <img src="https://img.shields.io/badge/python-3.10%2B-blue" alt="Python">
  <br>
  <b>🧠 あなたのAIアシスタントは400以上のスキルを持っていますが、あなたが知っているのは10個だけ。<br>Skill Aggregatorが使うべきスキルを見つけ出します。</b>
</p>

[English](../README.md) · [中文](../README_CN.md) · **日本語** · [한국어](README.ko.md) · [Français](README.fr.md) · [Español](README.es.md) · [Русский](README.ru.md) · [العربية](README.ar.md)

---

## ⚡ クイックスタート

```bash
pip install skill-aggregator
skill-aggregator "Reactでログインフォームのバリデーションを書く"
```

## ✨ 主な機能

| 機能 | 説明 |
|------|------|
| 🧠 **意図理解** | キーワードだけでなく、本当の意図を分析 |
| 🈯 **日中英対応** | jieba中国語分詞 + 英語正規表現 |
| 🔄 **環境認識** | `config.yaml` から全スキルディレクトリを自動発見 |
| 🎯 **4軸スコアリング** | キーワード(40%) + ドメイン(25%) + TF-IDF(20%) + 優先度(15%) |
| 🧹 **スキル健全性チェック** | 400以上のスキルをスキャンして問題を検出 |

## 🆚 比較

| | 知的マッチング | 中国語分詞 | 環境認識 | スキルチェック |
|------|:--:|:--:|:--:|:--:|
| **Skill Aggregator** | ✅ | ✅ | ✅ | ✅ |
| 手動フォルダ検索 | ❌ | ❌ | ❌ | ❌ |
| AIに直接質問 | ⚠️ | ⚠️ | ❌ | ❌ |

---

MIT © 2026 [Vinger](https://github.com/Vinger-lee)
