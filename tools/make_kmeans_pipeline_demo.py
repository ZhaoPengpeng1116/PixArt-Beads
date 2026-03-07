import os
import argparse
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from sklearn.cluster import KMeans
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import functions as fun


def nearest_labels(points: np.ndarray, centers: np.ndarray) -> np.ndarray:
    d = points[:, None, :] - centers[None, :, :]
    dist2 = np.sum(d * d, axis=2)
    return np.argmin(dist2, axis=1)


def quantize_with_centers(img_arr: np.ndarray, centers: np.ndarray) -> np.ndarray:
    flat = img_arr.reshape(-1, 3).astype(np.float32)
    labels = nearest_labels(flat, centers.astype(np.float32))
    q = centers[labels].reshape(img_arr.shape)
    return np.clip(q, 0, 255).astype(np.uint8)


def build_frame(
    image: Image.Image,
    subtitle: str,
    panel_h: int = 400,
) -> Image.Image:
    """Build a frame showing just the image with subtitle."""
    font = ImageFont.load_default()

    # Scale image to fixed height
    w, h = image.size
    new_w = int(w * panel_h / h)
    scaled = image.resize((new_w, panel_h), Image.NEAREST)

    margin = 15
    text_h = 30
    
    width = margin * 2 + scaled.width
    height = margin * 2 + text_h + panel_h
    canvas = Image.new("RGB", (width, height), (250, 250, 250))
    draw = ImageDraw.Draw(canvas)

    # Subtitle
    draw.text((margin, margin), subtitle, fill=(50, 50, 50), font=font)

    y_img = margin + text_h
    canvas.paste(scaled, (margin, y_img))
    
    return canvas


def main():
    parser = argparse.ArgumentParser(description="Generate full pipeline demo: K-means -> Downscale -> Upscale -> Grid")
    parser.add_argument("--input", required=True, help="Input image path")
    parser.add_argument("--output-dir", required=True, help="Output directory")
    parser.add_argument("--k", type=int, default=8, help="Number of clusters")
    parser.add_argument("--downscale", type=int, default=48, help="Downscale width")
    parser.add_argument("--upscale", type=int, default=10, help="Upscale multiplier")
    parser.add_argument("--iters", type=int, default=30, help="Max iteration frames")
    parser.add_argument("--sample", type=int, default=2000, help="Sample pixel count for fitting")
    parser.add_argument("--fps", type=int, default=1, help="GIF frames per second")
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    img = Image.open(args.input).convert("RGB")
    arr = np.array(img)
    flat = arr.reshape(-1, 3).astype(np.float32)

    rng = np.random.default_rng(42)
    n = flat.shape[0]
    sample_size = min(args.sample, n)
    idx = rng.choice(n, sample_size, replace=False)
    sample = flat[idx]

    # Initialize centers
    init_idx = rng.choice(sample.shape[0], args.k, replace=False)
    centers = sample[init_idx].copy()

    frames = []
    frames_png_dir = os.path.join(args.output_dir, "frames")
    os.makedirs(frames_png_dir, exist_ok=True)

    # Frame 0: Original image with clusters initialized
    initial_labels = nearest_labels(flat, centers.astype(np.float32))
    q_arr = quantize_with_centers(arr, centers)
    q_img = Image.fromarray(q_arr, mode="RGB")
    
    subtitle = "Step 1: Iteration 0 - Random cluster initialization"
    fr = build_frame(q_img, subtitle)
    frames.append(fr)
    fr.save(os.path.join(frames_png_dir, "frame_00_iter0.png"))

    # K-means iterations
    prev_centers = None
    conv_iter = 0
    for i in range(1, args.iters + 1):
        km = KMeans(
            n_clusters=args.k,
            init=centers,
            n_init=1,
            max_iter=1,
            random_state=42,
            algorithm="lloyd",
        )
        km.fit(sample)
        centers = km.cluster_centers_.astype(np.float32)

        q_arr = quantize_with_centers(arr, centers)
        q_img = Image.fromarray(q_arr, mode="RGB")

        shift = 0.0 if prev_centers is None else float(np.linalg.norm(centers - prev_centers))
        subtitle = f"Step 1: Iteration {i} - K-means clustering (Shift={shift:.4f})"
        
        fr = build_frame(q_img, subtitle)
        frames.append(fr)
        fr.save(os.path.join(frames_png_dir, f"frame_{i:02d}_iter{i}.png"))

        if prev_centers is not None and shift < 1e-2:
            conv_iter = i
            print(f"K-means converged at iteration {i}")
            break
        prev_centers = centers.copy()

    # Use converged centers for pipeline
    conv_centers = centers.copy()

    # Downscale step
    print("Downscaling...")
    dsize = fun.downscaleSize(img, args.downscale)
    img_qnt = img.resize(dsize, Image.LANCZOS)
    q_arr = quantize_with_centers(np.array(img_qnt), conv_centers)
    img_dwn = Image.fromarray(q_arr)
    
    subtitle = f"Step 2: Downscaling to {dsize[0]}×{dsize[1]} pixels"
    fr = build_frame(img_dwn, subtitle)
    frames.append(fr)
    fr.save(os.path.join(frames_png_dir, "frame_downscale.png"))

    # Upscale step
    print("Upscaling...")
    upscale_size = [args.upscale * i for i in dsize]
    img_ups = img_dwn.resize(upscale_size, Image.NEAREST)
    
    subtitle = f"Step 3: Upscaling by {args.upscale}× to {img_ups.size[0]}×{img_ups.size[1]} pixels"
    fr = build_frame(img_ups, subtitle)
    frames.append(fr)
    fr.save(os.path.join(frames_png_dir, "frame_upscale.png"))

    # Grid overlay step
    print("Adding grid overlay...")
    img_ups_cv = np.array(img_ups)
    img_grd_cv = fun.gridOverlay(img_ups_cv, args.upscale, gridColor=(0, 0, 0))
    img_grd = Image.fromarray(img_grd_cv)
    
    subtitle = f"Step 4: Grid overlay with {args.upscale}px spacing"
    fr = build_frame(img_grd, subtitle)
    frames.append(fr)
    fr.save(os.path.join(frames_png_dir, "frame_grid.png"))

    # Hold final frame longer
    for _ in range(4):
        frames.append(frames[-1].copy())

    # Save GIF
    print("Saving GIF...")
    gif_path = os.path.join(args.output_dir, "kmeans_pipeline_demo.gif")
    duration_ms = int(1000 / max(1, args.fps))
    frames[0].save(
        gif_path,
        save_all=True,
        append_images=frames[1:],
        optimize=False,
        duration=duration_ms,
        loop=0,
    )

    # Save final frame
    final_png = os.path.join(args.output_dir, "kmeans_pipeline_final.png")
    frames[-1].save(final_png)

    print("DONE")
    print(f"GIF: {gif_path}")
    print(f"Final frame: {final_png}")
    print(f"Frames dir: {frames_png_dir}")
    print(f"Total frames: {len(frames)}")
    print(f"K-means converged at iteration: {conv_iter}")


if __name__ == "__main__":
    main()
