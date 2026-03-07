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


def get_converged_centers(sample: np.ndarray, k: int, max_iters: int = 50) -> tuple:
    """Run K-means until convergence and return centers + iteration count."""
    rng = np.random.default_rng(42)
    init_idx = rng.choice(sample.shape[0], k, replace=False)
    centers = sample[init_idx].copy()

    for i in range(max_iters):
        km = KMeans(
            n_clusters=k,
            init=centers,
            n_init=1,
            max_iter=1,
            random_state=42,
            algorithm="lloyd",
        )
        km.fit(sample)
        centers = km.cluster_centers_.astype(np.float32)

    return centers, i


def build_comparison_frame(
    original: Image.Image,
    results: dict,  # {k: (quantized_img, centers, counts)}
    title: str,
    subtitle: str,
    panel_h: int = 200,
) -> Image.Image:
    font = ImageFont.load_default()

    # Scale original
    ow, oh = original.size
    o_new = (int(ow * panel_h / oh), panel_h)
    orig = original.resize(o_new, Image.NEAREST)

    # Layout: Original + 4 k-means results in a row
    gap = 10
    margin = 20
    label_h = 20
    palette_h = 40
    text_h = 50

    width = margin * 2 + (orig.width + gap) * (len(results) + 1)
    height = margin * 2 + text_h + panel_h + gap + palette_h + label_h

    canvas = Image.new("RGB", (width, height), (250, 250, 250))
    draw = ImageDraw.Draw(canvas)

    # Title
    draw.text((margin, margin), title, fill=(20, 20, 20), font=font)
    draw.text((margin, margin + 22), subtitle, fill=(70, 70, 70), font=font)

    y_panel = margin + text_h
    x_pos = margin

    # Original image
    canvas.paste(orig, (x_pos, y_panel))
    draw.text((x_pos, y_panel - 16), "Original", fill=(40, 40, 40), font=font)
    x_pos += orig.width + gap

    # K-means results for each K
    for k in sorted(results.keys()):
        q_img, centers, counts = results[k]
        qw, qh = q_img.size
        q_new = (int(qw * panel_h / qh), panel_h)
        quan = q_img.resize(q_new, Image.NEAREST)

        canvas.paste(quan, (x_pos, y_panel))
        draw.text((x_pos, y_panel - 16), f"K={k}", fill=(40, 40, 40), font=font)

        # Draw color palette with counts
        total = counts.sum()
        sw = max(1, quan.width // max(1, k))
        for i, c in enumerate(centers.astype(np.uint8)):
            cx0 = x_pos + i * sw
            cx1 = x_pos + quan.width if i == k - 1 else x_pos + (i + 1) * sw
            draw.rectangle([cx0, y_panel + panel_h + gap, cx1, y_panel + panel_h + gap + palette_h], 
                          fill=(int(c[0]), int(c[1]), int(c[2])))
            pct = 100.0 * counts[i] / max(1, total)
            draw.text((cx0 + 2, y_panel + panel_h + gap + 2), f"{pct:.0f}%", fill=(0, 0, 0), font=font)

        x_pos += quan.width + gap

    return canvas


def main():
    parser = argparse.ArgumentParser(description="Generate K-means comparison for different K values")
    parser.add_argument("--input", required=True, help="Input image path")
    parser.add_argument("--output-dir", required=True, help="Output directory")
    parser.add_argument("--ks", type=int, nargs="+", default=[2, 4, 8, 12], help="K values to compare")
    parser.add_argument("--sample", type=int, default=2000, help="Sample pixel count for fitting")
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

    # Converge K-means for each K
    results = {}
    for k in args.ks:
        print(f"Processing K={k}...")
        centers, iters = get_converged_centers(sample, k, max_iters=50)
        
        q_arr = quantize_with_centers(arr, centers)
        q_img = Image.fromarray(q_arr, mode="RGB")
        
        labels = nearest_labels(flat, centers.astype(np.float32))
        counts = np.bincount(labels, minlength=k)
        
        results[k] = (q_img, centers, counts)

    # Create comparison frame
    title = "K-means 聚类对比"
    subtitle = f"Input: {os.path.basename(args.input)} | K values: {', '.join(map(str, args.ks))}"
    frame = build_comparison_frame(img, results, title, subtitle)
    
    output_path = os.path.join(args.output_dir, "kmeans_comparison.png")
    frame.save(output_path)

    print("DONE")
    print(f"Comparison: {output_path}")


if __name__ == "__main__":
    main()
