import argparse
import json
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw

_DEFAULT_EXE = Path(__file__).parent / "ReplayToJson/bin/Release/net9.0/ReplayToJson.exe"


def load_json(path: Path) -> dict:
    with open(path, encoding="utf-8-sig") as f:
        return json.load(f)


def parse_args():
    parser = argparse.ArgumentParser(description="Plot Fortnite replay route on map image.")
    parser.add_argument(
        "FN_REPLAY_FILE", type=Path,
        help="Path to Fortnite replay file (.replay or .json)."
    )
    parser.add_argument(
        "--base-params", dest="FN_REPLAY_PARAMS", type=Path,
        default=Path("base_params.json"),
        help="Path to base_params.json (default: ./base_params.json)"
    )
    parser.add_argument(
        "--user-params", dest="FN_USER_PARAMS", type=Path,
        default=Path("user_params.json"),
        help="Path to user_params.json (default: ./user_params.json)"
    )
    parser.add_argument(
        "--exe", dest="EXE_PATH", type=Path,
        default=_DEFAULT_EXE,
        help=f"Path to ReplayToJson.exe (default: {_DEFAULT_EXE})"
    )
    return parser.parse_args()


def run_replay_to_json(replay_path: Path, exe_path: Path) -> Path:
    """Call ReplayToJson.exe to convert .replay binary to JSON. Returns output JSON path."""
    if not exe_path.exists():
        print(f"Error: ReplayToJson.exe not found: {exe_path}", file=sys.stderr)
        sys.exit(1)

    result = subprocess.run(
        [str(exe_path), str(replay_path)],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        print(f"Error: ReplayToJson failed:\n{result.stderr}", file=sys.stderr)
        sys.exit(1)

    return Path(result.stdout.strip())


def main():
    args = parse_args()

    replay_file: Path = args.FN_REPLAY_FILE
    base_params_file: Path = args.FN_REPLAY_PARAMS
    user_params_file: Path = args.FN_USER_PARAMS

    if replay_file.suffix.lower() == ".replay":
        print(f"Converting {replay_file.name} to JSON ...")
        replay_json_file = run_replay_to_json(replay_file, args.EXE_PATH)
        print(f"Converted  -> {replay_json_file}")
    else:
        replay_json_file = replay_file

    replay = load_json(replay_json_file)
    base_params = load_json(base_params_file)
    user_params = load_json(user_params_file)

    # --- Step 1: Build location array ---
    location_entries = build_location_entries(replay, base_params, user_params)

    output_path = replay_json_file.stem + "_locations.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(location_entries, f, ensure_ascii=False, indent=2)
    print(f"Saved {len(location_entries)} entries -> {output_path}")

    # --- Step 2: Draw route on map ---
    img = draw_route(location_entries, base_params)
    image_output_path = replay_json_file.stem + "_map.png"
    img.save(image_output_path)
    print(f"Saved map image -> {image_output_path}")


def build_location_entries(replay: dict, base_params: dict, user_params: dict) -> list:
    """Extract player locations from replay and convert to map coordinates."""
    player_id = user_params["player_id"]
    scale_x = base_params["world_to_pixel"]["scale_x"]
    scale_y = base_params["world_to_pixel"]["scale_y"]
    origin_x = base_params["world_to_pixel"]["world_origin_on_map"]["x"]
    origin_y = base_params["world_to_pixel"]["world_origin_on_map"]["y"]

    player = next(
        (p for p in replay["PlayerData"] if p.get("PlayerId") == player_id),
        None
    )
    if player is None:
        raise ValueError(f"Player '{player_id}' not found in replay.")

    location_entries = []
    for loc in player["Locations"]:
        rm = loc.get("ReplicatedMovement")
        if not rm or not rm.get("Location"):
            continue
        wx = rm["Location"]["X"]
        wy = rm["Location"]["Y"]
        wz = rm["Location"]["Z"]
        location_entries.append({
            "ReplicatedWorldTimeSecondsDouble": loc.get("ReplicatedWorldTimeSecondsDouble"),
            "world": {"X": wx, "Y": wy, "Z": wz},
            "map": {
                "X": scale_x * wx + origin_x,
                "Y": scale_y * wy + origin_y,
            }
        })

    return location_entries


def z_to_color(z: float, z_min: float, z_mean: float, z_max: float) -> tuple:
    """Map Z value to RGB color: blue (min) -> green (mean) -> red (max)."""
    if z <= z_mean:
        t = (z - z_min) / (z_mean - z_min) if z_mean != z_min else 0.0
        t = max(0.0, min(1.0, t))
        r = int(0   * (1 - t) + 0   * t)
        g = int(0   * (1 - t) + 255 * t)
        b = int(255 * (1 - t) + 0   * t)
    else:
        t = (z - z_mean) / (z_max - z_mean) if z_max != z_mean else 0.0
        t = max(0.0, min(1.0, t))
        r = int(0   * (1 - t) + 255 * t)
        g = int(255 * (1 - t) + 0   * t)
        b = int(0   * (1 - t) + 0   * t)
    return (r, g, b)


def draw_route(location_entries: list, base_params: dict) -> Image.Image:
    """Draw player route on map image with Z-based color gradient."""
    map_cfg = base_params["map_image"]
    map_path = Path(map_cfg["path"])
    expected_w = map_cfg["width"]
    expected_h = map_cfg["height"]

    img = Image.open(map_path).copy()
    if img.size != (expected_w, expected_h):
        print(
            f"Error: image size {img.size} does not match expected "
            f"({expected_w}, {expected_h}).",
            file=sys.stderr
        )
        sys.exit(1)

    z_values = [e["world"]["Z"] for e in location_entries]
    z_min  = min(z_values)
    z_max  = max(z_values)
    z_mean = sum(z_values) / len(z_values)
    print(f"Z stats: min={z_min:.1f}, mean={z_mean:.1f}, max={z_max:.1f}")

    draw = ImageDraw.Draw(img)
    dot_r      = 1   # normal dot radius  (~2px diameter)
    dot_r_end  = 5   # first/last dot radius (~10px diameter)
    line_width = 1

    points = [(e["map"]["X"], e["map"]["Y"]) for e in location_entries]
    colors = [z_to_color(e["world"]["Z"], z_min, z_mean, z_max) for e in location_entries]

    # Lines
    for i in range(1, len(points)):
        draw.line([points[i - 1], points[i]], fill=colors[i], width=line_width)

    # Dots
    for i, (px, py) in enumerate(points):
        r = dot_r_end if i == 0 or i == len(points) - 1 else dot_r
        draw.ellipse([(px - r, py - r), (px + r, py + r)], fill=colors[i])

    return img


if __name__ == "__main__":
    main()
