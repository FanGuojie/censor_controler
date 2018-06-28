appName = "传感器上位机"
strDataDirName = "SensorToolData"
strDataAssetsDirName = "SensorToolData/assets"
appIcon = "assets/logo.png"
appLogo = "assets/logo.png"
appLogo2 = "assets/logo2.png"

author = "newtonbob"
strSend = "Send"
strReceive = "Receive"
strSerialPort = "串口"
strSerialBaudrate = "波特率"
strSerialBytes = "数据位"
strSerialParity = "校验位"
strSerialStopbits = "停止位"
strAscii = "ASCII"
strHex = "HEX"
strSendSettings = "Send Settings"
strReceiveSettings = "Receive Settings"
strOpen = "打开"
strClose = "关闭"
strAutoLinefeed = "Auto\nLinefeed\n(ms)"
strAutoLinefeedTime = "200"
strScheduled = "Scheduled\nSend(ms)"
strScheduledTime = "300"
strSerialSettings = "串口设置"
strSerialReceiveSettings = "Receive Settings"
strSerialSendSettings = "Send Settings"
strClearReceive = "重置"
strAdd = "+"
strFunctionalSend = "通道设置"
strBaudRateDefault = "115200"
strOpenFailed = "Open Failed"
strOpenReady = "Open Ready"
strClosed = "Closed"
strWriteError = "Send Error"
strReady = "Ready"
strWriteFormatError = "format error"
strCRLF = "<CRLF>(for Windows)"
strTimeFormatError = "Time format error"
strHelp = "HELP"
strAbout = "ABOUT"
strSettings = "Settings"
strNeedUpdate = "Need Update"
strUpdateNow = "update now?"
strUninstallApp = "uninstall app"


class ParametersToSave:
    baudRate = 4
    dataBytes = 3
    parity = 0
    stopBits = 0
    receiveAscii = True
    receiveAutoLinefeed = False
    receiveAutoLindefeedTime = "200"
    sendAscii = True
    sendScheduled = False
    sendScheduledTime = "300"
    useCRLF = True
    skin = 1
    sendHistoryList = []
    def __init__(self):
        return

    def __del__(self):
        return

strStyleShowHideButtonLeft = '''
QPushButton {
    border-image: url("$DataPath/assets/arrow-left.png")
}
QPushButton:hover {
    border-image: url("$DataPath/assets/arrow-left-white.png")
}'''

strStyleShowHideButtonRight = '''
QPushButton {
    border-image: url("$DataPath/assets/arrow-right.png")
}
QPushButton:hover {
    border-image: url("$DataPath/assets/arrow-right-white.png")
}'''

