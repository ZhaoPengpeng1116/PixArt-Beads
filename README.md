# PixArt Beads

PixArt Beads（拼豆）

This repo contains some python scripts that should be useful in transforming images into pixel-beads images and handcrafts!

本仓库包含一些 Python 脚本，可用于将图像转换为拼豆图和手工制品！

<img src="./media/FNL-Pilxten_41-TransportCopter.png" width="300px"> <img src="./media/FNL-Pilxten_41-BattleCopter.png" width="300px">


Some of the main features are:

主要特性包括：

* **Color quantization:** with the option to use number of colors, provided or user-defined color palettes.
* **Image downscale:** take an image and downsize it to a desired number of pixels.
* **Color mapping:** manually change colors to do things like remove the background.
* **Color counts:** count the number of beads of each color that are needed for our handcraft.
* **Grid overlay:** option to add a light grid to visualize individual bead positions on the final image.
* **Row/column labels:** option to add row and column numbers around the grid for easier placement reference.
* **Author annotation:** option to add author/credit information to the final output.

* **颜色量化：** 支持使用指定颜色数、内置或自定义调色板。
* **图像缩放：** 将图像缩放到期望的像素尺寸。
* **颜色映射：** 手动更改颜色，例如移除背景。
* **颜色计数：** 统计手工制作所需的每种颜色的拼豆数量。
* **网格叠加：** 可选在最终拼豆图上添加浅色网格以标注各拼豆位置。
* **行列编号：** 可选在网格周围绘制行号和列号以便放置参考。
* **作者标注：** 可选在最终输出上添加作者/署名信息。


<img src="./media/sami.png" width="200px"><img src="./media/B-SGB_M1A-sami.png" width="200px" ><img src="./media/C-SGB_M1A-sami.png" width="200px"><img src="./media/D-SGB_M1A-sami.png" width="200px">

## Instructions / 使用说明

**IMPORTANT NOTE:** For a step-by-step use of the scripts, please have a look at the provided [demo](./demo) after installing the dependencies.

**重要提示：** 安装依赖后，如需逐步使用脚本，请查看提供的 [demo](./demo)。

To use the scripts first install the required dependencies either through the REQUIREMENTS files (`txt`/`yml`), or manually:

要使用这些脚本，请先通过 REQUIREMENTS 文件（`txt`/`yml`）或手动安装所需依赖：

```bash
pip install -r REQUIREMENTS.txt
```

Or install dependencies manually:

或手动安装：

```bash
pip install numpy
pip install Pillow
pip install matplotlib
pip install opencv-python
```

Give the bash script executable permissions:

为 bash 脚本添加可执行权限：

```bash
chmod +x main.sh
```

And then run it as follows:

然后按如下方式运行：

```bash
./main.sh $PTH $IMG $DWN $UPS $DBG $GRD $LBL $AUTH
```

* `PTH`: Folder in which our image(s) are stored along with the palettes and color mapper.
* `IMG`: Image name for the file to be processed.
* `DWN`: Width in pixels for our output image (leave as `0` if no downscaling is desired).
* `UPS`: Upscaler multiplier for the plots (`10`, the suggested value, will multiply the dimensions of the downscaled images by ten when exporting the output).
* `DBG`: Debug mode (leave as `0` if no intermediary output is desired, and as `1` to have each intermediate plot exported).
* `GRD`: Final grid overlay (set to `1` to add a light grid to the final beads image, `0` otherwise).
* `LBL`: Row/column labels (set to `1` to add an extra border row/column with numbers around the grid, `0` otherwise).
* `AUTH`: Optional author label to append next to the size/total text in the swatch (e.g., `(@晚回舟)`).

* `PTH`：存放图像、调色板与颜色映射文件的目录。
* `IMG`：要处理的图像文件名。
* `DWN`：输出图像的像素宽度（不缩放请设为 `0`）。
* `UPS`：输出图的放大倍率（建议 `10`，导出时将缩放后的图像尺寸放大 10 倍）。
* `DBG`：调试模式（不需要中间输出请设为 `0`，设为 `1` 会导出每个中间结果）。
* `GRD`：最终网格叠加（设为 `1` 在最终拼豆图上添加浅色网格，`0` 不添加）。
* `LBL`：行列编号（设为 `1` 在网格外围额外加一行一列用于标注行号与列号，`0` 不绘制）。
* `AUTH`：可选作者标注，追加到 Size/Total 文本后（例如 `(@晚回舟)`）。

This will take the `IMG` in the set `PTH` along with all the `*.plt` files stored in the directory and the `CMapper.map`, and generate a nested output folder (in the same directory) with the bead plots. Alternatively, we can use the `batch.sh` file to process all the images stored in the same directory:

该命令会读取 `PTH` 目录中的 `IMG`、所有 `*.plt` 文件以及 `CMapper.map`，并在同一目录下生成包含拼豆图的嵌套输出文件夹。或者，可以使用 `batch.sh` 处理同一目录中的所有图片：

```bash
./batch.sh $PTH $DWN $UPS $DBG
```

Finally, the script can also be called from python with:

最后，也可以通过 Python 调用脚本：

```bash
python main.py $PTH $IMG $PAL $DWN $UPS $DBG $GRD $LBL $AUTH
```

where an additional parameter `PAL` is needed for the color palette filename (if set to a number instead of a `.plt` file, it will instead quantize to the provided number of colors).

其中需要额外的参数 `PAL` 指定调色板文件名（如果不是 `.plt` 文件而是数字，则会量化到给定的颜色数量）。

### Output Files / 输出文件

The script generates several output files for each image:

脚本为每张图像生成以下输出文件：

* **DWN**: Downscaled image (resized to the target dimensions)
* **UPS**: Upscaled image (enlarged for display/printing)
* **GRD**: Grid overlay (with beads grid lines)
* **BDS**: Beads plot (circular beads visualization)
* **SWT**: Color swatch (palette with color counts)
* **FNL**: Final output (beads plot + color swatch)

* **DWN**: 降采样图像（缩放到目标尺寸）
* **UPS**: 放大图像（用于展示/打印）
* **GRD**: 网格图（含拼豆网格线）
* **BDS**: 拼豆图（圆形拼豆可视化）
* **SWT**: 色卡（调色板与颜色数量统计）
* **FNL**: 最终输出（拼豆图 + 色卡）


<img src="./media/FNL-SGBM1A_4-sami.png" width="800px">

## Available Palettes / 可用调色板

Some nice [color palettes](./palettes/README.md) are included in the scripts, but if you have the hex colors of your beads, please follow [this link](./palettes/README.md) for information on how to use them in your handcraft! A subset of the included palettes is shown but follow the [link for the full list](./palettes/README.md):

脚本内置了一些不错的[调色板](./palettes/README.md)。如果你有拼豆的十六进制颜色值，请查看[这里](./palettes/README.md)了解如何在你的手工制作中使用它们！下面仅展示了部分调色板，完整列表请见[该链接](./palettes/README.md)：

<table>
    <tr><th>Code</th><th>Palette</th><th>Source</th></tr>
    <!--Table Begins-->
    <tr><td>CoolWood_8</td><td><img src='./palettes/CoolWood_8.png'></td><td><a href=https://lospec.com/palette-list/coldwood8>https://lospec.com/palette-list/coldwood8</a></td></tr>
    <tr><td>Gray2Bit_4</td><td><img src='./palettes/Gray2Bit_4.png'></td><td><a href=https://lospec.com/palette-list/2-bit-grayscale>https://lospec.com/palette-list/2-bit-grayscale</a></td></tr>
    <tr><td>IslandJoy_16</td><td><img src='./palettes/IslandJoy_16.png'></td><td><a href=https://lospec.com/palette-list/island-joy-16>https://lospec.com/palette-list/island-joy-16</a></td></tr>
    <tr><td>MF_16</td><td><img src='./palettes/MF_16.png'></td><td><a href=https://lospec.com/palette-list/mf-16>https://lospec.com/palette-list/mf-16</a></td></tr>
    <tr><td>Mist_GB</td><td><img src='./palettes/Mist_GB.png'></td><td><a href=https://lospec.com/palette-list/mist-gb>https://lospec.com/palette-list/mist-gb</a></td></tr>
    <tr><td>NES</td><td><img src='./palettes/NES.png'></td><td><a href=https://lospec.com/palette-list/nintendo-entertainment-system>https://lospec.com/palette-list/nintendo-entertainment-system</a></td></tr>
    <tr><td>Nostalgia_36</td><td><img src='./palettes/Nostalgia_36.png'></td><td><a href=https://lospec.com/palette-list/nostalgia36>https://lospec.com/palette-list/nostalgia36</a></td></tr>
    <tr><td>Super_16</td><td><img src='./palettes/Super_16.png'></td><td><a href=https://lospec.com/palette-list/super16>https://lospec.com/palette-list/super16</a></td></tr>
    <tr><td>Sweetie_16</td><td><img src='./palettes/Sweetie_16.png'></td><td><a href=https://lospec.com/palette-list/sweetie-16>https://lospec.com/palette-list/sweetie-16</a></td></tr>
</table> 

## Author / 作者

本项目基于 GNU General Public License v3.0（GPLv3）协议，从原项目 fork 而来并进行二次开发，承诺对所做的任何修改均进行开源。

原项目地址：https://github.com/Chipdelmal/PixArt-Beads
