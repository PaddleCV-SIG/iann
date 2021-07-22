import os.path as osp
import math
from functools import partial

from PyQt5.QtCore import QPoint

from qtpy import QtCore, QtWidgets
from qtpy.QtWidgets import (
    QWidget,
    QLabel,
    QPushButton,
    QGridLayout,
    QKeySequenceEdit,
    QMessageBox,
)
from qtpy.QtGui import QIcon
from qtpy import QtCore
from qtpy.QtCore import Qt

from util import save_configs


class RecordShortcutWindow(QKeySequenceEdit):
    def __init__(self, finishCallback, location):
        super().__init__()
        self.finishCallback = finishCallback
        # 隐藏界面
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.move(location)
        self.show()
        self.editingFinished.connect(lambda: finishCallback(self.keySequence()))

    def keyReleaseEvent(self, ev):
        self.finishCallback(self.keySequence())


class ShortcutWindow(QWidget):
    def __init__(self, actions, pjpath, trans):
        super().__init__()
        self.trans = trans
        self.setWindowTitle(trans.put("编辑快捷键"))
        self.setWindowIcon(QIcon(osp.join(pjpath, "resource/Shortcut.png")))
        # self.setFixedSize(self.width(), self.height()); 
        self.actions = actions
        self.recorder = None
        self.initUI()

    def initUI(self):
        grid = QGridLayout()
        self.setLayout(grid)

        actions = self.actions
        for idx, action in enumerate(actions):
            grid.addWidget(QLabel(action.iconText()[1:]), idx // 2, idx % 2 * 2)
            shortcut = action.shortcut().toString()
            if len(shortcut) == 0:
                shortcut = self.trans.put("无")
            button = QPushButton(shortcut)
            button.setFixedWidth(150)
            button.setFixedHeight(30)
            button.clicked.connect(partial(self.recordShortcut, action))
            grid.addWidget(
                button,
                idx // 2,
                idx % 2 * 2 + 1,
            )

    def refreshUi(self):
        actions = self.actions
        for idx, action in enumerate(actions):
            shortcut = action.shortcut().toString()
            if len(shortcut) == 0:
                shortcut = self.trans.put("无")
            self.layout().itemAtPosition(
                idx // 2,
                idx % 2 * 2 + 1,
            ).widget().setText(shortcut)

    def recordShortcut(self, action):
        # 打开快捷键设置的窗口时，如果之前的还在就先关闭
        if self.recorder is not None:
            self.recorder.close()
        rect = self.geometry()
        x = rect.x()
        y = rect.y() + rect.height()
        self.recorder = RecordShortcutWindow(self.setShortcut, QPoint(x, y))
        self.currentAction = action

    def setShortcut(self, key):
        print("setting shortcut", key.toString())
        self.recorder.close()

        for a in self.actions:
            if a.shortcut() == key:
                key = key.toString()
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Warning)
                msg.setWindowTitle(key + " " + self.trans.put("快捷键冲突"))
                # TODO：动态翻译问题待解决
                msg.setText(
                    key + " " +  self.trans.put("快捷键已被") + " " + a.data() + \
                    " " + self.trans.put("使用，请设置其他快捷键或先修改") + " " + \
                    a.data() + " " +  self.trans.put("的快捷键")
                )
                msg.setStandardButtons(QMessageBox.Ok)
                msg.exec_()
                return
        key = "" if key.toString() == "Esc" else key  # ESC不设置快捷键
        self.currentAction.setShortcut(key)
        self.refreshUi()
        save_configs(None, None, self.actions)

    # 快捷键设置跟随移动
    def moveEvent(self, event):
        p = self.geometry()
        x = p.x()
        y = p.y() + p.height()
        if self.recorder is not None:
            self.recorder.move(x, y)

    def closeEvent(self, event):
        # 关闭时也退出快捷键设置
        if self.recorder is not None:
            self.recorder.close()