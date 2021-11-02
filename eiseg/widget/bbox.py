from qtpy import QtWidgets, QtGui, QtCore
from qtpy.QtCore import Qt


# TODO: code clean up
# Note, bbox annotation is more convenient than the default boundingBox generated by QGrpaphicItem
class BBoxAnnotation(QtWidgets.QGraphicsPathItem):
    def __init__(
        self,
        labelIndex,
        polyline,
        borderColor=[0, 0, 255],
        cocoIndex=None,
        parent=None,
    ):
        super(BBoxAnnotation, self).__init__(parent)
        self.polyline = polyline
        self.corner_points = []
        self.upper_right = QtCore.QPointF()
        self.bottom_left = QtCore.QPointF()
        self.w = -1.0
        self.h = -1.0

        self.parent = parent
        self.is_added = False
        if self.parent is not None:
            self.is_added = True
        self.labelIndex = labelIndex
        self.coco_id = cocoIndex
        self.bbox_hovering = True

        # set rendering attributes
        self.setZValue(10)

        # b = borderColor
        # self.borderColor = QtGui.QColor(b[0], b[1], b[2])
        self.borderColor = QtGui.QColor(128, 128, 128)
        self.borderColor.setAlphaF(0.8)
        pen = QtGui.QPen(self.borderColor, 1.2)
        pen.setStyle(Qt.DashDotLine)
        self.setPen(pen)

        self.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable, False)
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable, False)
        self.setFlag(QtWidgets.QGraphicsItem.ItemSendsGeometryChanges, True)
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsFocusable, False)
        self.setAcceptHoverEvents(False)
        # self.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))

    @property
    def scnenePoints(self):
        # return 4 corner points
        raise Exception("Not Implemented Yet!")

    def setAnning(self, isAnning=True):
        raise Exception("Not Implemented Yet!")

    def remove(self):
        raise Exception("Not Implemented Yet!")

    # ===== mouse evts

    # def hoverEnterEvent(self, ev):
    #     if self.parent is not None and self.parent.polygon_hovering:
    #         return
    #     self.bbox_hovering = True
    #     self.setBrush(self.borderColor)
    #     super(BBoxAnnotation, self).hoverEnterEvent(ev)

    # def hoverLeaveEvent(self, ev):
    #     self.bbox_hovering = False
    #     if not self.hasFocus():
    #         self.setBrush(QtGui.QBrush(QtCore.Qt.NoBrush))
    #     super(BBoxAnnotation, self).hoverLeaveEvent(ev)

    # def focusInEvent(self, ev):
    #     if self.parent is not None and self.parent.hasFocus():
    #         return
    #     # self.setBrush(self.borderColor)

    # def focusOutEvent(self, ev):
    #     if not self.bbox_hovering:
    #         self.setBrush(QtGui.QBrush(QtCore.Qt.NoBrush))

    # ===== generate geometry info

    def create_corners(self):
        bbox_rect_geo = self.polyline.boundingRect()
        self.bottom_left = bbox_rect_geo.bottomLeft()
        self.upper_right = bbox_rect_geo.topRight()
        self.corner_points.clear()
        self.corner_points.extend(
            [
                self.bottom_left,
                bbox_rect_geo.topLeft(),
                self.upper_right,
                bbox_rect_geo.bottomRight(),
            ]
        )
        self.w = self.corner_points[3].x() - self.corner_points[1].x()
        self.h = self.corner_points[3].y() - self.corner_points[1].y()

        if self.corner_points[1].x() > 512 or self.corner_points[1].x() + self.w > 512:
            pass
        if self.corner_points[1].y() > 512 or self.corner_points[1].y() + self.h > 512:
            pass
        return self.corner_points

    def create_lines(self):
        pass

    # ===== graphic interface to update in scene tree

    def update(self):
        l = len(self.polyline.points)
        # print("up L:", l, " is_added:", self.is_added)
        if l < 3:
            if self.is_added:
                self.remove_from_scene()
        else:  # 大于三个点就可以更新，小于三个点删除多边形
            if self.is_added:
                self.add_to_scene()
            else:
                path_geo = QtGui.QPainterPath()
                self.create_corners()
                path_geo.moveTo(self.corner_points[0])
                for i in range(4):
                    path_geo.lineTo(self.corner_points[(i + 1) % 4])
                self.setPath(QtGui.QPainterPath(path_geo))
                pass
            pass
        pass

    def add_to_scene(self):
        # self.parentItem().scene().addItem(self)
        self.setParentItem(self.parent)
        self.is_added = True

    def remove_from_scene(self):
        # self.parentItem().scene().removeItem(self)
        self.setParentItem(None)
        self.is_added = False

    # ===== annotation info

    # @return : [x, y, w, h]
    def to_array(self):
        np_array = [
            self._round(self.corner_points[1].x()),
            self._round(self.corner_points[1].y()),  # topLeft
            self._round(self.w),
            self._round(self.h),
        ]
        return np_array

    def _round(self, number, ind=0):
        nint, ndec = str(number).split(".")
        res = float(nint + "." + ndec[:ind])
        if res <= 0:
            res = 0.0
        return res

    def __del__(self):
        self.corner_points.clear()
