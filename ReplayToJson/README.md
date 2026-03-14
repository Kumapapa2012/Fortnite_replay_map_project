# ReplayToJson

Fortnite リプレイファイル（`.replay`）を JSON に変換する CLI ツール。
Fortnite がインストールされている環境でないとおそらく動作しません。

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

## 依存アセンブリ

`dotnet build` 実行後、`bin/Release/net9.0/` に以下の DLL が出力されます。
exe と同じフォルダに揃っていないと実行時エラーになります。

| アセンブリ | 用途 |
|---|---|
| `FortniteReplayReader.dll` | Fortnite リプレイファイルのパース |
| `Unreal.Core.dll` | Unreal Engine バイナリ形式の低レベル読み取り |
| `Unreal.Encryption.dll` | Unreal Engine ファイルの暗号化処理 |
| `OozSharp.dll` | Oodle 圧縮形式の展開 |
| `Microsoft.Extensions.DependencyInjection.Abstractions.dll` | DI 抽象化（FortniteReplayReader の依存） |
| `Microsoft.Extensions.Logging.Abstractions.dll` | ログ抽象化（FortniteReplayReader の依存） |

> `System.Text.Json` は .NET 9 ランタイムに組み込まれているため、別途 DLL は不要です。

`dotnet publish` で単一ファイルにまとめた場合、依存 DLL はすべて exe に埋め込まれます。

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
