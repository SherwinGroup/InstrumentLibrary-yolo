from PyQt5 import QtCore, QtWidgets
import time
import numpy as np
import pyqtgraph as pg


class DateAxis(pg.AxisItem):
    def tickStrings(self, values, scale, spacing):
        strns = []
        for x in values:
            try:
                strns.append(time.strftime("%X", time.localtime(x)))
            except (ValueError, OSError):  ## Windows can't handle dates before 1970
                strns.append('')
        return strns

    def drawPicture(self, p, axisSpec, tickSpecs, textSpecs):
        """

        :param p:
        :type p: QtGui.QPainter
        :param axisSpec:
        :param tickSpecs:
        :param textSpecs:
        :return:
        """

        p.setRenderHint(p.Antialiasing, False)
        p.setRenderHint(p.TextAntialiasing, True)

        ## draw long line along axis
        pen, p1, p2 = axisSpec
        p.setPen(pen)
        p.drawLine(p1, p2)
        p.translate(0.5,0)  ## resolves some damn pixel ambiguity

        ## draw ticks
        for pen, p1, p2 in tickSpecs:
            p.setPen(pen)
            p.drawLine(p1, p2)

        ## Draw all text
        if self.tickFont is not None:
            p.setFont(self.tickFont)
        p.setPen(self.pen())
        ## TODO: Figure this out, I want this text rotate, ffs.
        for rect, flags, text in textSpecs:
            # p.rotate(-2)
            p.save()
            QtCore.QRectF().center()
            p.translate(rect.center())
            p.rotate(40)
            # height = rect.width()*0.8
            p.translate(-rect.center())
            p.drawText(rect, flags, text)
            # p.rotate(2)
            # p.drawRect(rect)
            p.restore()
        # self.setStyle(tickTextHeight=int(height)*5)

    def tickSpacing(self, minVal, maxVal, size):
        """
        I delcare that my desired possible spacings are every
        1s, 5s, 10s, 15s, 30s,
        1m, 5m, 10m, 15m, 30m,
        1h, 5h, 10h
        And hopefully no further than that?
        """
        superRet = super(DateAxis, self).tickSpacing(minVal, maxVal, size)
        # return ret
        # Todo set spacing to be reasonable
        dif = abs(maxVal - minVal)
        spacings = np.array([1, 5, 10, 15, 30,
                             1*60, 5*60, 10*60, 15*60, 30*60,
                             1*60*60, 5*60*60, 10*60*60])
        numTicks = (maxVal - minVal)/spacings

        # I really want to know where this comes from,
        # I just nabbed it from Luke's code
        optimalTickCount = max(2., np.log(size))

        bestValidx = np.abs(numTicks-optimalTickCount).argmin()
        desiredTicks = numTicks[bestValidx]
        if desiredTicks > 20:
            # Too many ticks to plot, would cause the render engine to break
            # Cutoff is arbitrary
            # todo: set it to a density (px/spacing) to handle it better
            return superRet
        bestVal = spacings[bestValidx]
        # todo: set better minor tick spacings
        ret =  [
            (bestVal, 0),
            (bestVal/5., 0),
            (bestVal/10., 0)
        ]
        return ret

        return super(DateAxis, self).tickSpacing(minVal, maxVal, size)
