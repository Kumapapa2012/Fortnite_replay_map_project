# replay_to_map

Fortnite リプレイファイル（`.replay`）からプレイヤーの移動ルートを読み取り、マップ画像上にプロットするスクリプト。

マップ画像のファイルは、[Fortnite API で取得している](https://dash.fortnite-api.com/endpoints/map)ことを想定しています。
画像サイズは既定で 2048ｘ2048。

通常バトロワのソロのリプレイファイルのみでテストを行っていますが、他のモードについても使用可能と思われます。

ただプレイヤーの位置だけをプロットするだけです。バトルバスの航路、キルイベントなどの付加情報は今のところありません。

---

## 必要環境

- Python 3.10+
- Pillow (`pip install Pillow`)
- .NET 9 SDK（`ReplayToJson` のビルドに必要）

---

## サンプル画像

（クリックして実物大）

### 出撃がバトルバスの場合

<img width="768" height="768" alt="Image" src="https://github.com/user-attachments/assets/c8db917d-aff9-4a51-83c8-3aae82f3ed35" />

### 出撃がサーフィンの場合

<img width="768" height="768" alt="Image" src="https://github.com/user-attachments/assets/b617a3d6-2841-4138-baf7-ed7a075da3b8" />

---

## ファイル構成

```
Fortnite_replay_map_project/
├── replay_to_map.py        # メインスクリプト
├── base_params.json        # マップ画像・座標変換パラメータ
├── user_params.json        # プレイヤー情報
├── sample__user_params.json
├── README.md
└── ReplayToJson/           # .replay → JSON 変換ツール（C#）
    ├── ReplayToJson.csproj
    ├── Program.cs
    └── README.md
```

---

## セットアップ

### 1. ReplayToJson をビルドする

```bash
cd ReplayToJson
dotnet build -c Release
cd ..
```

### 2. user_params.json を作成する

```bash
cp sample__user_params.json user_params.json
# user_params.json を編集して player_id を設定する
```

### 3. base_params.json

取得したマップ画像のファイルに応じて編集してください。
少なくとも、"path" はダウンロードしたマップ画像のファイルパスに変更する必要があります。

---

## 設定ファイル

### base_params.json

マップ画像のパス・サイズと、ワールド座標 → ピクセル座標の変換パラメータを記述します。

```json
{
  "map_image": {
    "path": "../PATH_TO_MAP_IMAGE.png",
    "width": 2048,
    "height": 2048
  },
  "world_to_pixel": {
    "scale_x": 0.00682888,
    "scale_y": 0.00673428,
    "world_origin_on_map": {
      "x": 964,
      "y": 1014
    }
  }
}
```

変換式:
```
pixel_x = scale_x * world_x + world_origin_on_map.x
pixel_y = scale_y * world_y + world_origin_on_map.y
```

### user_params.json

対象プレイヤーの ID を記述します。

```json
{
  "player_id": "YOUR_player_id or epic_id"
}
```

---

## 使い方

```bash
python replay_to_map.py <FN_REPLAY_FILE> [--base-params <path>] [--user-params <path>] [--exe <path>]
```

### 引数

| 引数 | 必須 | 説明 |
|---|---|---|
| `FN_REPLAY_FILE` | 必須 | Fortnite リプレイファイルのパス（`.replay` または `.json`） |
| `--base-params` | 省略可 | base_params.json のパス（省略時: `./base_params.json`） |
| `--user-params` | 省略可 | user_params.json のパス（省略時: `./user_params.json`） |
| `--exe` | 省略可 | ReplayToJson.exe のパス（省略時: `./ReplayToJson/bin/Release/net9.0/ReplayToJson.exe`） |

### 実行例

```bash
# .replay ファイルを直接指定（推奨）
python replay_to_map.py "C:\Users\<user>\AppData\Local\FortniteGame\Saved\Demos\UnsavedReplay-xxxx.replay"

# 既に変換済みの JSON を指定
python replay_to_map.py "replay.json"

# 設定ファイルを明示的に指定する場合
python replay_to_map.py "UnsavedReplay.replay" --base-params ./base_params.json --user-params ./user_params.json
```

> **Fortnite リプレイの既定の格納場所**:
> `%LocalAppData%\FortniteGame\Saved\Demos`

---

## 出力ファイル

実行すると以下の3ファイルが生成されます（カレントフォルダ）。

| ファイル名 | 内容 |
|---|---|
| `{リプレイ名}.json` | リプレイ全データの JSON（C# による変換結果） |
| `{リプレイ名}_locations.json` | 各フレームの時刻・ワールド座標・ピクセル座標の配列 |
| `{リプレイ名}_map.png` | ルートを描画したマップ画像 |

### locations.json の構造

```json
[
  {
    "ReplicatedWorldTimeSecondsDouble": 100.366,
    "world": { "X": -67429.25, "Y": -37382.63, "Z": 79850.0 },
    "map":   { "X": 503.5, "Y": 762.3 }
  },
  ...
]
```

---

## 描画ルール

- **色**: Z 値（高度）に応じてグラデーション
  - 青 = Z 最小値（地上付近）
  - 緑 = Z 平均値
  - 赤 = Z 最大値（スカイダイブ中など）
- **点**: 通常 2px、始点・終点のみ 10px
- **線**: 前後の点を 1px の線で接続

> **注意**: 始点はマップ画像の範囲外になり、表示されないことがあります。
