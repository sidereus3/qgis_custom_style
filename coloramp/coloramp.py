from qgis.core import QgsStyle, QgsProject, QgsSymbol, QgsRendererRange, QgsGraduatedSymbolRenderer
from PyQt5.QtGui import QColor

import math
import threading
import queue
import time

def linear_color_interpolation(c1, c2, t):
    r = int(c1.red() + (c2.red() - c1.red()) * t)
    g = int(c1.green() + (c2.green() - c1.green()) * t)
    b = int(c1.blue() + (c2.blue() - c1.blue()) * t)
    return QColor(r, g, b)

def round_up(n, decimals=0):
    multiplier = 10 ** decimals
    return math.ceil(n * multiplier) / multiplier

def getCRPlayers(fld):
    layers = QgsProject().instance().mapLayers()
    actualayers = []
    for key, layer in layers.items():
        fld_index = layer.fields().lookupField(fld)
        if fld_index >= 0:
            actualayers.append(layer)
    return actualayers

def getMaxParallelVal(layers, fld):

    q = queue.Queue()
    maxq = []

    def worker():
        while True:
            layer = q.get()
            fld_index = layer.fields().lookupField(fld)
            lmax = layer.maximumValue(fld_index)
            maxq.append(lmax)
            q.task_done()

    threading.Thread(target=worker, daemon=True).start()

    for layer in layers:
        q.put(layer)

    q.join()
    return max(maxq)

def getMaxVal(layers, fld, multi):
    if multi:
        return getMaxParallelVal(layers, fld)
    else:
        upper = -1.0
        for layer in layers:
            fld_index = layer.fields().lookupField(fld)
            lmax = layer.maximumValue(fld_index)
            if lmax > upper:
                upper = lmax
        return upper

def getIntervalInterpolation(nn):
    t_list = []
    interp = 0
    for i in range(0, nn):
        t_list.append(interp)
        interp += 1./(nn-1)
    return t_list

def getInterpolatedColors(nn, colorName):
    myStyle = QgsStyle().defaultStyle()
    ramp = myStyle.colorRamp(colorName)
    c1 = ramp.color1()
    c2 = ramp.color2()
    t_list = getIntervalInterpolation(nn)
    colors = []
    for i in t_list:
        colors.append(linear_color_interpolation(c1, c2, i))
    return colors

def renderingUpdate(layers, colors, interval, fld):
    for layer in layers:
        range_list = []
        lower = 0.0
        for c in colors:
            cat = [lower, lower + interval, c.name()]
            sym = QgsSymbol.defaultSymbol(layer.geometryType())
            sym.setColor(c)
            sym.symbolLayer(0).setStrokeStyle(Qt.PenStyle(Qt.NoPen))
            rng = QgsRendererRange(cat[0], cat[1], sym, '{0:.1f}-{1:.1f}'.format(cat[0], cat[1]))
            range_list.append(rng)
            lower = lower + interval
        renderer = QgsGraduatedSymbolRenderer(fld, range_list)
        renderer.setMode(QgsGraduatedSymbolRenderer.Custom)
        layer.setRenderer(renderer)
        layer.triggerRepaint()

def style(fld, multi, colorName = 'PuRd', interval = 5):

    layers = getCRPlayers(fld)
    t = time.time()
    upper = getMaxVal(layers, fld, multi)
    elapsed = time.time() - t
    print(elapsed)
    print(upper)

    nn = int(round_up(upper/interval))
    print(nn)
    colors = getInterpolatedColors(nn, colorName)
    renderingUpdate(layers, colors, interval, fld)

def style_na(fld):
    layers = getCRPlayers(fld)
    c = '#20a802'
    colors = []
    colors.append(QColor(c))
    lmin = -1
    lmax = 0

    for layer in layers:
        range_list = []
        cat = [lmin, lmax, c]
        sym = QgsSymbol.defaultSymbol(layer.geometryType())
        sym.setColor(QColor(c))
        sym.symbolLayer(0).setStrokeStyle(Qt.PenStyle(Qt.NoPen))
        rng = QgsRendererRange(cat[0], cat[1], sym, '{0:.1f}-{1:.1f}'.format(cat[0], cat[1]))
        range_list.append(rng)
        renderer = QgsGraduatedSymbolRenderer(fld, range_list)
        renderer.setMode(QgsGraduatedSymbolRenderer.Custom)
        layer.setRenderer(renderer)
        layer.triggerRepaint()
