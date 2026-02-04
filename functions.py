###############################################################################
#   Functions Definitions
###############################################################################

import re
import os
import cv2
import numpy as np
from cv2 import cvtColor
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from PIL import Image, ImageColor, ImageDraw, ImageFont
import matplotlib.patches as mpatch

###############################################################################
# Globals 
###############################################################################
FIDS = ('QNT', 'DWN', 'UPS', 'GRD', 'SWT', 'BDS', 'FNL')
MTHDS = (0, Image.BILINEAR)
RADII = (0.2, 0.975)
(BEAD_ALPHA, BEAD_BKG) = (1.0, '#fefefe')
SLEEP = 5

###############################################################################
# Functions 
###############################################################################
def paletteReshape(colorPalette):
    # Hex to entries
    rgbTuples = [ImageColor.getcolor(i, "RGB") for i in colorPalette]
    pal = [item for sublist in rgbTuples for item in sublist]
    entries = int(len(pal)/3)
    # Palette swatch - repeat the last color for remaining slots to avoid extra colors
    lastColor = rgbTuples[-1]
    repeatedPal = pal + list(lastColor) * (256 - entries)
    palette = repeatedPal[:256*3]
    resnp = np.arange(256, dtype=np.uint8).reshape(256, 1)
    resim = Image.fromarray(resnp, mode='P')
    resim.putpalette(palette)
    # Return
    return (len(pal), resim)

def quantizeImage(img, colorsNumber=255, colorPalette=None, method=0, dither=False):
    if colorPalette is None:
        img = img.quantize(colorsNumber, method=method, dither=dither)
    else:
        img = img.quantize(
            palette=colorPalette, method=method, dither=dither
        )
    return img


def gridOverlay(img, gridSize, gridColor=(0,0,0)):
    img = np.asarray(img)
    (height, width, channels) = img.shape
    for x in range(0, width-1, gridSize):
        cv2.line(img, (x, 0), (x, height), gridColor, 1, 1)
    for x in range(0, height-1, gridSize):
        cv2.line(img, (0, x), (width, x), gridColor, 1, 1)
    return img


def addGrid(img, gridSize, color=(200, 200, 200), width=1):
    gridSize = max(1, int(gridSize))
    img = img.copy()
    draw = ImageDraw.Draw(img)
    (w, h) = img.size
    for x in range(0, w + 1, gridSize):
        draw.line([(x, 0), (x, h)], fill=color, width=width)
    for y in range(0, h + 1, gridSize):
        draw.line([(0, y), (w, y)], fill=color, width=width)
    return img


def addGridByCount(img, xCount, yCount, color=(200, 200, 200), width=1):
    xCount = max(1, int(xCount))
    yCount = max(1, int(yCount))
    img = img.copy()
    draw = ImageDraw.Draw(img)
    (w, h) = img.size
    cellW = w / float(xCount)
    cellH = h / float(yCount)
    for i in range(0, xCount + 1):
        x = round(i * cellW)
        draw.line([(x, 0), (x, h)], fill=color, width=width)
    for i in range(0, yCount + 1):
        y = round(i * cellH)
        draw.line([(0, y), (w, y)], fill=color, width=width)
    return img


def _loadFont(size):
    candidates = [
        "C:/Windows/Fonts/msyh.ttc",
        "C:/Windows/Fonts/msyh.ttf",
        "C:/Windows/Fonts/simhei.ttf",
        "C:/Windows/Fonts/simsun.ttc",
        "C:/Windows/Fonts/arial.ttf",
    ]
    for pth in candidates:
        if os.path.exists(pth):
            return ImageFont.truetype(pth, size)
    return ImageFont.load_default()


def _getFontPath():
    candidates = [
        "C:/Windows/Fonts/msyh.ttc",
        "C:/Windows/Fonts/msyh.ttf",
        "C:/Windows/Fonts/simhei.ttf",
        "C:/Windows/Fonts/simsun.ttc",
        "C:/Windows/Fonts/arial.ttf",
    ]
    for pth in candidates:
        if os.path.exists(pth):
            return pth
    return None


def addGridLabels(img, xCount, yCount, color=(120, 120, 120)):
    return addGridLabelsWithMargin(img, xCount, yCount, color=color)


def addGridLabelsWithMargin(img, xCount, yCount, color=(120, 120, 120)):
    xCount = max(1, int(xCount))
    yCount = max(1, int(yCount))
    (w, h) = img.size
    cellW = w / float(xCount)
    cellH = h / float(yCount)
    marginW = max(1, int(round(cellW)))
    marginH = max(1, int(round(cellH)))
    bg = ImageColor.getcolor(BEAD_BKG, "RGB")
    canvas = Image.new('RGB', (w + 2 * marginW, h + 2 * marginH), color=bg)
    canvas.paste(img, (marginW, marginH))
    draw = ImageDraw.Draw(canvas)
    fontSize = max(10, int(min(cellW, cellH) * 0.35))
    font = _loadFont(fontSize)
    # Top and bottom labels
    for i in range(1, xCount + 1):
        x = marginW + round((i - 0.5) * cellW)
        label = str(i)
        bbox = draw.textbbox((0, 0), label, font=font)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        draw.text((x - tw / 2, (marginH - th) / 2), label, fill=color, font=font)
        draw.text((x - tw / 2, marginH + h + (marginH - th) / 2), label, fill=color, font=font)
    # Left and right labels
    for i in range(1, yCount + 1):
        y = marginH + round((i - 0.5) * cellH)
        label = str(i)
        bbox = draw.textbbox((0, 0), label, font=font)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        draw.text(((marginW - tw) / 2, y - th / 2), label, fill=color, font=font)
        draw.text((marginW + w + (marginW - tw) / 2, y - th / 2), label, fill=color, font=font)
    return canvas


def totalLabelYCenter(imgHeight, paletteCount, n_groups=1):
    n_rows = (paletteCount // n_groups) + 1
    y_norm = (n_rows + 0.5) / (n_rows + 1)
    return imgHeight * y_norm


def addAuthorLabel(img, text, total, y_center=None, color=(120, 120, 120)):
    if not text:
        return img
    img = img.copy()
    draw = ImageDraw.Draw(img)
    fontSize = max(12, int(img.height * 0.07))
    font = _loadFont(fontSize)
    totalText = f'Total: {total}'
    bbox = draw.textbbox((0, 0), totalText, font=font)
    totalW = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    left = int(img.width * 0.05)
    x = left + totalW + 10
    if y_center is None:
        y_center = img.height - th / 2 - 6
    y = int(y_center + th * 0.65)
    draw.text((left, y), text, fill=color, font=font)
    return img


def makeFolder(path):
    if not os.path.exists(path):
        try:
            os.mkdir(path)
        except OSError:
            raise OSError(
                    "Can't create destination directory (%s)!" % (path)
                )

def isNotebook():
    try:
        shell = get_ipython().__class__.__name__
        if shell == 'ZMQInteractiveShell':
            return True
        elif shell == 'TerminalInteractiveShell':
            return False
        else:
            return False
    except NameError:
        return False


def plotBeads(
        fig, ax, img, diameter=1,
        innerRadius=.2, outerRadius=.975,
        imgAlpha=.9, bgColor=(1, 1, 1)
    ):
    radius = diameter/2
    (width, height, _) = img.shape
    # Iterate through pixels 
    for h in range(int(height)):
        y = (diameter*h)
        for w in range(int(width)):
            x = (diameter*w)
            coord = (width-x, height-y)
            # Plot solid disk
            crl = plt.Circle(
                coord, radius*outerRadius, 
                color=tuple([i/255 for i in img[x][y]]), alpha=imgAlpha,
                antialiased=False
            )
            ax.add_patch(crl)
            # Plot empty center
            crlV = plt.Circle(coord, radius*innerRadius, color=bgColor, antialiased=False)
            ax.add_patch(crlV)
    # Clean the frame
    ax.set_xlim(radius, width+radius)
    ax.set_ylim(radius, height+radius)
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)
    ax.set_facecolor(bgColor)
    ax.set_aspect(1)
    ax.axis('off')
    # Return figure
    return (fig, ax)


def genBeadsPlot(
        imgCV, diameter=1, outRadius=0.975, inRadius=0.2, 
        imgAlpha=.9, bgColor='#ffffff'
    ):
    bkgCol = [i/255 for i in ImageColor.getcolor(bgColor, "RGB")]
    imgCV = cvtColor(imgCV, cv2.COLOR_BGR2RGB)
    imgCV = cv2.rotate(imgCV, cv2.cv2.ROTATE_90_COUNTERCLOCKWISE)
    (fig, ax) = plt.subplots(1, 1, figsize=(15, 15))
    (fig, ax) = plotBeads(
        fig, ax, imgCV, diameter=diameter,
        innerRadius=inRadius, outerRadius=outRadius,
        imgAlpha=imgAlpha, bgColor=bkgCol
    )
    return (fig, ax)


def readPaletteFile(filePath, hexPtrn=r'^#(?:[0-9a-fA-F]{3}){1,2}$'):
    with open(filePath) as f:
        lines = f.read().splitlines() 
    (name, source, colors) = (lines[0], lines[1], lines[2:])
    colors = [c for c in colors if re.search(hexPtrn, c)]
    colorPalette = {'name': name, 'source': source, 'palette': colors}
    return colorPalette


def readCMapperFile(filePath):
    with open(filePath) as f:
        lines = f.read().splitlines()
    cMapper = [[i.strip() for i in l.split(',')] for l in lines]
    cMapper = [i for i in cMapper if len(i) > 1]
    return cMapper


def replaceBackground(img, bkgColor, replacementColor='#ffffff'):
    # Convert HEX to RGB
    orig_color = ImageColor.getcolor(bkgColor, "RGB")
    replacement_color = ImageColor.getcolor(replacementColor, "RGB")
    # Replace color
    data = np.array(img)
    data[(data==orig_color).all(axis=-1)] = replacement_color
    img2 = Image.fromarray(data, mode='RGB')
    return img2


def mapColors(img, cMapper=(('#ff7fff', '#ffffff'))):
    for i in cMapper:
        img = replaceBackground(img, i[0], replacementColor=i[1])
    return img


def rgbToHex(r, g, b):
    return '#{:02x}{:02x}{:02x}'.format(r, g, b)


def getImagePalette(img):
    palette = sorted(img.getcolors(), reverse=True)
    hexPalette = [(rgbToHex(*i[1]), i[0]) for i in palette]
    return hexPalette


def genColorSwatch(palette, width, height):
    colors = [ImageColor.getcolor(i, "RGB") for i in palette]
    clstNumber = len(colors)
    pltAppend = np.zeros((height, width, 3))
    (wBlk, hBlk) = (round(width/clstNumber), round(height))
    for row in range(hBlk):
        colorIter = -1
        for col in range(width):
            if (col%wBlk == 0) and (colorIter < clstNumber-1):
                colorIter = colorIter + 1
            pltAppend[row][col] = colors[colorIter]
    return Image.fromarray(pltAppend.astype('uint8'), 'RGB')


def getLuma(r, g, b):
    luma = 0.299*r + 0.587*g + 0.114*b
    return luma


def genColorCounts(
    imgPalette, width, height, imgSize, upscale=1,
        fontdict = {'family':'monospace', 'weight':'normal', 'size':30},
    xlim = (0, 1.25),
    authorLabel=None,
    authorFontdict = {'family':'monospace', 'weight':'normal', 'size':24}
    ):
    pal = imgPalette
    # Create canvas
    fig = plt.gcf()
    DPI = fig.get_dpi()
    ax = fig.add_axes([0, 0, 1, 1])
    fig.set_size_inches(width/float(DPI), height/float(DPI))
    # Setting up groups
    n_groups = 1
    n_rows = len(pal)//n_groups+1
    # Generate swatch with count
    for j in range(len(pal)):
        (wr, hr) = (.25, 1)
        (color, count) = pal[j]
        rgb = [i/255 for i in ImageColor.getcolor(color, "RGB")]
        # Color rows
        col_shift = (j//n_rows)*3
        y_pos = (j%(n_rows))*hr
        # Print rectangle and text
        hshift = .05
        ax.add_patch(mpatch.Rectangle(
            (hshift+col_shift, y_pos), wr, hr, color=rgb, ec='k', lw=4
        ))
        colorText = color.upper()
        ax.text(
            hshift+wr*1.1+col_shift, y_pos+hr/2, 
            f' {colorText} ({count:05}) ', 
            color='k', va='center', ha='left', fontdict=fontdict
        )
    # Add pixel size and total count
    pxSize = [int(i/upscale) for i in imgSize]
    y_pos = ((0)%(n_rows))*hr
    ax.text(
        hshift, y_pos-hr/2, 
        f'Size: {pxSize[0]}x{pxSize[1]}', 
        color='k', va='center', ha='left', fontdict=fontdict
    )
    y_pos = ((j+1)%(n_rows))*hr
    ax.text(
        hshift, y_pos+hr/2, 
        f'Total: {pxSize[0]*pxSize[1]}', 
        color='k', va='center', ha='left', fontdict=fontdict
    )
    if authorLabel:
        y_pos = ((j+1)%(n_rows))*hr
        font_path = _getFontPath()
        if font_path:
            fp = fm.FontProperties(fname=font_path, size=authorFontdict.get('size', 24))
            ax.text(
                hshift, y_pos+hr*0.9,
                f'{authorLabel}',
                color='grey', va='center', ha='left', fontproperties=fp
            )
        else:
            ax.text(
                hshift, y_pos+hr*0.9,
                f'{authorLabel}',
                color='grey', va='center', ha='left', fontdict=authorFontdict
            )
    # Clean up the axes
    ax.set_xlim(xlim[0], xlim[1]*n_groups)
    ax.set_ylim((n_rows), -1)
    ax.axis('off')
    # Return figure
    return (fig, ax)


def downscaleSize(img, downscale):
    if downscale == 0:
        downscale = img.size
    else:
        if type(downscale) is not tuple:
            (wo, ho) = img.size
            downscale = (downscale, int((ho/wo)*downscale))
    return downscale


def makeFolder(path):
    if not os.path.exists(path):
        try:
            os.mkdir(path)
        except OSError:
            raise OSError(
                    "Can't create destination directory (%s)!" % (path)
                )


def hConcat(im1, im2):
    dst = Image.new('RGB', (im1.width + im2.width, im1.height))
    dst.paste(im1, (0, 0))
    dst.paste(im2, (im1.width, 0))
    return dst


def vConcat(im1, im2):
    dst = Image.new('RGB', (im1.width, im1.height + im2.height))
    dst.paste(im1, (0, 0))
    dst.paste(im2, (0, im1.height))
    return dst


def isInt(element):
    try:
        int(element)
        return True
    except ValueError:
        return False
