
import os
from sys import argv
from time import sleep
from os.path import exists
from os import path, remove
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image, ImageColor
import functions as fun

if fun.isNotebook():
    (BASE_PATH, PNG_NAME, PAL_NAME) = (
        '/home/chipdelmal/Documents/PixelatorBeads/AdvanceWars/Portraits/', 
        'sonja.png', 'Pear_36.plt'
    )
    (DOWNSCALE, UPSCALE) = ((50,50), 10)
    DEBUG = True
    GRID = 0
    LABELS = 0
    AUTHOR = None
    MARD = 0
    CLUSTER = 0
else:
    os.environ.pop("QT_QPA_PLATFORM_PLUGIN_PATH", None)
    (BASE_PATH, PNG_NAME, PAL_NAME) = (argv[1], argv[2], argv[3])
    (DOWNSCALE, UPSCALE) = (int(argv[4]), int(argv[5]))
    DEBUG = int(argv[6])
    GRID = int(argv[7]) if len(argv) > 7 else 0
    if len(argv) > 8 and fun.isInt(argv[8]):
        LABELS = int(argv[8])
        AUTHOR = argv[9] if len(argv) > 9 else None
        MARD = int(argv[10]) if len(argv) > 10 and fun.isInt(argv[10]) else 0
        CLUSTER = int(argv[11]) if len(argv) > 11 and fun.isInt(argv[11]) else 0
    else:
        LABELS = 0
        AUTHOR = argv[8] if len(argv) > 8 else None
        MARD = int(argv[9]) if len(argv) > 9 and fun.isInt(argv[9]) else 0
        CLUSTER = int(argv[10]) if len(argv) > 10 and fun.isInt(argv[10]) else 0
# Internal constants ----------------------------------------------------------
(QNT_MTHD, DWN_MTHD) = (fun.MTHDS[0], fun.MTHDS[1])
###############################################################################
# Folders and Filenames
###############################################################################
(fID, palID) = (PNG_NAME.split('.')[0], PAL_NAME.split('.')[0])
outFolder = path.join(BASE_PATH, fID)
fun.makeFolder(outFolder)
(pthQNT, pthDWN, pthUPS, pthGRD, pthSWT, pthBDS, pthFNL, pthCMP) = [
    path.join(outFolder, i+f'-{palID}-{fID}.png') for i in fun.FIDS
]
###############################################################################
# Load Image
###############################################################################
pth = path.join(BASE_PATH, PNG_NAME)
img = Image.open(pth).convert('RGB')
# Precompute target downscale size (used by clustering seed as well)
dsize = fun.downscaleSize(img, DOWNSCALE)
###############################################################################
# Replace Background Color
###############################################################################
fileMapper = path.join(BASE_PATH, 'CMapper.map')
if exists(fileMapper):
    cMapper = fun.readCMapperFile(fileMapper)
    img = fun.mapColors(img, cMapper)
###############################################################################
# Quantize
#   0: median cut, 1: maximum coverage, 2: fast octree
###############################################################################
mardPalette = None
clusterPalette = None
imgDwnRaw = img.resize(dsize, resample=DWN_MTHD)
if fun.isInt(PAL_NAME):
    imgDwn = fun.quantizeImage(imgDwnRaw, int(PAL_NAME), method=QNT_MTHD, dither=False)
    cpal = None
elif PAL_NAME.lower() in ['mard', 'mard.plt']:
    # Use full MARD palette (215 colors)
    mardPalette = None
    if CLUSTER > 0:
        # Cluster colors from downscaled image (raw)
        usedPalette = fun.getImagePalette(imgDwnRaw.convert('RGB'))
        usedColors = [c[0] for c in usedPalette]
        usedCounts = [c[1] for c in usedPalette]
        # Cluster the used colors (weighted by counts), using existing colors as representatives
        clusteredPalette = fun.clusterColors(usedColors, CLUSTER, usedCounts)
        # Ensure clustered palette stays within MARD colors
        clusterPalette = fun.mapPaletteToNearestMard(clusteredPalette)
        mardPalette = clusterPalette
    else:
        originalPalette = fun.getFullMardPalette()
        mardPalette = originalPalette
    cpal = fun.paletteReshape(mardPalette)
    imgDwn = fun.quantizeImageLab(imgDwnRaw.convert('RGB'), mardPalette)
else:
    palDict = fun.readPaletteFile(path.join(BASE_PATH, PAL_NAME))
    originalPalette = palDict['palette']
    
    # Apply color clustering if enabled
    if CLUSTER > 0:
        # Cluster colors from downscaled image (raw)
        usedPalette = fun.getImagePalette(imgDwnRaw.convert('RGB'))
        usedColors = [c[0] for c in usedPalette]
        usedCounts = [c[1] for c in usedPalette]
        # Cluster the used colors (weighted by counts), using existing colors as representatives
        clusteredPalette = fun.clusterColors(usedColors, CLUSTER, usedCounts)
        clusterPalette = fun.mapPaletteToNearestPalette(clusteredPalette, originalPalette)
        cpal = fun.paletteReshape(clusterPalette)
        imgDwn = fun.quantizeImageLab(imgDwnRaw.convert('RGB'), clusterPalette)
    else:
        cpal = fun.paletteReshape(originalPalette)
        imgDwn = fun.quantizeImageLab(imgDwnRaw.convert('RGB'), originalPalette)
# imgQnt.save(pthQNT)
###############################################################################
# Downscale
#   Image.NEAREST, Image.BILINEAR, Image.BICUBIC, Image.LANCZOS, Image.NEAREST
###############################################################################
# imgDwn already computed above (downscale -> cluster -> quantize)
imgDwn.save(pthDWN)
sleep(fun.SLEEP)
###############################################################################
# Upscale
###############################################################################
upscaleSize = [UPSCALE*i for i in dsize]
imgUps = imgDwn.resize(upscaleSize, Image.NEAREST)
imgUps.save(pthUPS)
sleep(fun.SLEEP)
###############################################################################
# Gridded
###############################################################################
# Use PIL for I/O to support non-ASCII paths on Windows
imgTmp = np.array(Image.open(pthUPS).convert('RGB'))
imgGrd = fun.gridOverlay(imgTmp, UPSCALE, gridColor=(0, 0, 0))
Image.fromarray(imgGrd).save(pthGRD)
sleep(fun.SLEEP)
###############################################################################
# Beads Plot
###############################################################################
# Use PIL for I/O to support non-ASCII paths on Windows
imgTmp = np.array(Image.open(pthDWN).convert('RGB'))[:, :, ::-1]  # RGB -> BGR
(fig, ax) = fun.genBeadsPlot(
    imgTmp, bgColor=fun.BEAD_BKG,
    inRadius=fun.RADII[0], outRadius=fun.RADII[1], imgAlpha=fun.BEAD_ALPHA
)
plt.savefig(
    pthBDS, bbox_inches='tight', pad_inches=0, dpi=100,
    facecolor=[i/255 for i in ImageColor.getcolor(fun.BEAD_BKG, "RGB")]
)
plt.close('all')
sleep(fun.SLEEP)
###############################################################################
# Swatch
###############################################################################
(imgBDS, imgTmp) = (
    Image.open(pthBDS).convert('RGB'),
    imgDwn.convert('RGB') if imgDwn.mode != 'RGB' else imgDwn.copy()
)
swatch = fun.getImagePalette(imgTmp)
imgSwt = fun.genColorCounts(
    swatch, 500, imgBDS.size[1], imgDwn.size, authorLabel=AUTHOR, useMard=(MARD == 1)
)
plt.savefig(
    pthSWT, bbox_inches='tight', pad_inches=0,
    facecolor=[i/255 for i in ImageColor.getcolor(fun.BEAD_BKG, "RGB")]
)
plt.close('all')
sleep(fun.SLEEP)
###############################################################################
# Final Figure
###############################################################################
(imgBDS, imgSWT) = (
    Image.open(pthBDS).convert('RGB'),
    Image.open(pthSWT).convert('RGB')
)
if GRID:
    imgBDS = fun.addGridByCount(imgBDS, dsize[0], dsize[1], color=(200, 200, 200), width=1)
if LABELS:
    baseHeight = imgBDS.height
    imgBDS = fun.addGridLabelsWithMargin(imgBDS, dsize[0], dsize[1], color=(120, 120, 120))
    marginH = max(0, (imgBDS.height - baseHeight) // 2)
    if imgSWT.height != imgBDS.height:
        bkg = ImageColor.getcolor(fun.BEAD_BKG, "RGB")
        padded = Image.new('RGB', (imgSWT.width, imgBDS.height), color=bkg)
        padded.paste(imgSWT, (0, marginH))
        imgSWT = padded
ccat = fun.hConcat(imgBDS, imgSWT)
ccat.save(pthFNL)
sleep(fun.SLEEP)
###############################################################################
# Comparison Grid
###############################################################################
pthOriginal = path.join(BASE_PATH, PNG_NAME)
fun.createComparisonGrid(pthOriginal, pthUPS, pthGRD, pthFNL, pthCMP)
sleep(fun.SLEEP)
###############################################################################
# Delete files
###############################################################################
banList = (pthDWN, pthUPS, pthGRD, pthSWT, pthBDS, pthFNL, pthCMP)
if not DEBUG:
    for tFile in banList[:-1]:
        remove(tFile)