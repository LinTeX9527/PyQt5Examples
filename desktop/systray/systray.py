#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
comment on 2019-01-07 22:04:49

reviewer: lintex9527@yeah.net
"""

#############################################################################
##
## Copyright (C) 2013 Riverbank Computing Limited.
## Copyright (C) 2010 Nokia Corporation and/or its subsidiary(-ies).
## All rights reserved.
##
## This file is part of the examples of PyQt.
##
## $QT_BEGIN_LICENSE:BSD$
## You may use this file under the terms of the BSD license as follows:
##
## "Redistribution and use in source and binary forms, with or without
## modification, are permitted provided that the following conditions are
## met:
##   * Redistributions of source code must retain the above copyright
##     notice, this list of conditions and the following disclaimer.
##   * Redistributions in binary form must reproduce the above copyright
##     notice, this list of conditions and the following disclaimer in
##     the documentation and/or other materials provided with the
##     distribution.
##   * Neither the name of Nokia Corporation and its Subsidiary(-ies) nor
##     the names of its contributors may be used to endorse or promote
##     products derived from this software without specific prior written
##     permission.
##
## THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
## "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
## LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
## A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
## OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
## SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
## LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
## DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
## THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
## (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
## OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE."
## $QT_END_LICENSE$
##
#############################################################################


from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QAction, QApplication, QCheckBox, QComboBox,
        QDialog, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit,
        QMessageBox, QMenu, QPushButton, QSpinBox, QStyle, QSystemTrayIcon,
        QTextEdit, QVBoxLayout)

import systray_rc


class Window(QDialog):
    """
    窗体继承自QDialog，可以当做普通的widget使用
    """
    def __init__(self):
        super(Window, self).__init__()

        self.createIconGroupBox()
        self.createMessageGroupBox()
        # 微调UI元素，同一列的最短的标签它的宽度设置成某一个最长部件的推荐的宽度
        self.iconLabel.setMinimumWidth(self.durationLabel.sizeHint().width())

        self.createActions()
        self.createTrayIcon()

        # 绑定信号和槽函数
        self.showMessageButton.clicked.connect(self.showMessage)
        self.showIconCheckBox.toggled.connect(self.trayIcon.setVisible)
        self.iconComboBox.currentIndexChanged.connect(self.setIcon)
        self.trayIcon.messageClicked.connect(self.messageClicked)
        self.trayIcon.activated.connect(self.iconActivated)

        # 窗体的主布局是垂直BOX布局
        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.iconGroupBox)
        mainLayout.addWidget(self.messageGroupBox)
        self.setLayout(mainLayout)

        self.iconComboBox.setCurrentIndex(1)
        self.trayIcon.show()

        self.setWindowTitle("Systray")
        self.resize(400, 300)

    def setVisible(self, visible):
        """
        槽函数，QCheckBox 的选中与否来设定系统托盘是否可见
        """
        self.minimizeAction.setEnabled(visible)
        self.maximizeAction.setEnabled(not self.isMaximized())
        self.restoreAction.setEnabled(self.isMaximized() or not visible)
        # FIXME: 疑惑，这里不应该是窗体主界面可见不可见吗？
        super(Window, self).setVisible(visible)

    def closeEvent(self, event):
        """
        如果系统托盘是可见的，那么不能直接关闭窗口，只是隐藏当前窗口，需要从系统托盘关闭应用
        """
        if self.trayIcon.isVisible():
            QMessageBox.information(self, "Systray",
                    "The program will keep running in the system tray. To "
                    "terminate the program, choose <b>Quit</b> in the "
                    "context menu of the system tray entry.")
            self.hide()
            event.ignore()

    def setIcon(self, index):
        """
        通过QComboBox获取一个QIcon，然后同时更新主窗口的图标和托盘的图片表
        :param index: 组合列表框的索引号
        :return:
        """
        # NOTE: 注意这里通过 QComboBox 可以通过索引号返回一个icon和文字
        icon = self.iconComboBox.itemIcon(index)
        self.trayIcon.setIcon(icon)
        self.setWindowIcon(icon)

        self.trayIcon.setToolTip(self.iconComboBox.itemText(index))

    def iconActivated(self, reason):
        """
        系统托盘被单击、双击、鼠标中键单击的处理
        """
        if reason in (QSystemTrayIcon.Trigger, QSystemTrayIcon.DoubleClick):
            self.iconComboBox.setCurrentIndex(
                    (self.iconComboBox.currentIndex() + 1)
                    % self.iconComboBox.count())
        elif reason == QSystemTrayIcon.MiddleClick:
            self.showMessage()

    def showMessage(self):
        """
        系统托盘弹出消息
        """
        icon = QSystemTrayIcon.MessageIcon(
                self.typeComboBox.itemData(self.typeComboBox.currentIndex()))

        # NOTE: 这里的4个参数分别是title, text, icon, duration
        self.trayIcon.showMessage(self.titleEdit.text(),
                self.bodyEdit.toPlainText(), icon,
                self.durationSpinBox.value() * 1000)

    def messageClicked(self):
        """
        槽函数，托盘消息被单击，这个事件有这个函数来处理
        """
        QMessageBox.information(None, "Systray",
                "Sorry, I already gave what help I could.\nMaybe you should "
                "try asking a human?")

    def createIconGroupBox(self):
        """
        设置系统托盘相关的UI元素，只涉及布局
        """
        self.iconGroupBox = QGroupBox("Tray Icon")

        # 标签，提示用户后面的组合列表框的作用
        self.iconLabel = QLabel("Icon:")

        # 组合列表框中填充几个item，每一个设置不同的系统托盘图标
        self.iconComboBox = QComboBox()
        # NOTE: 注意这里加载图片资源的用法，用到 qt resource compiler
        self.iconComboBox.addItem(QIcon(':/images/bad.png'), "Bad")
        self.iconComboBox.addItem(QIcon(':/images/heart.png'), "Heart")
        self.iconComboBox.addItem(QIcon(':/images/trash.png'), "Trash")

        self.showIconCheckBox = QCheckBox("Show icon")
        self.showIconCheckBox.setChecked(True)

        iconLayout = QHBoxLayout()
        iconLayout.addWidget(self.iconLabel)
        iconLayout.addWidget(self.iconComboBox)
        iconLayout.addStretch()
        iconLayout.addWidget(self.showIconCheckBox)
        # NOTE: 明白了QGroupBox也是一个QtWidget，也需要设置自己的布局管理器
        self.iconGroupBox.setLayout(iconLayout)

    def createMessageGroupBox(self):
        """
        设置系统弹窗提示
        """
        self.messageGroupBox = QGroupBox("Balloon Message")

        typeLabel = QLabel("Type:")

        self.typeComboBox = QComboBox()
        self.typeComboBox.addItem("None", QSystemTrayIcon.NoIcon)
        self.typeComboBox.addItem(self.style().standardIcon(
                QStyle.SP_MessageBoxInformation), "Information",
                QSystemTrayIcon.Information)
        self.typeComboBox.addItem(self.style().standardIcon(
                QStyle.SP_MessageBoxWarning), "Warning",
                QSystemTrayIcon.Warning)
        self.typeComboBox.addItem(self.style().standardIcon(
                QStyle.SP_MessageBoxCritical), "Critical",
                QSystemTrayIcon.Critical)
        self.typeComboBox.setCurrentIndex(1)

        self.durationLabel = QLabel("Duration:")

        # QSpinBox() 专门用来选择整数
        self.durationSpinBox = QSpinBox()
        self.durationSpinBox.setRange(5, 60)
        # NOTE: 有设置后缀的就有设置前缀的
        self.durationSpinBox.setSuffix(" s")
        self.durationSpinBox.setValue(15)

        durationWarningLabel = QLabel("(some systems might ignore this hint)")
        # NOTE: 设置标签的缩进，以像素为单位
        durationWarningLabel.setIndent(10)

        titleLabel = QLabel("Title:")

        self.titleEdit = QLineEdit("Cannot connect to network")

        bodyLabel = QLabel("Body:")

        self.bodyEdit = QTextEdit()
        self.bodyEdit.setPlainText("Don't believe me. Honestly, I don't have "
                "a clue.\nClick this balloon for details.")

        self.showMessageButton = QPushButton("Show Message")
        self.showMessageButton.setDefault(True)

        messageLayout = QGridLayout()
        messageLayout.addWidget(typeLabel, 0, 0)
        messageLayout.addWidget(self.typeComboBox, 0, 1, 1, 2)
        messageLayout.addWidget(self.durationLabel, 1, 0)
        messageLayout.addWidget(self.durationSpinBox, 1, 1)
        messageLayout.addWidget(durationWarningLabel, 1, 2, 1, 3)
        messageLayout.addWidget(titleLabel, 2, 0)
        messageLayout.addWidget(self.titleEdit, 2, 1, 1, 4)
        messageLayout.addWidget(bodyLabel, 3, 0)
        messageLayout.addWidget(self.bodyEdit, 3, 1, 2, 4)
        messageLayout.addWidget(self.showMessageButton, 5, 4)
        # NOTE: 设置第3列伸缩因子为1
        messageLayout.setColumnStretch(3, 1)
        # NOTE: 设置第4行伸缩因子为1
        messageLayout.setRowStretch(4, 1)
        # NOTE: 需要记住QGroupBox是一个QtWidget，必须要设置一个布局管理器
        self.messageGroupBox.setLayout(messageLayout)

    def createActions(self):
        """
        为系统托盘创建action，分别是最小化、最大化、普通显示以及退出应用
        """
        self.minimizeAction = QAction("Mi&nimize", self, triggered=self.hide)
        self.maximizeAction = QAction("Ma&ximize", self,
                triggered=self.showMaximized)
        self.restoreAction = QAction("&Restore", self,
                triggered=self.showNormal)
        self.quitAction = QAction("&Quit", self,
                triggered=QApplication.instance().quit)

    def createTrayIcon(self):
        # 创建菜单
        self.trayIconMenu = QMenu(self)
        # 菜单中添加已经创建的actions
        self.trayIconMenu.addAction(self.minimizeAction)
        self.trayIconMenu.addAction(self.maximizeAction)
        self.trayIconMenu.addAction(self.restoreAction)
        self.trayIconMenu.addSeparator()
        self.trayIconMenu.addAction(self.quitAction)

        # 创建系统托盘，它是一个窗体，需要给它添加菜单
        self.trayIcon = QSystemTrayIcon(self)
        # NOTE: 系统托盘创建的是上下文菜单
        self.trayIcon.setContextMenu(self.trayIconMenu)


if __name__ == '__main__':

    # NOTE: 原来 import 可以放在程序的任何地方
    import sys

    app = QApplication(sys.argv)

    # 首先检查系统是否允许使用 SystemTray
    if not QSystemTrayIcon.isSystemTrayAvailable():
        QMessageBox.critical(None, "Systray",
                "I couldn't detect any system tray on this system.")
        sys.exit(1)

    # NOTE: 最后一个主窗口（没有父对象）关闭时退出整个应用为假，即不退出。但是在win10上似乎不起作用
    QApplication.setQuitOnLastWindowClosed(False)
    # QApplication.setQuitOnLastWindowClosed(True)

    window = Window()
    window.show()
    sys.exit(app.exec_())
