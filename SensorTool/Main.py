import sys
import os
import random
from SensorTool import parameters, helpAbout, autoUpdate
from SensorTool.Combobox import ComboBox
from PyQt5.QtCore import pyqtSignal, Qt, QTimer, QPoint, QMetaMethod
from PyQt5.QtWidgets import (QApplication, QWidget, QToolTip, QPushButton, QMessageBox, QDesktopWidget, QMainWindow,
                             QVBoxLayout, QHBoxLayout, QGridLayout, QTextEdit, QLabel, QRadioButton, QCheckBox,
                             QLineEdit, QGroupBox, QSplitter, QFileDialog)
from PyQt5.QtGui import QIcon, QFont, QTextCursor, QPixmap, QPen, QPainter, QColor, QTextDocumentWriter
import serial
import serial.tools.list_ports
import serial.threaded
import threading
import time
import binascii
import re
from collections import deque
import pyqtgraph as pg
import numpy as np
try:
  import cPickle as pickle
except ImportError:
  import pickle
if sys.platform == "win32":
    import ctypes
from PyQt5.QtChart import *


class MainWindow(QMainWindow):
    receiveUpdateSignal = pyqtSignal(str)
    updateChartSignal = pyqtSignal(list)
    errorSignal = pyqtSignal(str)
    isDetectSerialPort = False
    receiveCount = 0
    sendCount = 0
    isScheduledSending = False
    DataPath = "./"
    isHideSettings = False
    isHideFunctinal = False
    app = None
    dataCache = []
    dataDeque = deque([])
    offset = None
    readCount = 0
    # uartReceiveTimer = QTimer()
    timmer = QTimer()
    feedFlag = True
    fileCache = None
    img = None
    CHANNELCOUNT = 32
    dataMin = np.ones(CHANNELCOUNT)*33768

    def __init__(self, app):
        super().__init__()
        self.app = app
        pathDirList = sys.argv[0].replace("\\", "/").split("/")
        pathDirList.pop()
        self.DataPath = os.path.abspath("/".join(str(i) for i in pathDirList))
        if not os.path.exists(self.DataPath + "/" + parameters.strDataDirName):
            pathDirList.pop()
            self.DataPath = os.path.abspath("/".join(str(i) for i in pathDirList))
        self.DataPath = (self.DataPath + "/" + parameters.strDataDirName).replace("\\", "/")
        self.initWindow()
        self.initTool()
        self.initEvent()
        self.programStartGetSavedParameters()
        return

    def __del__(self):
        return

    def initTool(self):
        self.com = serial.Serial()
        return

    def initWindow(self):
        QToolTip.setFont(QFont('SansSerif', 10))
        # main layout
        mainWidget = QSplitter(Qt.Horizontal)

        frameWidget = QWidget()
        frameLayout = QVBoxLayout() # 整体垂直布局，包括menu和main

        configWidget = QWidget()
        configLayout = QVBoxLayout()
        configWidget.setLayout(configLayout)

        self.settingWidget = QWidget()
        self.settingWidget.setProperty("class","settingWidget")

        # self.receiveSendWidget = QSplitter(Qt.Vertical)
        self.receiveSendWidget = QWidget()

        self.functionalWiget = QWidget()
        settingLayout = QVBoxLayout()
        sendReceiveLayout = QVBoxLayout()
        sendFunctionalLayout = QGridLayout()
        mainLayout = QHBoxLayout()
        self.settingWidget.setLayout(settingLayout)
        self.receiveSendWidget.setLayout(sendReceiveLayout)
        self.functionalWiget.setLayout(sendFunctionalLayout)

        configLayout.addWidget(self.settingWidget)
        configLayout.addWidget(self.functionalWiget)

        mainLayout.addWidget(self.receiveSendWidget)
        # mainLayout.addWidget(self.settingWidget)
        # mainLayout.addWidget(self.functionalWiget)
        mainLayout.addWidget(configWidget)
        mainLayout.setStretch(0, 7)
        # mainLayout.setStretch(1, 1)
        # mainLayout.setStretch(2, 1)

        menuLayout = QHBoxLayout()

        mainWidget.setLayout(mainLayout)

        # frameLayout.addLayout(menuLayout)
        frameLayout.addWidget(mainWidget)
        frameWidget.setLayout(frameLayout)
        self.setCentralWidget(frameWidget)

        # option layout
        self.settingsButton = QPushButton()
        self.skinButton = QPushButton("")
        self.aboutButton = QPushButton()
        self.functionalButton = QPushButton()
        self.settingsButton.setProperty("class", "menuItem1")
        self.skinButton.setProperty("class", "menuItem2")
        self.aboutButton.setProperty("class", "menuItem3")
        self.functionalButton.setProperty("class", "menuItem4")
        self.settingsButton.setObjectName("menuItem")
        self.skinButton.setObjectName("menuItem")
        self.aboutButton.setObjectName("menuItem")
        self.functionalButton.setObjectName("menuItem")
        menuLayout.addWidget(self.settingsButton)
        # menuLayout.addWidget(self.skinButton)
        # menuLayout.addWidget(self.aboutButton)
        menuLayout.addStretch(0)
        menuLayout.addWidget(self.functionalButton)

        # widgets receive and send area
        # self.receiveArea = QTextEdit()
        # self.receiveArea.setFixedHeight(50)
        # self.sendArea = QTextEdit()
        self.saveReceiveButtion = QPushButton("保存")
        self.clearReceiveButtion = QPushButton(parameters.strClearReceive)
        btnLayout = QHBoxLayout()
        btnLayout.addWidget(self.saveReceiveButtion)
        btnLayout.addWidget(self.clearReceiveButtion)
        btnLayout.setStretch(0, 1)
        btnLayout.setStretch(1, 1)
        btnWidget = QWidget()
        btnWidget.setLayout(btnLayout)
        # self.sendButtion = QPushButton(parameters.strSend)
        # self.sendHistory = ComboBox()
        # sendWidget = QWidget()
        # sendAreaWidgetsLayout = QHBoxLayout()
        # sendWidget.setLayout(sendAreaWidgetsLayout)
        # buttonLayout = QVBoxLayout()
        # buttonLayout.addWidget(self.clearReceiveButtion)
        # buttonLayout.addStretch(1)
        # buttonLayout.addWidget(self.sendButtion)
        self.chartTest = Chart(self.CHANNELCOUNT)
        self.chartTest.setTitle("实时压力值")
        self.chartTest.legend().show()

        self.chartView = QChartView(self.chartTest)
        self.chartView.setStyleSheet("margin: 0px; border: 1px solid black;")
        # self.chartView.setRubberBand(QChartView.HorizontalRubberBand)
        # self.chartView.setRubberBand(QChartView.VerticalRubberBand)
        self.chartView.setRubberBand(QChartView.RectangleRubberBand)
        self.chartView.setRenderHint(QPainter.Antialiasing)

        # sendAreaWidgetsLayout.addWidget(self.sendArea)
        # sendAreaWidgetsLayout.addLayout(buttonLayout)
        sendReceiveLayout.addWidget(self.chartView)
        pw = pg.PlotWidget(name='Plot1')
        sendReceiveLayout.addWidget(pw)
        self.img = pg.ImageItem()
        pw.addItem(self.img)
        # Generate image data
        # self.imgData = np.full((8, 3, 3), [0, 255, 0])
        # self.img.setImage(self.imgData)
        # sendReceiveLayout.addWidget(self.receiveArea)
        # sendReceiveLayout.addWidget(sendWidget)
        sendReceiveLayout.addWidget(btnWidget)
        # sendReceiveLayout.addWidget(self.sendHistory)
        sendReceiveLayout.setStretch(0, 10)
        sendReceiveLayout.setStretch(1, 5)
        sendReceiveLayout.setStretch(2, 1)

        # widgets serial settings
        serialSettingsGroupBox = QGroupBox(parameters.strSerialSettings)
        serialSettingsLayout = QGridLayout()
        serialReceiveSettingsLayout = QGridLayout()
        serialSendSettingsLayout = QGridLayout()
        serialPortLabek = QLabel(parameters.strSerialPort)
        serailBaudrateLabel = QLabel(parameters.strSerialBaudrate)
        serailBytesLabel = QLabel(parameters.strSerialBytes)
        serailParityLabel = QLabel(parameters.strSerialParity)
        serailStopbitsLabel = QLabel(parameters.strSerialStopbits)
        self.serialPortCombobox = ComboBox()
        self.serailBaudrateCombobox = ComboBox()
        # self.serailBaudrateCombobox.addItem("9600")
        # self.serailBaudrateCombobox.addItem("19200")
        # self.serailBaudrateCombobox.addItem("38400")
        # self.serailBaudrateCombobox.addItem("57600")
        self.serailBaudrateCombobox.addItem("115200")
        self.serailBaudrateCombobox.addItem("230400")
        self.serailBaudrateCombobox.addItem("460800")
        self.serailBaudrateCombobox.setCurrentIndex(1)
        self.serailBaudrateCombobox.setEditable(True)
        self.serailBytesCombobox = ComboBox()
        self.serailBytesCombobox.addItem("5")
        self.serailBytesCombobox.addItem("6")
        self.serailBytesCombobox.addItem("7")
        self.serailBytesCombobox.addItem("8")
        self.serailBytesCombobox.setCurrentIndex(3)
        self.serailParityCombobox = ComboBox()
        self.serailParityCombobox.addItem("None")
        self.serailParityCombobox.addItem("Odd")
        self.serailParityCombobox.addItem("Even")
        self.serailParityCombobox.addItem("Mark")
        self.serailParityCombobox.addItem("Space")
        self.serailParityCombobox.setCurrentIndex(0)
        self.serailStopbitsCombobox = ComboBox()
        self.serailStopbitsCombobox.addItem("1")
        self.serailStopbitsCombobox.addItem("1.5")
        self.serailStopbitsCombobox.addItem("2")
        self.serailStopbitsCombobox.setCurrentIndex(0)
        self.serialOpenCloseButton = QPushButton(parameters.strOpen)
        # 选择端口
        serialSettingsLayout.addWidget(serialPortLabek, 0, 0)
        serialSettingsLayout.addWidget(self.serialPortCombobox, 0, 1)
        # 波特率
        serialSettingsLayout.addWidget(serailBaudrateLabel, 1, 0)
        serialSettingsLayout.addWidget(self.serailBaudrateCombobox, 1, 1)
        # 数据位
        serialSettingsLayout.addWidget(serailBytesLabel, 2, 0)
        serialSettingsLayout.addWidget(self.serailBytesCombobox, 2, 1)
        # 校验
        serialSettingsLayout.addWidget(serailParityLabel, 3, 0)
        serialSettingsLayout.addWidget(self.serailParityCombobox, 3, 1)
        # 停止位
        serialSettingsLayout.addWidget(serailStopbitsLabel, 4, 0)
        serialSettingsLayout.addWidget(self.serailStopbitsCombobox, 4, 1)
        # 打开/关闭按钮
        serialSettingsLayout.addWidget(self.serialOpenCloseButton, 5, 0, 1, 2)

        serialSettingsGroupBox.setLayout(serialSettingsLayout)
        settingLayout.addWidget(serialSettingsGroupBox)

        # right functional layout
        self.ChannelCheckBoxAll = QCheckBox("全选")
        self.ChannelCheckBoxAll.setChecked(True)

        # create channel check box
        for channelNum in range(self.CHANNELCOUNT):
            self.__setattr__("ChannelCheckBox" + str(channelNum + 1), QCheckBox("CH" + str(channelNum + 1)))
            self.__getattribute__("ChannelCheckBox" + str(channelNum + 1)).setChecked(True)

        functionalGroupBox = QGroupBox(parameters.strFunctionalSend)
        # functionalGridLayout = QGridLayout()
        # functionalGridLayout.addWidget(self.testCheck, 0, 1)
        # functionalGroupBox.setLayout(functionalGridLayout)
        checkBoxVerticalLayout = QGridLayout()
        checkBoxVerticalLayout.addWidget(self.ChannelCheckBoxAll, 0, 0)

        # add channel checkbox into widget
        for channelNum in range(self.CHANNELCOUNT):
            checkBoxVerticalLayout.addWidget(self.__getattribute__("ChannelCheckBox" + str(channelNum + 1)), (channelNum/2+1), (channelNum)%2)

        # checkBoxVerticalLayout.addStretch(1)
        functionalGroupBox.setLayout(checkBoxVerticalLayout)
        sendFunctionalLayout.addWidget(functionalGroupBox)

        # main window
        self.statusBarStauts = QLabel()
        self.statusBarStauts.setMinimumWidth(80)
        self.statusBarStauts.setText("<font color=%s>%s</font>" %("#008200", parameters.strReady))
        # self.statusBarSendCount = QLabel(parameters.strSend+"(bytes): "+"0")
        self.statusBarReceiveCount = QLabel(parameters.strReceive+"(bytes): "+"0")
        self.statusBar().addWidget(self.statusBarStauts)
        # self.statusBar().addWidget(self.statusBarSendCount,2)
        self.statusBar().addWidget(self.statusBarReceiveCount,3)
        # self.statusBar()

        self.resize(800, 500)
        self.MoveToCenter()
        self.setWindowTitle(parameters.appName+" V"+str(helpAbout.versionMajor)+"."+str(helpAbout.versionMinor))
        icon = QIcon()
        print("icon path:"+self.DataPath+"/"+parameters.appIcon)
        icon.addPixmap(QPixmap(self.DataPath+"/"+parameters.appIcon), QIcon.Normal, QIcon.Off)
        self.setWindowIcon(icon)
        if sys.platform == "win32":
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("comtool")
        self.show()
        return

    def initEvent(self):
        self.serialOpenCloseButton.clicked.connect(self.openCloseSerial)
        # self.sendButtion.clicked.connect(self.sendData)
        self.receiveUpdateSignal.connect(self.updateReceivedDataDisplay)
        self.updateChartSignal.connect(self.chartTest.handleData)
        self.clearReceiveButtion.clicked.connect(self.clearReceiveBuffer)
        self.serialPortCombobox.clicked.connect(self.portComboboxClicked)
        # self.sendSettingsHex.clicked.connect(self.onSendSettingsHexClicked)
        # self.sendSettingsAscii.clicked.connect(self.onSendSettingsAsciiClicked)
        self.errorSignal.connect(self.errorHint)
        # self.sendHistory.currentIndexChanged.connect(self.sendHistoryIndexChanged)
        self.settingsButton.clicked.connect(self.showHideSettings)
        # self.skinButton.clicked.connect(self.skinChange) # 换主题色
        # self.aboutButton.clicked.connect(self.showAbout) # 关于

        self.ChannelCheckBoxAll.stateChanged.connect(self.functionSetAllChannel)

        for channelNum in range(self.CHANNELCOUNT):
            self.__getattribute__("ChannelCheckBox" + str(channelNum + 1)).stateChanged.connect(self.functionSetVisible)

        self.functionalButton.clicked.connect(self.showHideFunctional)
        self.saveReceiveButtion.clicked.connect(self.on_saveReceivedData)

        # self.uartReceiveTimer.timeout.connect(self.onUartReceiveTimeOut)
        self.timmer.timeout.connect(self.onTimerOut)
        return

    def openCloseSerialProcess(self):
        try:
            if self.com.is_open:
                self.com.close()
                self.serialOpenCloseButton.setText(parameters.strOpen)
                self.statusBarStauts.setText("<font color=%s>%s</font>" % ("#f31414", parameters.strClosed))
                self.receiveProgressStop = True
                self.serialPortCombobox.setDisabled(False)
                self.serailBaudrateCombobox.setDisabled(False)
                self.serailParityCombobox.setDisabled(False)
                self.serailStopbitsCombobox.setDisabled(False)
                self.serailBytesCombobox.setDisabled(False)
                self.programExitSaveParameters()
                # 调试-打印缓存数据
                print(self.dataCache)
                print('==============')
                # print('接收数据长度 = %d' % (int(len(''.join(self.dataCache))/3)))
                print('接收数据长度 = %d' % (int(len(self.dataCache))))
                self.dataCache.clear()
                self.fileCache.close()
                self.offset = None
                self.readCount = 0
                self.timmer.stop()
            else:
                try:
                    self.com.baudrate = int(self.serailBaudrateCombobox.currentText())
                    self.com.port = self.serialPortCombobox.currentText().split(" ")[0]
                    self.com.bytesize = int(self.serailBytesCombobox.currentText())
                    self.com.parity = self.serailParityCombobox.currentText()[0]
                    self.com.stopbits = float(self.serailStopbitsCombobox.currentText())
                    self.com.timeout = None
                    print(self.com)
                    self.serialOpenCloseButton.setDisabled(True)
                    self.com.open()
                    self.serialOpenCloseButton.setText(parameters.strClose)
                    self.statusBarStauts.setText("<font color=%s>%s</font>" % ("#008200", parameters.strReady))
                    self.serialPortCombobox.setDisabled(True)
                    self.serailBaudrateCombobox.setDisabled(True)
                    self.serailParityCombobox.setDisabled(True)
                    self.serailStopbitsCombobox.setDisabled(True)
                    self.serailBytesCombobox.setDisabled(True)
                    self.serialOpenCloseButton.setDisabled(False)
                    self.dataCache.clear()
                    self.offset = None
                    self.fileCache = open('cache.txt', 'w')
                    self.fileCache.truncate()
                    self.fileCache = open('cache.txt', 'a')
                    receiveProcess = threading.Thread(target=self.receiveData)
                    receiveProcess.setDaemon(True)
                    receiveProcess.start()
                except Exception as e:
                    self.com.close()
                    self.receiveProgressStop = True
                    self.errorSignal.emit( parameters.strOpenFailed +"\n"+ str(e))
                    self.serialOpenCloseButton.setDisabled(False)
        except Exception:
            pass
        return

    def openCloseSerial(self):
        t = threading.Thread(target=self.openCloseSerialProcess)
        t.setDaemon(True)
        t.start()
        return

    def portComboboxClicked(self):
        self.detectSerialPort()
        return

    def getSendData(self):
        data = self.sendArea.toPlainText()
        if self.sendSettingsCFLF.isChecked():
            data = data.replace("\n", "\r\n")
        if self.sendSettingsHex.isChecked():
            if self.sendSettingsCFLF.isChecked():
                data = data.replace("\r\n", " ")
            else:
                data = data.replace("\n", " ")
            data = self.hexStringB2Hex(data)
            if data == -1:
                self.errorSignal.emit( parameters.strWriteFormatError)
                return -1
        else:
            data = data.encode()
        return data

    def on_saveReceivedData(self):
        self.serialOpenCloseButton.click()
        fileName, fileType = QFileDialog.getSaveFileName(
            self, '保存数据', 'data', "文本文档(*.txt);;所有文件(*.*)")
        print('Save file', fileName, fileType)
        # writer = QTextDocumentWriter(fileName)
        # writer.write(self.receiveArea.document())
        # writer.write(self.fileCache.read())
        f = open(fileName, 'w')
        self.fileCache = open('cache.txt', 'r')
        # QApplication.processEvents()
        f.write(self.fileCache.read())
        f.close()
        self.fileCache = open('cache.txt', 'a')
        self.serialOpenCloseButton.click()

    def cache_save(self, datas):
        self.fileCache.write(datas)

    def sendData(self):
        try:
            if self.com.is_open:
                data = self.getSendData()
                if data == -1:
                    return
                print(self.sendArea.toPlainText())
                print("send:",data)
                self.sendCount += len(data)
                self.com.write(data)
                data = self.sendArea.toPlainText()
                self.sendHistoryFindDelete(data)
                self.sendHistory.insertItem(0,data)
                self.sendHistory.setCurrentIndex(0)
                self.receiveUpdateSignal.emit("")
                # scheduled send
                if self.sendSettingsScheduledCheckBox.isChecked():
                    if not self.isScheduledSending:
                        t = threading.Thread(target=self.scheduledSend)
                        t.setDaemon(True)
                        t.start()
        except Exception as e:
            self.errorSignal.emit(parameters.strWriteError)
            print(e)
        return

    def scheduledSend(self):
        self.isScheduledSending = True
        while self.sendSettingsScheduledCheckBox.isChecked():
            self.sendData()
            try:
                time.sleep(int(self.sendSettingsScheduled.text().strip())/1000)
            except Exception:
                self.errorSignal.emit(parameters.strTimeFormatError)
        self.isScheduledSending = False
        return

    def receiveData(self):
        self.receiveProgressStop = False
        while(not self.receiveProgressStop):
            try:
                length = 3*16
                bytes = self.com.read(length)
                # print('length = %s, len(bytes)= %s' % (length, len(bytes)))
                self.receiveCount += len(bytes)
                strReceived = self.asciiB2HexString(bytes)
                # print(strReceived)
                self.receiveUpdateSignal.emit(strReceived) # 使用slot机制将接收到的数据发送给updateReceivedDataDisplay
            except Exception as e:
                print("receiveData error")
                # if self.com.is_open and not self.serialPortCombobox.isEnabled():
                #     self.openCloseSerial()
                #     self.serialPortCombobox.clear()
                #     self.detectSerialPort()
                print(e)
            # time.sleep(0.001) # 不注释会导致程序卡死
        return

    def updateReceivedDataDisplay(self, str):
        try:
            if str != "" and not None:
                # 将数据缓存在list中
                temp = str.split(' ')
                temp.pop() # 去掉最后一个为空格的元素
                self.dataCache.extend(temp)
                # print('str = %s, after split str = %s' % (str, temp))

                # 获取起始数据的偏移量
                if self.offset is None:
                    for mIndex in range(48):
                        # print(mIndex)
                        tempList = self.dataCache[mIndex:9+mIndex:3]
                        # print(tempList)
                        if len(tempList) > 2 and int(tempList[2], 16) - int(tempList[1], 16) == 1 and int(tempList[1], 16) - int(tempList[0], 16) == 1:
                            self.offset = mIndex
                            # print(tempList)
                            print(self.offset)
                            del self.dataCache[0:mIndex]
                            break
                else:
                    if (self.timmer.isActive() == False):
                        self.timmer.setInterval(40) # 40ms更新一次，也就是刷新速度为25Hz
                        self.timmer.start()
                        # self.timmer.timeout.connect(self.onTimerOut)
        except Exception as e1:
            print("updateReceivedDataDisplay error: %s" % e1)

        self.statusBarReceiveCount.setText("%s(bytes):%d" %(parameters.strReceive ,self.receiveCount))
        return

    def onTimerOut(self):
        samples = 16 # 每次每个通道更新16个数据点，16 = 400/(1000/40)，其中400指每个通道收到数据点的速度是400pts（串口接收速率）
        if (len(self.dataCache) > (3 * samples * self.CHANNELCOUNT)):
            self.cache_save(' '.join(self.dataCache[0:3 * samples * self.CHANNELCOUNT])) # 缓存
            QApplication.processEvents()
            toShowData = [[] for i in range(self.CHANNELCOUNT)]
            for i in range(samples * self.CHANNELCOUNT):
                channelNumber = int(self.dataCache[0], 16)
                channelData = int(''.join(self.dataCache[1:3]), 16)
                # toShowData[channelNumber - 1].append(channelData)
                if np.array(channelData).min() < self.dataMin[channelNumber - 1]:
                    self.dataMin[channelNumber - 1] = np.array(channelData).min()
                toShowData[channelNumber - 1].append(channelData - self.dataMin[channelNumber - 1])
                # print('%s, %s' % (channelNumber, channelData))
                # print(toShowData)
                del self.dataCache[0:3]
            try:
                self.feedFlag = False
                start = time.clock()
                self.updateChartSignal.emit(toShowData)
                tempA = np.array(toShowData)
                tempB = tempA[:, 0] #(24,1)
                tempC = np.zeros((self.CHANNELCOUNT, 3))
                for i in range(self.CHANNELCOUNT):
                    tempC[(i%8)*(self.CHANNELCOUNT//8)+(i//8), :] = self.blend_color([0, 255, 0], [255, 0, 0], tempB[i]/1024)
                tempD = np.reshape(tempC, (8, self.CHANNELCOUNT//8, 3))
                # test = self.blend_color([0, 255, 0], [255, 0, 0], 0.1)
                #热力图显示 TODO 将压力值转换为颜色显示
                # data = np.random.normal(size=(8, self.CHANNELCOUNT//8, 3))
                self.img.setImage(tempD)
                elapsed = (time.clock() - start)
                self.feedFlag = True
                print("Time used: %.3fs" % elapsed)
            except Exception as e:
                print("chart.handleData error: %s" % e)
            print(len(self.dataCache))

    def blend_color(self, color1, color2, f):
        [r1, g1, b1] = color1
        [r2, g2, b2] = color2
        r = r1 + (r2 - r1) * f
        g = g1 + (g2 - g1) * f
        b = b1 + (b2 - b1) * f
        return [r, g, b]

    def onSendSettingsHexClicked(self):
        data = self.sendArea.toPlainText().replace("\n","\r\n")
        data = self.asciiB2HexString(data.encode())
        self.sendArea.clear()
        self.sendArea.insertPlainText(data)
        return

    def onSendSettingsAsciiClicked(self):
        try:
            data = self.sendArea.toPlainText().replace("\n"," ").strip()
            self.sendArea.clear()
            if data != "":
                data = self.hexStringB2Hex(data).decode('utf-8','ignore')
                self.sendArea.insertPlainText(data)
        except Exception as e:
            QMessageBox.information(self,parameters.strWriteFormatError,parameters.strWriteFormatError)
        return

    def sendHistoryIndexChanged(self):
        self.sendArea.clear()
        self.sendArea.insertPlainText(self.sendHistory.currentText())
        return

    def clearReceiveBuffer(self):
        self.dataCache.clear() # 清空数据缓存list
        self.readCount = 0 # 清空读取数据缓存次数的计数器
        self.offset = None
        # self.receiveArea.clear()
        self.receiveCount = 0
        self.sendCount = 0
        self.receiveUpdateSignal.emit(None)
        # 清空图表
        self.chartTest.handleClear()
        return

    def MoveToCenter(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
        return

    def errorHint(self,str):
        QMessageBox.information(self, str, str)
        return

    def closeEvent(self, event):

        reply = QMessageBox.question(self, '退出',
                                     "确定退出？", QMessageBox.Yes |
                                     QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.com.close()
            self.timmer.stop()
            # self.uartReceiveTimer.stop()
            try:
                if self.fileCache is not None:
                    self.fileCache.close()
            except Exception as e:
                print(e)
            self.receiveProgressStop = True
            self.programExitSaveParameters()
            event.accept()
        else:
            event.ignore()

    def findSerialPort(self):
        self.port_list = list(serial.tools.list_ports.comports())
        return self.port_list

    def portChanged(self):
        self.serialPortCombobox.setCurrentIndex(0)
        self.serialPortCombobox.setToolTip(str(self.portList[0]))

    def detectSerialPort(self):
        if not self.isDetectSerialPort:
            self.isDetectSerialPort = True
            t = threading.Thread(target=self.detectSerialPortProcess)
            t.setDaemon(True)
            t.start()

    def detectSerialPortProcess(self):
        self.serialPortCombobox.clear()
        while(1):
            portList = self.findSerialPort();
            for i in portList:
                self.serialPortCombobox.addItem(str(i[0])+" "+str(i[1]))
            if len(portList)>0:
                self.serialPortCombobox.setCurrentIndex(0)
                self.serialPortCombobox.setToolTip(str(portList[0]))
                break
            # time.sleep(1)
        self.isDetectSerialPort = False
        return

    def sendHistoryFindDelete(self,str):
        self.sendHistory.removeItem(self.sendHistory.findText(str))
        return

    def test(self):
        print("test")
        return

    def asciiB2HexString(self,strB):
        strHex = binascii.b2a_hex(strB).upper()
        return re.sub(r"(?<=\w)(?=(?:\w\w)+$)", " ", strHex.decode())+" "

    def hexStringB2Hex(self,hexString):
        dataList = hexString.split(" ")
        j = 0
        for i in dataList:
            if len(i) > 2:
                return -1
            elif len(i) == 1:
                dataList[j] = "0" + i
            j += 1
        data = "".join(dataList)
        try:
            data = bytes.fromhex(data)
        except Exception:
            return -1
        print(data)
        return data

    def programExitSaveParameters(self):
        paramObj = parameters.ParametersToSave()
        paramObj.baudRate = self.serailBaudrateCombobox.currentIndex()
        paramObj.dataBytes = self.serailBytesCombobox.currentIndex()
        paramObj.parity = self.serailParityCombobox.currentIndex()
        paramObj.stopBits = self.serailStopbitsCombobox.currentIndex()
        paramObj.skin = self.param.skin
        # 注释掉发送配置相关的代码
        # if self.receiveSettingsHex.isChecked():
        #     paramObj.receiveAscii = False
        # if not self.receiveSettingsAutoLinefeed.isChecked():
        #     paramObj.receiveAutoLinefeed = False
        # else:
        #     paramObj.receiveAutoLinefeed = True
        # paramObj.receiveAutoLindefeedTime = self.receiveSettingsAutoLinefeedTime.text()
        # if self.sendSettingsHex.isChecked():
        #     paramObj.sendAscii = False
        # if not self.sendSettingsScheduledCheckBox.isChecked():
        #     paramObj.sendScheduled = False
        # paramObj.sendScheduledTime = self.sendSettingsScheduled.text()
        # if not self.sendSettingsCFLF.isChecked():
        #     paramObj.useCRLF = False
        # paramObj.sendHistoryList.clear()
        # for i in range(0,self.sendHistory.count()):
        #     paramObj.sendHistoryList.append(self.sendHistory.itemText(i))
        f = open("settings.config","wb")
        f.truncate()
        pickle.dump(paramObj, f)
        pickle.dump(paramObj.sendHistoryList,f)
        f.close()
        return

    def programStartGetSavedParameters(self):
        paramObj = parameters.ParametersToSave()
        try:
            f = open("settings.config", "rb")
            paramObj = pickle.load( f)
            paramObj.sendHistoryList = pickle.load(f)
            f.close()
        except Exception as e:
            f = open("settings.config", "wb")
            f.close()
        self.serailBaudrateCombobox.setCurrentIndex(paramObj.baudRate)
        self.serailBytesCombobox.setCurrentIndex(paramObj.dataBytes)
        self.serailParityCombobox.setCurrentIndex(paramObj.parity)
        self.serailStopbitsCombobox.setCurrentIndex(paramObj.stopBits)
        self.param = paramObj
        return

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Control:
            self.keyControlPressed = True
        elif event.key() == Qt.Key_Return or event.key()==Qt.Key_Enter:
            if self.keyControlPressed:
                self.sendData()
        elif event.key() == Qt.Key_L:
            if self.keyControlPressed:
                self.sendArea.clear()
        # elif event.key() == Qt.Key_K:
        #     if self.keyControlPressed:
        #         self.receiveArea.clear()
        return

    def keyReleaseEvent(self,event):
        if event.key() == Qt.Key_Control:
            self.keyControlPressed = False
        return

    def functionAdd(self):
        # QMessageBox.information(self, "On the way", "On the way")
        print(self.ChannelCheckBox1.isChecked())
        return

    def functionSetAllChannel(self):
        for channelNum in range(self.CHANNELCOUNT):
            self.__getattribute__("ChannelCheckBox" + str(channelNum + 1)).setChecked(self.ChannelCheckBoxAll.isChecked())

    def functionSetVisible(self):
        # self.chartTest.setVisibleFlag(1, self.__getattribute__('ChannelCheckBox1').isChecked())
        for channelNum in range(self.CHANNELCOUNT):
            self.chartTest.setVisibleFlag((channelNum + 1), self.__getattribute__("ChannelCheckBox" + str(channelNum + 1)).isChecked())

    def showHideSettings(self):
        if self.isHideSettings:
            self.showSettings()
            self.isHideSettings = False
        else:
            self.hideSettings()
            self.isHideSettings = True
        return

    def showSettings(self):
        self.settingWidget.show()
        self.settingsButton.setStyleSheet(
            parameters.strStyleShowHideButtonLeft.replace("$DataPath",self.DataPath))
        return;

    def hideSettings(self):
        self.settingWidget.hide()
        self.settingsButton.setStyleSheet(
            parameters.strStyleShowHideButtonRight.replace("$DataPath", self.DataPath))
        return;

    def showHideFunctional(self):
        if self.isHideFunctinal:
            self.showFunctional()
            self.isHideFunctinal = False
        else:
            self.hideFunctional()
            self.isHideFunctinal = True
        return

    def showFunctional(self):
        self.functionalWiget.show()
        self.functionalButton.setStyleSheet(
            parameters.strStyleShowHideButtonRight.replace("$DataPath",self.DataPath))
        return;

    def hideFunctional(self):
        self.functionalWiget.hide()
        self.functionalButton.setStyleSheet(
            parameters.strStyleShowHideButtonLeft.replace("$DataPath", self.DataPath))
        return;

    def skinChange(self):
        if self.param.skin == 1: # light
            file = open(self.DataPath + '/assets/qss/style-dark.qss', "r")
            self.param.skin = 2
        else: # elif self.param.skin == 2: # dark
            file = open(self.DataPath + '/assets/qss/style.qss', "r")
            self.param.skin = 1
        self.app.setStyleSheet(file.read().replace("$DataPath", self.DataPath))
        return

    def showAbout(self):
        QMessageBox.information(self, "About","<h1 style='color:#f75a5a';margin=10px;>"+parameters.appName+
                                '</h1><br><b style="color:#08c7a1;margin = 5px;">V'+str(helpAbout.versionMajor)+"."+
                                str(helpAbout.versionMinor)+"."+str(helpAbout.versionDev)+
                                "</b><br><br>"+helpAbout.date+"<br><br>"+helpAbout.strAbout())
        return

    def autoUpdateDetect(self):
        auto = autoUpdate.AutoUpdate()
        if auto.detectNewVersion():
            auto.OpenBrowser()

    def openDevManagement(self):
        os.system('start devmgmt.msc')

class Chart(QChart):

    def __init__(self, channelCount):
        super().__init__()
        self.m_series = 0
        # self.m_axis = QValueAxis()
        self.xMax = 400
        self.yMin = 0
        self.yMax = 1536
        self.offset = 0
        self.channelNumber = 8
        self.channelCount = channelCount
        self.channelColor = [
            Qt.red, Qt.yellow, Qt.green, Qt.blue, Qt.black, Qt.gray, Qt.magenta, Qt.cyan,
            Qt.darkRed, Qt.darkYellow, Qt.darkGreen, Qt.darkBlue, Qt.black, Qt.darkGray, Qt.darkMagenta, Qt.darkCyan,
            QColor('#EC7063'), QColor('#F4D03F'), QColor('#58D68D'), QColor('#5499C7'), QColor('#5D6D7E'), QColor('#CACFD2'), QColor('#BA4A00'), QColor('#117A65')]
        self.seriesList = []

        pen = []
        self.visibleFlag = [] # 是否显示的标志位

        # pen = QPen(Qt.red)
        # pen = QPen(QColor('#409EFF'))
        # pen.setWidth(1)

        p1 = QPen(Qt.red)
        p1.setWidth(1)

        # self.m_series = QLineSeries()
        # self.m_series.setPen(pen)

        self.scatseries0 = QScatterSeries()
        self.scatseries0.setMarkerShape(QScatterSeries.MarkerShapeCircle)  # 设置点的类型
        self.scatseries0.setMarkerSize(2)  # 设置点的大小
        self.scatseries0.setPen(p1)

        # self.addSeries(self.m_series)
        # self.addSeries(self.scatseries0)

        self.axisX = QValueAxis()
        self.axisX.setRange(0, self.xMax)
        self.axisX.setTitleText('x值')

        self.axisY = QValueAxis()
        self.axisY.setRange(self.yMin, self.yMax)
        self.axisY.setTitleText('Y值')

        self.addAxis(self.axisX, Qt.AlignBottom)
        self.addAxis(self.axisY, Qt.AlignLeft)

        # self.m_series.attachAxis(self.axisX)
        # self.m_series.attachAxis(self.axisY)
        # self.scatseries0.attachAxis(self.axisX)
        # self.scatseries0.attachAxis(self.axisY)

        for num in range(self.channelCount):
            # print(num)
            # pen[num] = QPen(self.channelColor[num])
            pen.append(QPen(QColor(random.random()*255, random.random()*255, random.random()*255,)))
            self.visibleFlag.append(True)
            # print(len(pen))
            pen[num].setWidth(1)
            self.seriesList.append(QLineSeries())
            self.seriesList[num].setName('CH'+str(num + 1))
            self.seriesList[num].setPen(pen[num])
            self.seriesList[num].setUseOpenGL(True)
            self.addSeries(self.seriesList[num])
            self.seriesList[num].attachAxis(self.axisX)
            self.seriesList[num].attachAxis(self.axisY)

        # self.createDefaultAxes()
        # self.setAxisX(self.m_axis, self.m_series)
        # self.m_axis.setTickCount(5)
        # self.axisX().setRange(0, self.xMax)
        # self.axisY().setRange(self.yMin, self.yMax)

    def handleData(self, vals):
        for num in range(self.channelCount):
            if self.offset < self.xMax or len(self.seriesList[num].pointsVector()) < self.xMax:
                # self.seriesList[num].append(self.offset, val)
                points = self.seriesList[num].pointsVector()
                for x in range(len(vals[num])):
                    points.append(QPoint(self.offset + x, vals[num][x]))
                self.seriesList[num].replace(points)
            else:
                # print("min = %d, max = %d" % (self.axisX.min(), self.axisX.max()))
                self.xMax = self.axisX.max() - self.axisX.min()
                # print("xMax = %d" % self.xMax)
                points = self.seriesList[num].pointsVector()
                # 把数据前移一个单位
                for index in range(len(points) - len(vals[num])):
                    # points[index] = QPoint(self.offset - self.xMax + index, points[index + len(vals[num])].y())  # 与后面setRange配合，完成滚动显示
                    points[index].setY(points[index + len(vals[num])].y())
                for i in range(len(vals[num])):
                    # points[len(points) - len(vals[num]) + i] = QPoint(self.offset - self.xMax + len(points) - len(vals[num]) + i + 1, vals[num][i])
                    points[len(points) - len(vals[num]) + i].setY(vals[num][i])
                self.seriesList[num].replace(points)
                # self.axisX.setRange(self.offset - self.xMax, self.offset)  # 修改x轴显示范围
        self.offset += len(vals[0])

    def handleClear(self):
        self.offset = 0
        # self.yMin = 37000
        # self.yMax = 32768
        # self.xMax = 100
        # self.axisX.setRange(0, self.xMax)
        for num in range(self.channelCount):
            self.seriesList[num].clear()

    def grabMouseEvent(self, *args, **kwargs):
        self.xMax = self.xMax * 2

    def setVisibleFlag(self, channel, val):
        # print(channel)
        # print(val)
        self.visibleFlag[channel-1] = val
        self.seriesList[channel-1].setVisible(val)
        # print("%d %s" % (channel, self.visibleFlag[channel-1]))

    def handleTimeout(self):
        x = self.plotArea().width() / self.m_axis.tickCount()
        y = (self.m_axis.max() - self.m_axis.min()) / self.m_axis.tickCount()
        self.m_x += y
        self.axisX().setRange(0, self.m_x+10)
        self.m_y += random.random()*100
        self.axisY().setRange(0, self.m_y+5)
        # print(self.m_x)
        # print(self.m_y)
        self.m_series.append(self.m_x, self.m_y)
        self.scroll(x, 0)
        # if (self.m_x == 1000):
        #     self.m_timer.stop()



def main():
    app = QApplication(sys.argv)
    mainWindow = MainWindow(app)
    print("data path:"+mainWindow.DataPath)
    if(mainWindow.param.skin == 1) :# light skin
        file = open(mainWindow.DataPath+'/assets/qss/style.qss',"r")
    else: #elif mainWindow.param == 2: # dark skin
        file = open(mainWindow.DataPath + '/assets/qss/style-dark.qss', "r")
    qss = file.read().replace("$DataPath",mainWindow.DataPath)
    app.setStyleSheet(qss)
    mainWindow.detectSerialPort()
    t = threading.Thread(target=mainWindow.autoUpdateDetect)
    t.setDaemon(True)
    t.start()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()

