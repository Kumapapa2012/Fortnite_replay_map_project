# replay_to_map

Fortnite リプレイ JSON ファイルからプレイヤーの移動ルートを読み取り、マップ画像上にプロットするスクリプト。

---

## 必要環境

- Python 3.10+
- Pillow (`pip install Pillow`)

---

## ファイル構成

```
Replay_to_map/
├── replay_to_map.py   # メインスクリプト
├── base_params.json   # マップ画像・座標変換パラメータ
├── user_params.json   # プレイヤー情報
└── README.md
```

---

## 設定ファイル

### base_params.json

マップ画像のパス・サイズと、ワールド座標 → ピクセル座標の変換パラメータを記述します。

```json
{
  "map_image": {
    "path": "../map_ja.png",
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

> **初回セットアップ**: `sample__user_params.json` を `user_params.json` としてコピーし、`player_id` に実際の ID を入力してください。
>
> ```bash
> cp sample__user_params.json user_params.json
> # user_params.json を編集して player_id を設定する
> ```

---

## 使い方

```bash
python replay_to_map.py <FN_REPLAY_FILE> [--base-params <path>] [--user-params <path>]
```

### 引数

| 引数 | 必須 | 説明 |
|---|---|---|
| `FN_REPLAY_FILE` | 必須 | Fortnite リプレイ JSON ファイルのパス |
| `--base-params` | 省略可 | base_params.json のパス（省略時: `./base_params.json`） |
| `--user-params` | 省略可 | user_params.json のパス（省略時: `./user_params.json`） |

### 実行例

```bash
# カレントフォルダの設定ファイルを使う場合
python replay_to_map.py "../replay (4).json"

# 設定ファイルを明示的に指定する場合
python replay_to_map.py "../replay (4).json" --base-params ./base_params.json --user-params ./user_params.json
```

---

## 出力ファイル

実行すると以下の2ファイルが生成されます（カレントフォルダ）。

| ファイル名 | 内容 |
|---|---|
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

> **注意**: 通常、始点はゲーム開始前の待機島（Lobby Island）の座標となるため、マップ画像の範囲外になることが想定されます。
