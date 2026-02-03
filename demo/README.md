
# PixArt Beads: Demos

# PixArt Beads：示例

These examples show some use-cases for the scripts!

这些示例展示了脚本的一些使用场景！

## Processing a single image

## 处理单张图片

For this demo we're gonna process a sprite from [Advance Wars](https://www.spriters-resource.com/game_boy_advance/advancewars2blackholerising/) (a great site for getting some nice sprites is: [the spriters resource](https://www.spriters-resource.com/). The files needed to run this demo can be found in [this folder](./tCopter).

本示例将处理一张来自 [Advance Wars](https://www.spriters-resource.com/game_boy_advance/advancewars2blackholerising/) 的精灵图（获取精灵图的好网站是：[the spriters resource](https://www.spriters-resource.com/)）。运行该示例所需文件位于[此文件夹](./tCopter)。

<img src="../media/tcopterPalette.png" width="100px">

In this example, we will change the image's background to white, downscale it, and process with the [Blk Neo](https://lospec.com/palette-list/blk-neo) color palette.

在本例中，我们会将图像背景改为白色，缩小尺寸，并使用 [Blk Neo](https://lospec.com/palette-list/blk-neo) 调色板进行处理。

### 1. Setting working directory up

### 1. 设置工作目录

For simplicity, are going to assume the folder is in our `$HOME` directory and is named `tCopter`. First, we place our image `TransportCopter.png` in the folder along with the `BlkNeo_46.plt` color palette file (available [here](https://github.com/Chipdelmal/PixelatorBeads/blob/main/palettes/BlkNeo_46.plt)) and an empty txt file named `CMapper.map` (for the color mapping/background removal).

为简单起见，假设该文件夹位于 `$HOME` 目录下，名称为 `tCopter`。首先将图像 `TransportCopter.png` 放入该文件夹，并放入调色板文件 `BlkNeo_46.plt`（可在[此处](https://github.com/Chipdelmal/PixelatorBeads/blob/main/palettes/BlkNeo_46.plt)获取），以及一个名为 `CMapper.map` 的空 txt 文件（用于颜色映射/移除背景）。

### 2. Color-mapping

### 2. 颜色映射

We want to remove the pink background from the image, so we are going to map that color to white. To do this, just open the `CMapper.map` file in a text editor and add the following line: `#ff7fff, #ffffff`; this will tell our application to change every `#ff7fff` pixel into `#ffffff`. An arbitrary list of color mappings can be added if a more complicated mapping is desired (the colors will be mapped sequentially in the order provided by the file).

我们要移除图像中的粉色背景，因此将该颜色映射为白色。打开 `CMapper.map` 文件并添加一行：`#ff7fff, #ffffff`；这会让应用把所有 `#ff7fff` 像素替换为 `#ffffff`。如果需要更复杂的映射，可以添加任意数量的映射规则（颜色按文件中给出的顺序依次映射）。

### 3. Processing the image

### 3. 处理图像

The only thing needed now is to run our script. The first way to do it is by calling our `bash` script as described in our main [README](../README.md):

接下来只需要运行脚本即可。第一种方式是按照主 [README](../README.md) 中的说明调用 `bash` 脚本：

```bash
./main.sh $PTH $IMG $DWN $UPS $DBG
```

The original image is 63x58 pixels, so let's try and rescale it a bit so that the total width is 48px (the height will be auto-calculated so that it maintains the same aspect ratio). Additionally, let's "upscale" the output images by a factor of 10 so that we end up with images 480x440px in size. Finally, let's set the debug mode on to keep all the intermediate images:

原始图像为 63x58 像素，我们尝试将总宽度缩放到 48px（高度会自动计算以保持纵横比）。同时将输出图像放大 10 倍，得到 480x440px 的图像。最后开启调试模式以保留所有中间结果：

```bash
./main.sh ./demo/tCopter TransportCopter.png 48 10 1
```

This will process the image with all of the `.pal` files available in the work directory. One way to run a specific color palette would be by calling the original python routine:

这会使用工作目录中所有可用的 `.pal` 文件来处理图像。如果只想使用指定调色板，可调用原始的 Python 程序：

```bash
python main.py ./demo/tCopter TransportCopter.png BlkNeo_46.plt 48 10 1
```

Which would give us the same results in this case.

在本例中，两种方式会得到相同结果。

### 4. Outputs

### 4. 输出结果

This script will generate the following images in a `TransportCopter` folder (in order):

脚本会在 `TransportCopter` 文件夹中生成以下图像（按顺序）：

* **DWN**: Downscaled (resized)
* **UPS**: Upscaled
* **GRD**: Gridded
* **BDS**: Beads
* **FNL**: Beads with swatch and color counts

<img src="../media/DWN-BlkNeo_46-TransportCopter.png" width="100px"><img src="../media/UPS-BlkNeo_46-TransportCopter.png" width="100px"><img src="../media/GRD-BlkNeo_46-TransportCopter.png" width="100px"><img src="../media/BDS-BlkNeo_46-TransportCopter.png" width="100px">

<img src="../media/FNL-BlkNeo_46-TransportCopter.png" width="400px">

## Processing a batch of images

## 批量处理图像

Now, let's imagine we wanted to process several images through the same color palettes. For this example, we will use the files in [this folder](./copters).

现在假设我们想用同一组调色板处理多张图像。本例将使用[此文件夹](./copters)中的文件。

<img src="../media/BattleCopter.png" height="100px"> <img src="../media/TransportCopter.png" height="100px">

To do this, we place all the palettes `.plt` files, images and the `CMapping.map` in the base folder and simply call:

做法是把所有调色板 `.plt` 文件、图像以及 `CMapping.map` 放到同一基础目录，然后执行：

```bash
./batch.sh ./demo/copters 0 10 0
```

This time, we are keeping the images in their original size, upscaling them by a factor of 10, and turning the debug mode off.

这次我们保留图像原尺寸，放大 10 倍，并关闭调试模式。

<img src="../media/FNL-Pilxten_41-TransportCopter.png" width="300px"> <img src="../media/FNL-BlkNeo_46-TransportCopter2.png" width="300px">

<img src="../media/FNL-Pilxten_41-BattleCopter.png" width="300px"> <img src="../media/FNL-BlkNeo_46-BattleCopter.png" width="300px">