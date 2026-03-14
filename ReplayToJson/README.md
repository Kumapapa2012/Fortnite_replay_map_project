# ReplayToJson

Fortnite リプレイファイル（`.replay`）を JSON に変換する CLI ツール。

---

## ビルド

.NET 9 SDK が必要です。

```bash
cd ReplayToJson
dotnet build -c Release
```

実行ファイルの出力先: `bin/Release/net9.0/ReplayToJson.exe`

単一ファイルにまとめる場合:

```bash
dotnet publish -c Release -r win-x64 --self-contained false /p:PublishSingleFile=true
```

出力先: `bin/Release/net9.0/win-x64/publish/ReplayToJson.exe`

---

## Usage

```
ReplayToJson <INPUT_REPLAY_FILE> [OUTPUT_JSON_FILE]
```

| 引数 | 必須 | 説明 |
|---|---|---|
| `INPUT_REPLAY_FILE` | 必須 | `.replay` ファイルのパス |
| `OUTPUT_JSON_FILE` | 省略可 | 出力 JSON パス（省略時: カレントフォルダに `{入力ファイル名}.json`） |

### 実行例

```bash
# 出力先を省略（カレントフォルダに replay.json を生成）
ReplayToJson "C:\path\to\replay.replay"

# 出力先を明示指定
ReplayToJson "C:\path\to\replay.replay" "C:\path\to\output.json"
```

### 終了コード

| コード | 意味 |
|---|---|
| `0` | 成功（標準出力に出力ファイルパスを表示） |
| `1` | エラー（標準エラー出力にメッセージを表示） |

---

## .gitignore への追加

`bin/` と `obj/` はリポジトリに含めないようにしてください。

```
ReplayToJson/bin/
ReplayToJson/obj/
```
