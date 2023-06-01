#import whisper
import sys
from PySide6.QtWidgets import QWidget, QApplication, QLineEdit, QMainWindow, QTextBrowser, QPushButton, QMenu
import os
import difflib
import openpyxl
import zhconv
import taglib


class Window(QMainWindow):
    def __init__(self):
        super(Window, self).__init__()
        self.text = ""  # ==> 默认文本内容
        self.setWindowTitle('AudioAssetManager')  # ==> 窗口标题
        self.resize(500, 400)  # ==> 定义窗口大小
        self.textBrowser = QTextBrowser()
        self.setCentralWidget(self.textBrowser)  # ==> 定义窗口主题内容为textBrowser
        self.setAcceptDrops(True)  # ==> 设置窗口支持拖动（必须设置）
        #self.model = whisper.load_model("medium")
        #self.model = whisper.load_model("small")
        #self.ModelLevel = 'small'
        self.Artistname = ''
        self.TextCol = ''
        self.AlbumCol = ''
        self.textBrowser.setText('drag audio file and enter metadata before hit button\n')
        self.audiopath = []
        #self.gate = '0.9'
        self.initUI()

    # 鼠标拖入事件
    def dragEnterEvent(self, event):
        file = event.mimeData().urls()[0].toLocalFile()
        if file.endswith('.wav'):
            event.accept()
        else:
            self.textBrowser.setText('drag .wav file please')
            event.ignore()

    # 鼠标放开
    def dropEvent(self, event):
        #self.setWindowTitle('FindingSimilarAudio')
        filepath = event.mimeData().urls()[0].toLocalFile()  # ==> 获取文件路径
        #print("拖拽的文件 ==> {}".format(file))
        #self.text += file + "\n"
        #self.textBrowser.setText(self.text)
        if filepath.endswith('.wav'):
            self.audiopath.append(filepath)
            self.text = 'audio files path set to:\n'
            for filepath in self.audiopath:
                self.text += filepath +'\n'
            #self.wb = openpyxl.load_workbook(file)
            #self.text += 'sheet: '+self.Sheetname + ' opened'
            #self.textBrowser.setText('sheet: '+self.Sheetname + ' opened')
        else:
            self.text = 'drag in .wav file please!!!'

        self.textBrowser.setText(self.text)
        event.accept()#事件处理完毕,不向上转发,ignore()则向上转发

    def addTag(self, filepath, tagname, metadata):
        with taglib.File(filepath, save_on_exit=True) as song:
            song.tags[tagname] = [metadata] # always use lists, even for single values
            #song.tags["PERFORMER:HARPSICHORD"] = ["TestToSee"]
        # with save_on_exit=True, file will be saved at the end of the 'with' block

    def initUI(self):
        MetadataBtn = QPushButton('add metadata', self)
        MetadataBtn.setCheckable(True)
        MetadataBtn.move(10, 350)
        DeleteBtn = QPushButton('Delete Metadata', self)
        DeleteBtn.setCheckable(True)
        DeleteBtn.resize(110, 30)
        DeleteBtn.move(380, 350)
        #MinusBtn = QPushButton('-', self)
        #MinusBtn.setCheckable(True)
        #MinusBtn.move(210, 350)
        MetadataBtn.clicked[bool].connect(self.applyMetadata)
        DeleteBtn.clicked[bool].connect(self.deleteMetadata)
        #MinusBtn.clicked[bool].connect(self.MinusNum)
        #self.setGeometry(300, 300, 280, 170)
        #self.setWindowTitle('切换按钮') 
        #self.show()
        TextColwidget = QLineEdit(self)
        # 设置最长输入字符10个
        #TextColwidget.setMaxLength(10)
        # 输入框提示
        TextColwidget.setPlaceholderText("comment here")
        TextColwidget.setClearButtonEnabled(True)
        TextColwidget.resize(300, 30)
        # 设置输入框只读
        # widget.setReadOnly(True)
        # 按下回车键
        #widget.returnPressed.connect(self.return_pressed)
        # 鼠标选中
        #widget.selectionChanged.connect(self.selection_changed)
        # 文本发生变化
        TextColwidget.textChanged.connect(self.TextColtext_changed)
        # 正在编辑
        #widget.textEdited.connect(self.text_edited)
        TextColwidget.move(10, 270)
        
        AlbumColwidget = QLineEdit(self)
        # 设置最长输入字符10个
        AlbumColwidget.setMaxLength(10)
        # 输入框提示
        AlbumColwidget.setPlaceholderText("Album")
        AlbumColwidget.setClearButtonEnabled(True)
        AlbumColwidget.textChanged.connect(self.AlbumColtext_changed)
        # 正在编辑
        #widget.textEdited.connect(self.text_edited)
        AlbumColwidget.move(10, 300)

        Artistwidget = QLineEdit(self)
        # 设置最长输入字符10个
        Artistwidget.setMaxLength(10)
        # 输入框提示
        Artistwidget.setPlaceholderText("Artist")
        Artistwidget.textChanged.connect(self.Artisttext_changed)
        Artistwidget.setClearButtonEnabled(True)
        # 正在编辑
        #widget.textEdited.connect(self.text_edited)
        Artistwidget.move(110, 300)

        #Gatewidget = QLineEdit(self)
        # 设置最长输入字符10个
        #Gatewidget.setMaxLength(10)
        # 输入框提示
        #Gatewidget.setPlaceholderText("accuracy gate, default 0.9")
        #Gatewidget.textChanged.connect(self.gatechange)
        # 正在编辑
        #widget.textEdited.connect(self.text_edited)
        #Gatewidget.move(210, 300)
        
    def applyMetadata(self, pressed):
        if len(self.audiopath) == 0:
            self.textBrowser.setText('drag in .wav files to set the audio path first!!!')
            return

        self.text = 'set metadata:\n'
        for filepath in self.audiopath:
            if self.TextCol != '':
                self.addTag(filepath, "COMMENT", self.TextCol)
            if self.AlbumCol != '':
                self.addTag(filepath, "ALBUM", self.AlbumCol)
            if self.Artistname != '':
                self.addTag(filepath, "ARTIST", self.Artistname)
            self.text += filepath +'\n'

        self.text += 'completed :)'
        self.audiopath.clear()
        self.textBrowser.setText(self.text)

        #result = model.transcribe(r"G:\SpeechRecognition\whisper\mytest\untitled_1.wav")
        #print(result["text"])

    def deleteMetadata(self, pressed):
        if len(self.audiopath) == 0:
            self.textBrowser.setText('drag in .wav files to set the audio path first!!!')
            return

        self.text = 'delete metadata:\n'
        for filepath in self.audiopath:
            self.addTag(filepath, "COMMENT", "")
            self.addTag(filepath, "ALBUM", "")
            self.addTag(filepath, "ARTIST", "")
            self.text += filepath +'\n'
        self.audiopath.clear()
        self.textBrowser.setText('COMMENT, ALBUM, ARTIST metadata deleted')


    def TextColtext_changed(self, s):
        self.TextCol = s

    def AlbumColtext_changed(self, s):
        self.AlbumCol = s

    def Artisttext_changed(self, s):
        self.Artistname = s

    def gatechange(self, s):
        self.gate = s

    def Compare(self, A,B):
        #if self.is_chinese(A[0]) and self.ModelLevel == 'medium':
            #self.textBrowser.setText('aaaaaaaaa')
            #B = zhconv.convert(B, 'zh-cn')
            #self.textBrowser.setText('bbbbbbbbbbbb')
        return difflib.SequenceMatcher(None, A, B).quick_ratio()

    def is_chinese(self, char):
        if '\u4e00' <= char <= '\u9fff':
            return True
        else:
            return False


'''
    def return_pressed(self):
        print("Return pressed!")
        #self.centralWidget().setText("Boom!")

    def selection_changed(self):
        print("Selection changed!")
        #print(self.centralWidget().selectedText())

    def text_edited(self, s):
        print("Text edited...")
        #print(s)
'''

app = QApplication(sys.argv)
window = Window()
window.show()
sys.exit(app.exec())