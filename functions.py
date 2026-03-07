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
from sklearn.cluster import KMeans

###############################################################################
# Globals 
###############################################################################
FIDS = ('QNT', 'DWN', 'UPS', 'GRD', 'SWT', 'BDS', 'FNL', 'CMP')
MTHDS = (0, Image.BILINEAR)
RADII = (0.2, 0.975)
(BEAD_ALPHA, BEAD_BKG) = (1.0, '#fefefe')
SLEEP = 5

MARD_MAP = {
    '#faf5cd': 'A1',
    '#fcfed6': 'A2',
    '#fcff92': 'A3',
    '#f7ec5c': 'A4',
    '#f0d83a': 'A5',
    '#fda951': 'A6',
    '#fa8c4f': 'A7',
    '#fbda4d': 'A8',
    '#f79d5f': 'A9',
    '#f47e38': 'A10',
    '#fedb99': 'A11',
    '#fda276': 'A12',
    '#fec667': 'A13',
    '#f75842': 'A14',
    '#fbf65e': 'A15',
    '#feff97': 'A16',
    '#fde173': 'A17',
    '#fcbf80': 'A18',
    '#fd7e77': 'A19',
    '#f9d666': 'A20',
    '#fae393': 'A21',
    '#edf878': 'A22',
    '#e4c8ba': 'A23',
    '#f3f6a9': 'A24',
    '#fdf785': 'A25',
    '#ffc734': 'A26',
    '#dff13b': 'B1',
    '#64f343': 'B2',
    '#a1f586': 'B3',
    '#5fdf34': 'B4',
    '#39e158': 'B5',
    '#64e0a4': 'B6',
    '#3eae7c': 'B7',
    '#1d9b54': 'B8',
    '#2a5037': 'B9',
    '#9ad1ba': 'B10',
    '#627032': 'B11',
    '#1a6e3d': 'B12',
    '#c8e87d': 'B13',
    '#abe84f': 'B14',
    '#305335': 'B15',
    '#c0ed9c': 'B16',
    '#9eb33e': 'B17',
    '#e6ed4f': 'B18',
    '#26b78e': 'B19',
    '#cbeccf': 'B20',
    '#18616a': 'B21',
    '#0a4241': 'B22',
    '#343b1a': 'B23',
    '#e8faa6': 'B24',
    '#4e846d': 'B25',
    '#907c35': 'B26',
    '#d0e0af': 'B27',
    '#9ee5bb': 'B28',
    '#c6df5f': 'B29',
    '#e3fbb1': 'B30',
    '#b4e691': 'B31',
    '#92ad60': 'B32',
    '#f0fee4': 'C1',
    '#abf8fe': 'C2',
    '#a2e0f7': 'C3',
    '#44cdfb': 'C4',
    '#06aadf': 'C5',
    '#54a7e9': 'C6',
    '#3977ca': 'C7',
    '#0f52bd': 'C8',
    '#3349c3': 'C9',
    '#3cbce3': 'C10',
    '#2aded3': 'C11',
    '#1e334e': 'C12',
    '#cde7fe': 'C13',
    '#d5fcf7': 'C14',
    '#21c5c4': 'C15',
    '#1858a2': 'C16',
    '#02d1f3': 'C17',
    '#213244': 'C18',
    '#18869d': 'C19',
    '#1a70a9': 'C20',
    '#bcddfc': 'C21',
    '#6bb1bb': 'C22',
    '#c8e2fd': 'C23',
    '#7ec5f9': 'C24',
    '#a9e8e0': 'C25',
    '#42adcf': 'C26',
    '#d0def9': 'C27',
    '#bdcee8': 'C28',
    '#364a89': 'C29',
    '#acb7ef': 'D1',
    '#868dd3': 'D2',
    '#3554af': 'D3',
    '#162d7b': 'D4',
    '#b34ec6': 'D5',
    '#b37bdc': 'D6',
    '#8758a9': 'D7',
    '#e3d2fe': 'D8',
    '#d5b9f4': 'D9',
    '#301a49': 'D10',
    '#beb9e2': 'D11',
    '#dc99ce': 'D12',
    '#b5038d': 'D13',
    '#862993': 'D14',
    '#2f1f8c': 'D15',
    '#e2e4f0': 'D16',
    '#c7d3f9': 'D17',
    '#9a64b8': 'D18',
    '#d8c2d9': 'D19',
    '#9a35ad': 'D20',
    '#940595': 'D21',
    '#38389a': 'D22',
    '#eadbf8': 'D23',
    '#768ae1': 'D24',
    '#4950c2': 'D25',
    '#d6c6eb': 'D26',
    '#f6d4cb': 'E1',
    '#fcc1dd': 'E2',
    '#f6bde8': 'E3',
    '#e8649e': 'E4',
    '#f0569f': 'E5',
    '#eb4172': 'E6',
    '#c53674': 'E7',
    '#fddbe9': 'E8',
    '#e376c7': 'E9',
    '#d13b95': 'E10',
    '#f7dad4': 'E11',
    '#f693bf': 'E12',
    '#b5026a': 'E13',
    '#fad4bf': 'E14',
    '#f5c9ca': 'E15',
    '#fbf4ec': 'E16',
    '#f7e3ec': 'E17',
    '#f9c8db': 'E18',
    '#f6bbd1': 'E19',
    '#d7c6ce': 'E20',
    '#c09da4': 'E21',
    '#b38c9f': 'E22',
    '#937d8a': 'E23',
    '#debee5': 'E24',
    '#fe9381': 'F1',
    '#f63d4b': 'F2',
    '#ee4e3e': 'F3',
    '#fb2a40': 'F4',
    '#e10328': 'F5',
    '#913635': 'F6',
    '#911932': 'F7',
    '#bb0126': 'F8',
    '#e0677a': 'F9',
    '#874628': 'F10',
    '#592323': 'F11',
    '#f3536b': 'F12',
    '#f45c45': 'F13',
    '#fcadb2': 'F14',
    '#d50527': 'F15',
    '#f8c0a9': 'F16',
    '#e89b7d': 'F17',
    '#d07f4a': 'F18',
    '#be454a': 'F19',
    '#c69495': 'F20',
    '#f2b8c6': 'F21',
    '#f7c3d0': 'F22',
    '#ed806c': 'F23',
    '#e09daf': 'F24',
    '#e84854': 'F25',
    '#ffe4d3': 'G1',
    '#fcc6ac': 'G2',
    '#f1c4a5': 'G3',
    '#dcb387': 'G4',
    '#e7b34e': 'G5',
    '#e3a014': 'G6',
    '#985c3a': 'G7',
    '#713d2f': 'G8',
    '#e4b685': 'G9',
    '#da8c42': 'G10',
    '#dac898': 'G11',
    '#fec993': 'G12',
    '#b2714b': 'G13',
    '#8b684c': 'G14',
    '#f6f8e3': 'G15',
    '#f2d8c1': 'G16',
    '#77544e': 'G17',
    '#ffe3d5': 'G18',
    '#dd7d41': 'G19',
    '#a5452f': 'G20',
    '#b38561': 'G21',
    '#ffffff': 'H1',
    '#fbfbfb': 'H2',
    '#b4b4b4': 'H3',
    '#878787': 'H4',
    '#464648': 'H5',
    '#2c2c2c': 'H6',
    '#010101': 'H7',
    '#e7d6dc': 'H8',
    '#efedee': 'H9',
    '#ebebeb': 'H10',
    '#cdcdcd': 'H11',
    '#fdf6ee': 'H12',
    '#f4edf1': 'H13',
    '#ced7d4': 'H14',
    '#9aa6a6': 'H15',
    '#1b1213': 'H16',
    '#f0eeef': 'H17',
    '#fcfff6': 'H18',
    '#f2eee5': 'H19',
    '#96a09f': 'H20',
    '#f8fbe6': 'H21',
    '#cacad2': 'H22',
    '#9b9c94': 'H23',
    '#bbc6b6': 'M1',
    '#909994': 'M2',
    '#697e81': 'M3',
    '#e0d4bc': 'M4',
    '#d1ccaf': 'M5',
    '#b0aa86': 'M6',
    '#b0a796': 'M7',
    '#ae8082': 'M8',
    '#a68862': 'M9',
    '#c4b3bb': 'M10',
    '#9d7693': 'M11',
    '#644b51': 'M12',
    '#c79266': 'M13',
    '#c27563': 'M14',
    '#747d7a': 'M15',
}

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
    imgCV = cv2.rotate(imgCV, cv2.ROTATE_90_COUNTERCLOCKWISE)
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


def normalizeHex(hexColor):
    if not hexColor:
        return None
    h = hexColor.strip().lower()
    if not h.startswith('#'):
        h = f'#{h}'
    return h


def getMardCode(hexColor):
    h = normalizeHex(hexColor)
    if not h:
        return None
    return MARD_MAP.get(h)


def _hexToRgb(hexColor):
    rgb = ImageColor.getcolor(hexColor, "RGB")
    return np.array(rgb, dtype=np.int16)


def getNearestMardCode(hexColor):
    h = normalizeHex(hexColor)
    if not h:
        return None
    if h in MARD_MAP:
        return MARD_MAP[h]
    target = _hexToRgb(h)
    best_code = None
    best_dist = None
    for mhex, code in MARD_MAP.items():
        dist = np.sum((target - _hexToRgb(mhex)) ** 2)
        if best_dist is None or dist < best_dist:
            best_dist = dist
            best_code = code
    return best_code


def getFullMardPalette():
    """
    Get all MARD color codes as a palette list.
    
    Returns:
        List of all MARD hex colors (215 colors)
    """
    return list(MARD_MAP.keys())


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
    authorFontdict = {'family':'monospace', 'weight':'normal', 'size':24},
    useMard=False
    ):
    pal = imgPalette
    # Create canvas
    fig, ax = plt.subplots(figsize=(width/100.0, height/100.0))
    ax.set_position([0, 0, 1, 1])
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
        labelText = colorText
        if useMard:
            mardCode = getMardCode(color)
            if not mardCode:
                mardCode = getNearestMardCode(color)
            if mardCode:
                labelText = f'{mardCode} ({colorText})'
        ax.text(
            hshift+wr*1.1+col_shift, y_pos+hr/2, 
            f' {labelText} ({count:05}) ', 
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


def createComparisonGrid(originalPath, upsPath, grdPath, fnlPath, outputPath):
    """
    Create a comparison grid: top row = original, UPS, GRD; bottom row = FNL (centered)
    
    Args:
        originalPath: Path to original image
        upsPath: Path to UPS image
        grdPath: Path to GRD image
        fnlPath: Path to FNL image
        outputPath: Output path for comparison grid
    """
    # Load images
    imgOrig = Image.open(originalPath).convert('RGB')
    imgUps = Image.open(upsPath).convert('RGB')
    imgGrd = Image.open(grdPath).convert('RGB')
    imgFnl = Image.open(fnlPath).convert('RGB')
    
    # Resize original to match UPS height while maintaining aspect ratio
    targetHeight = imgUps.height
    aspectRatio = imgOrig.width / imgOrig.height
    newWidth = int(targetHeight * aspectRatio)
    imgOrigResized = imgOrig.resize((newWidth, targetHeight), Image.LANCZOS)
    
    # Create spacing between images
    gap = 10
    gapImg = Image.new('RGB', (gap, targetHeight), color=(255, 255, 255))
    
    # Create top row: original, gap, UPS, gap, GRD
    topRow = hConcat(imgOrigResized, gapImg)
    topRow = hConcat(topRow, imgUps)
    topRow = hConcat(topRow, gapImg)
    topRow = hConcat(topRow, imgGrd)
    
    # Create bottom row: FNL centered (ensure full width is visible)
    # If FNL is wider than top row, stretch top row to match FNL width
    if imgFnl.width > topRow.width:
        # Scale top row to match FNL width
        scaleRatio = imgFnl.width / topRow.width
        newHeight = int(topRow.height * scaleRatio)
        topRow = topRow.resize((imgFnl.width, newHeight), Image.LANCZOS)
        xOffset = 0
    else:
        xOffset = (topRow.width - imgFnl.width) // 2
    
    bottomBg = Image.new('RGB', (topRow.width, imgFnl.height), color=(254, 254, 254))
    bottomBg.paste(imgFnl, (xOffset, 0))
    
    # Combine top and bottom
    combined = vConcat(topRow, bottomBg)
    
    # Add margins (top, left, right) with same gap width
    finalWidth = combined.width + 2 * gap
    finalHeight = combined.height + gap
    result = Image.new('RGB', (finalWidth, finalHeight), color=(255, 255, 255))
    result.paste(combined, (gap, gap))
    result.save(outputPath)
    
    return result


def isInt(element):
    try:
        int(element)
        return True
    except ValueError:
        return False


def clusterColors(colorPalette, numClusters):
    """
    Use K-means clustering to reduce palette to target color count.
    
    Args:
        colorPalette: List of hex color strings (e.g., ['#FF0000', '#00FF00', ...])
        numClusters: Target number of colors
    
    Returns:
        List of clustered hex colors
    """
    if len(colorPalette) <= numClusters:
        return colorPalette
    
    # Convert hex to RGB
    rgbArray = np.array([
        ImageColor.getcolor(c, "RGB") for c in colorPalette
    ])
    
    # K-means clustering on RGB
    kmeans = KMeans(n_clusters=numClusters, n_init=10, random_state=42)
    kmeans.fit(rgbArray)
    
    # Get cluster centers and convert back to hex
    centers = kmeans.cluster_centers_.astype(np.uint8)
    clusteredColors = [rgbToHex(c[0], c[1], c[2]) for c in centers]
    
    return clusteredColors


def remapImageToClusteredPalette(img, originalPalette, clusteredPalette):
    """
    Remap image from original palette to clustered palette by finding nearest color.
    
    Args:
        img: PIL Image with palette mode
        originalPalette: List of original hex colors
        clusteredPalette: List of clustered hex colors
    
    Returns:
        PIL Image quantized to clustered palette
    """
    # Convert image to RGB for processing
    img_rgb = img.convert('RGB')
    
    # Get clustered palette
    cpal = paletteReshape(clusteredPalette)
    remapped_img = quantizeImage(
        img_rgb, colorsNumber=cpal[0], colorPalette=cpal[1], 
        method=MTHDS[0], dither=False
    )
    
    return remapped_img


def isInt(element):
    try:
        int(element)
        return True
    except ValueError:
        return False
