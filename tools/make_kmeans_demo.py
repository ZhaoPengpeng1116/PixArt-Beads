import os
import argparse
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from sklearn.cluster import KMeans


def nearest_labels(points: np.ndarray, centers: np.ndarray) -> np.ndarray:
    d = points[:, None, :] - centers[None, :, :]
    dist2 = np.sum(d * d, axis=2)
    return np.argmin(dist2, axis=1)


def quantize_with_centers(img_arr: np.ndarray, centers: np.ndarray) -> np.ndarray:
    flat = img_arr.reshape(-1, 3).astype(np.float32)
    labels = nearest_labels(flat, centers.astype(np.float32))
    q = centers[labels].reshape(img_arr.shape)
    return np.clip(q, 0, 255).astype(np.uint8)


def draw_palette_bar(centers: np.ndarray, counts: np.ndarray, width: int, height: int) -> Image.Image:
    bar = Image.new("RGB", (width, height + 24), (255, 255, 255))
    draw = ImageDraw.Draw(bar)
    font = ImageFont.load_default()
    k = len(centers)
    sw = max(1, width // max(1, k))
    total = counts.sum()
    for i, c in enumerate(centers.astype(np.uint8)):
        x0 = i * sw
        x1 = width if i == k - 1 else (i + 1) * sw
        draw.rectangle([x0, 0, x1, height], fill=(int(c[0]), int(c[1]), int(c[2])))
        pct = 100.0 * counts[i] / max(1, total)
        label = f"{counts[i]}\n({pct:.1f}%)"
        draw.text((x0 + 2, height + 2), label, fill=(0, 0, 0), font=font)
    return bar


def build_frame(
    original: Image.Image,
    quantized: Image.Image,
    centers: np.ndarray,
    counts: np.ndarray,
    subtitle: str,
    panel_h: int = 280,
) -> Image.Image:
    """Build frame showing original vs quantized with color palette."""
    font = ImageFont.load_default()

    # Scale panels to fixed height
    ow, oh = original.size
    qw, qh = quantized.size
    o_new = (int(ow * panel_h / oh), panel_h)
    q_new = (int(qw * panel_h / qh), panel_h)

    orig = original.resize(o_new, Image.NEAREST)
    quan = quantized.resize(q_new, Image.NEAREST)

    gap = 16
    margin = 15
    palette_h = 50
    text_h = 30
    
    width = margin * 2 + orig.width + gap + quan.width
    height = margin * 2 + text_h + panel_h + gap + palette_h
    canvas = Image.new("RGB", (width, height), (250, 250, 250))
    draw = ImageDraw.Draw(canvas)

    # Subtitle only (no title)
    draw.text((margin, margin), subtitle, fill=(50, 50, 50), font=font)

    y_panel = margin + text_h
    canvas.paste(orig, (margin, y_panel))
    canvas.paste(quan, (margin + orig.width + gap, y_panel))

    draw.text((margin, y_panel - 12), "Original", fill=(60, 60, 60), font=font)
    draw.text((margin + orig.width + gap, y_panel - 12), "K-means", fill=(60, 60, 60), font=font)

    # Palette bar with counts
    bar = draw_palette_bar(centers, counts, width - margin * 2, 44)
    canvas.paste(bar, (margin, y_panel + panel_h + gap))
    
    return canvas


def main():
    parser = argparse.ArgumentParser(description="Generate K-means clustering demo animation")
    parser.add_argument("--input", required=True, help="Input image path")
    parser.add_argument("--output-dir", required=True, help="Output directory")
    parser.add_argument("--k", type=int, default=6, help="Number of clusters")
    parser.add_argument("--iters", type=int, default=20, help="Max iteration frames")
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

    # Initialize centers from random sample pixels
    init_idx = rng.choice(sample.shape[0], args.k, replace=False)
    centers = sample[init_idx].copy()

    frames = []
    frames_png_dir = os.path.join(args.output_dir, "frames")
    os.makedirs(frames_png_dir, exist_ok=True)

    # Frame 0: Initial random centers
    initial_labels = nearest_labels(flat, centers.astype(np.float32))
    initial_counts = np.bincount(initial_labels, minlength=args.k)
    
    subtitle = f"Iteration 0: Random initialization (K={args.k})"
    frame0 = build_frame(img, img, centers, initial_counts, subtitle)
    frames.append(frame0)

    prev_centers = None
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

        # Compute cluster sizes
        labels = nearest_labels(flat, centers.astype(np.float32))
        counts = np.bincount(labels, minlength=args.k)

        shift = 0.0 if prev_centers is None else float(np.linalg.norm(centers - prev_centers))
        subtitle = f"Iteration {i}: Updating clusters (Shift={shift:.4f})"
        
        fr = build_frame(img, q_img, centers, counts, subtitle)
        frames.append(fr)
        fr.save(os.path.join(frames_png_dir, f"frame_{i:02d}.png"))

        # Stop if converged
        if prev_centers is not None and shift < 1e-2:
            print(f"Converged at iteration {i}")
            break
        prev_centers = centers.copy()

    # Hold final frame longer
    for _ in range(4):
        frames.append(frames[-1].copy())

    # Save GIF
    gif_path = os.path.join(args.output_dir, "kmeans_demo.gif")
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
    final_png = os.path.join(args.output_dir, "kmeans_final.png")
    frames[-1].save(final_png)

    print("DONE")
    print(f"GIF: {gif_path}")
    print(f"Final frame: {final_png}")
    print(f"Frames dir: {frames_png_dir}")
    print(f"Total frames: {len(frames)}")


if __name__ == "__main__":
    main()
