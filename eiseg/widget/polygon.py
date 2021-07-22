from qtpy import QtWidgets, QtGui, QtCore

from . import GripItem, LineItem


class PolygonAnnotation(QtWidgets.QGraphicsPolygonItem):
    def __init__(
        self,
        index,
        insideColor=[255, 0, 0],
        borderColor=[0, 255, 0],
        opacity=0.5,
        parent=None,
    ):
        super(PolygonAnnotation, self).__init__(parent)
        self.points = []
        self.m_items = []
        self.m_lines = []

        self.labelIndex = index
        self.item_hovering = False
        self.polygon_hovering = False
        self.line_hovering = False
        self.noMove = False

        self.setZValue(10)
        i = insideColor
        self.insideColor = QtGui.QColor(i[0], i[1], i[2])
        self.insideColor.setAlphaF(opacity)
        self.opacity = opacity
        b = borderColor
        self.borderColor = QtGui.QColor(b[0], b[1], b[2])
        self.borderColor.setAlphaF(0.8)
        self.setPen(QtGui.QPen(self.borderColor))
        self.setAcceptHoverEvents(True)

        self.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QtWidgets.QGraphicsItem.ItemSendsGeometryChanges, True)
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsFocusable, True)

        self.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))

    def addPointMiddle(self, lineIdx, point):
        gripItem = GripItem(self, lineIdx + 1, self.borderColor)
        gripItem.setEnabled(False)
        gripItem.setPos(point)
        self.scene().addItem(gripItem)
        gripItem.updateSize()
        gripItem.setEnabled(True)
        for grip in self.m_items[lineIdx + 1 :]:
            grip.m_index += 1
        self.m_items.insert(lineIdx + 1, gripItem)
        self.points.insert(lineIdx + 1, self.mapFromScene(point))
        self.setPolygon(QtGui.QPolygonF(self.points))
        for line in self.m_lines[lineIdx + 1 :]:
            line.idx += 1
        line = QtCore.QLineF(
            self.mapToScene(self.points[lineIdx]),
            point
            # self.mapToScene(self.points[lineIdx + 1]),
        )
        self.m_lines[lineIdx].setLine(line)
        lineItem = LineItem(self, lineIdx + 1, self.borderColor)
        line = QtCore.QLineF(
            # self.mapToScene(self.points[lineIdx + 1]),
            point,
            self.mapToScene(self.points[(lineIdx + 2) % len(self)]),
        )
        lineItem.setLine(line)
        self.m_lines.insert(lineIdx + 1, lineItem)
        self.scene().addItem(lineItem)

    def addPointLast(self, p):
        grip = GripItem(self, len(self), self.borderColor)
        self.scene().addItem(grip)
        self.m_items.append(grip)
        grip.updateSize()
        grip.setPos(p)
        if len(self) == 0:
            line = LineItem(self, len(self), self.borderColor)
            self.scene().addItem(line)
            self.m_lines.append(line)
            line.setLine(QtCore.QLineF(p, p))
        else:
            self.m_lines[-1].setLine(QtCore.QLineF(self.points[-1], p))
            line = LineItem(self, len(self), self.borderColor)
            self.scene().addItem(line)
            self.m_lines.append(line)
            line.setLine(QtCore.QLineF(p, self.points[0]))

        self.points.append(p)
        self.setPolygon(QtGui.QPolygonF(self.points))

    def remove(self):
        for grip in self.m_items:
            self.scene().removeItem(grip)
        for line in self.m_lines:
            self.scene().removeItem(line)
        while len(self.m_items) != 0:
            self.m_items.pop()
        while len(self.m_lines) != 0:
            self.m_lines.pop()
        self.scene().polygon_items.remove(self)
        self.scene().removeItem(self)
        del self

    def removeFocusPoint(self):
        focusIdx = None
        for idx, item in enumerate(self.m_items):
            if item.hasFocus():
                focusIdx = idx
                break
        print("del", focusIdx)
        if focusIdx is not None:
            if len(self) <= 3:
                self.remove()
                return
            del self.points[focusIdx]
            self.setPolygon(QtGui.QPolygonF(self.points))
            self.scene().removeItem(self.m_items[focusIdx])
            del self.m_items[focusIdx]
            for grip in self.m_items[focusIdx:]:
                grip.m_index -= 1

            self.scene().removeItem(self.m_lines[focusIdx])
            del self.m_lines[focusIdx]
            line = QtCore.QLineF(
                self.mapToScene(self.points[(focusIdx - 1) % len(self)]),
                self.mapToScene(self.points[focusIdx % len(self)]),
            )
            # print((focusIdx - 1) % len(self), len(self.m_lines), len(self))
            self.m_lines[(focusIdx - 1) % len(self)].setLine(line)
            for line in self.m_lines[focusIdx:]:
                line.idx -= 1

    def removeLastPoint(self):
        # TODO: 创建的时候用到，需要删line
        if len(self.points) == 0:
            self.points.pop()
            self.setPolygon(QtGui.QPolygonF(self.points))
            it = self.m_items.pop()
            self.scene().removeItem(it)
            del it

    def movePoint(self, i, p):
        # print("Move point", i, p)
        if 0 <= i < len(self.points):
            p = self.mapFromScene(p)
            self.points[i] = p
            self.setPolygon(QtGui.QPolygonF(self.points))
            self.moveLine(i)

    def moveLine(self, i):
        # print("Moving line: ", i, self.noMove)
        if self.noMove:
            return
        points = self.points
        # line[i]
        line = QtCore.QLineF(
            self.mapToScene(points[i]), self.mapToScene(points[(i + 1) % len(self)])
        )
        self.m_lines[i].setLine(line)
        # line[i-1]
        line = QtCore.QLineF(
            self.mapToScene(points[(i - 1) % len(self)]), self.mapToScene(points[i])
        )
        # print((i - 1) % len(self), len(self.m_lines), len(self))
        self.m_lines[(i - 1) % len(self)].setLine(line)

    def move_item(self, i, pos):
        if 0 <= i < len(self.m_items):
            item = self.m_items[i]
            item.setEnabled(False)
            item.setPos(pos)
            item.setEnabled(True)
            self.moveLine(i)

    def itemChange(self, change, value):
        if change == QtWidgets.QGraphicsItem.ItemPositionHasChanged:
            for i, point in enumerate(self.points):
                self.move_item(i, self.mapToScene(point))
        return super(PolygonAnnotation, self).itemChange(change, value)

    def hoverEnterEvent(self, ev):
        self.polygon_hovering = True
        self.setBrush(self.insideColor)
        super(PolygonAnnotation, self).hoverEnterEvent(ev)

    def hoverLeaveEvent(self, ev):
        self.polygon_hovering = False
        if not self.hasFocus():
            self.setBrush(QtGui.QBrush(QtCore.Qt.NoBrush))
        super(PolygonAnnotation, self).hoverLeaveEvent(ev)

    def focusInEvent(self, ev):
        self.setBrush(self.insideColor)

    def focusOutEvent(self, ev):
        if not self.polygon_hovering:
            self.setBrush(QtGui.QBrush(QtCore.Qt.NoBrush))

    def setOpacity(self, opacity):
        self.opacity = opacity
        self.insideColor.setAlphaF(opacity)

    def setColor(self, c):
        self.insideColor = QtGui.QColor(c[0], c[1], c[2])
        self.insideColor.setAlphaF(self.opacity)

    def __len__(self):
        return len(self.points)
