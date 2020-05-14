from qgis.core import QgsStyle, QgsProject, QgsSymbol, QgsRendererRange, QgsGraduatedSymbolRenderer
from PyQt5.QtGui import QColor

import math

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

def style(fld, colorName = 'PuRd', interval = 5):
    myStyle = QgsStyle().defaultStyle()
    ramp = myStyle.colorRamp(colorName)
    c1 = ramp.color1()
    c2 = ramp.color2()
    actualayers = getCRPlayers(fld)
    lower = 0.0
    upper = -1.0
    for layer in actualayers:
        fld_index = layer.fields().lookupField(fld)
        lmax = layer.maximumValue(fld_index)
        if lmax > upper:
            upper = lmax
    colors = []
    max_erosion = int(round_up(upper))
    max_erosion += interval
    t_list = []
    init = 0
    number_classes = range(0, max_erosion, interval)
    nn = max_erosion/interval
    for i in number_classes:
        t_list.append(init)
        init += 1./(nn-1)
    for i in t_list:
        colors.append(linear_color_interpolation(c1, c2, i))
    for layer in actualayers:
        range_list = []
        ll = lower
        for c in colors:
            cat = [ll, ll + interval, c.name()]
            sym = QgsSymbol.defaultSymbol(layer.geometryType())
            sym.setColor(c)
            sym.symbolLayer(0).setStrokeStyle(Qt.PenStyle(Qt.NoPen))
            rng = QgsRendererRange(cat[0], cat[1], sym, '{0:.1f}-{1:.1f}'.format(cat[0], cat[1]))
            range_list.append(rng)
            ll = ll + interval
        renderer = QgsGraduatedSymbolRenderer(fld, range_list)
        renderer.setMode(QgsGraduatedSymbolRenderer.Custom)
        layer.setRenderer(renderer)
        layer.triggerRepaint()


def style_na(fld):
    actualayers = getCRPlayers(fld)
    c = '#20a802'
    lmin = -1
    lmax = 0
    for layer in actualayers:
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
