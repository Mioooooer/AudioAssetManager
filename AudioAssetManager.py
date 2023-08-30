#import whisper
import sys
from PySide6.QtWidgets import QWidget, QApplication, QLineEdit, QMainWindow, QTextBrowser, QPushButton, QMenu, QListWidget, QTableWidget, QHeaderView, QAbstractItemView, QTableWidgetItem, QCheckBox
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtCore import QUrl, Slot
#from PySide6.QtMultimedia import QMediaFormat
import os
import difflib
import openpyxl
#import zhconv
import taglib
import json
import shutil
import subprocess


class Window(QMainWindow):
    def __init__(self):
        super(Window, self).__init__()
        self.text = ""  # ==> 默认文本内容
        self.AppVer = "1.3.3"
        self.setWindowTitle('AudioAssetManager'+' Ver '+self.AppVer)  # ==> 窗口标题
        self.resize(1280, 720)  # ==> 定义窗口大小
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
        #//self.TagToProcess = []
        self.StorePath = '//xxxxx/xxxxx/xxxxx/'
        self.ConfigJsonPath = 'config.json'
        self.AssetJsonPath = 'AudioAssetData.json'
        self.TagInputWidgetList = []
        self.ModifiedWidgetList = []
        self.SearchList = []
        self.SearchGate = 0.7
        self.initUI()
        #init player
        self.player = QMediaPlayer()
        self.audioOutput = QAudioOutput() # 不能实例化为临时变量，否则被自动回收导致无法播放
        self.player.setAudioOutput(self.audioOutput)
        #self.player.positionChanged.connect(self.positionChanged)
        #self.player.durationChanged.connect(self.durationChanged)
        #self.player.playbackStateChanged.connect(self.stateChanged)
        #self.player.errorOccurred.connect(self._player_error)
        # Qt6中`QMediaPlayer.setVolume`已被移除，使用`QAudioOutput.setVolume`替代
        self.audioOutput.setVolume(1)
        #end init player

    # 鼠标拖入事件
    def dragEnterEvent(self, event):
        file = event.mimeData().urls()[0].toLocalFile()
        #if file.endswith('.wav'):
        event.accept()
        #else:
        #    self.textBrowser.setText('drag .wav file please')
        #    event.ignore()

    # 鼠标放开
    def dropEvent(self, event):
        #self.setWindowTitle('FindingSimilarAudio')
        filepath = event.mimeData().urls()[0].toLocalFile()  # ==> 获取文件路径
        #print("拖拽的文件 ==> {}".format(file))
        #self.text += file + "\n"
        #self.textBrowser.setText(self.text)
        #//if filepath.endswith('.wav'):
        self.audiopath.append(filepath)
        self.text = 'audio files path set to:\n'
        for filepath in self.audiopath:
            self.text += filepath +'\n'
            #self.wb = openpyxl.load_workbook(file)
            #self.text += 'sheet: '+self.Sheetname + ' opened'
            #self.textBrowser.setText('sheet: '+self.Sheetname + ' opened')
        #//else:
            #//self.text = 'drag in .wav file please!!!'

        self.textBrowser.setText(self.text)
        event.accept()#事件处理完毕,不向上转发,ignore()则向上转发

    def addTag(self, filepath, tagname, metadata):
        with taglib.File(filepath, save_on_exit=True) as song:
            song.tags[tagname] = [metadata] # always use lists, even for single values
            #song.tags["PERFORMER:HARPSICHORD"] = ["TestToSee"]
        # with save_on_exit=True, file will be saved at the end of the 'with' block

    def initUI(self):
        jsonPathConfigPatchFilePath = './AudioAssetManagerConfigPatch.json'
        if os.path.exists(jsonPathConfigPatchFilePath):
            with open(jsonPathConfigPatchFilePath, encoding='utf-8') as configpatch:
                jsonconfigpatch = json.load(configpatch)
                self.StorePath = jsonconfigpatch.get("StorePath")
        jsonfilepath = self.StorePath + self.ConfigJsonPath
        if not os.path.exists(jsonfilepath):
            self.textBrowser.setText("config.json not found in specified cloud drive path\nReset path by add an json file in app's directory named as AudioAssetManagerConfigPatch.json with content like {\"StorePath\": \"//要修改的地址放这里/这些都是范例/WorkShare/quanjx/音频归档测试用地/\"}")
            return
        with open(jsonfilepath, encoding='utf-8') as a:
            # 读取文件
            self.jsonContent = json.load(a)
            if self.jsonContent[0].get('AppVer') != self.AppVer:
                self.textBrowser.setText("App ver is not consistent with config stored in cloud drive.\nYou can get latest app from 音频部网盘\nLatest Ver is "+self.jsonContent[0].get('AppVer'))
                return
            self.SearchGate = self.jsonContent[0].get('SearchGate')
            for tag in self.jsonContent[0].get('SaveTag'):
                if tag.get('ComboBox') == 'True':
                    TagColwidget = QListWidget(self)
                    for comboContent in tag.get('ComboContent'):
                        TagColwidget.addItem(comboContent.get('ComboName'))

                    self.TagInputWidgetList.append(TagColwidget)
                    x = 10 + 100.0*((len(self.TagInputWidgetList)-1)%12)
                    y = 250 + 30.0*((len(self.TagInputWidgetList)-1)//12)
                    #TagColwidget.move(10, 350)
                    TagColwidget.move(x, y)
                    continue
                
                TagColwidget = QLineEdit(self)
                # 输入框提示
                TagColwidget.setPlaceholderText(tag.get('TagName'))
                TagColwidget.setClearButtonEnabled(True)
                #TagColwidget.textChanged.connect(self.TagColtext_changed)
                # 正在编辑
                #widget.textEdited.connect(self.text_edited)
                self.TagInputWidgetList.append(TagColwidget)
                x = 10 + 100.0*((len(self.TagInputWidgetList)-1)%12)
                y = 250 + 30.0*((len(self.TagInputWidgetList)-1)//12)
                #TagColwidget.move(10, 350)
                TagColwidget.move(x, y)


            #-------modified module------------------------------------------
            for tag in self.jsonContent[0].get('SaveTag'):
                if tag.get('ComboBox') == 'True':
                    TagColwidget = QListWidget(self)
                    for comboContent in tag.get('ComboContent'):
                        TagColwidget.addItem(comboContent.get('ComboName'))

                    self.ModifiedWidgetList.append(TagColwidget)
                    x = 10 + 100.0*((len(self.ModifiedWidgetList)-1)%12)
                    y = 400 + 30.0*((len(self.ModifiedWidgetList)-1)//12)
                    #TagColwidget.move(10, 350)
                    TagColwidget.move(x, y)
                    continue
                
                TagColwidget = QLineEdit(self)
                # 输入框提示
                TagColwidget.setPlaceholderText(tag.get('TagName'))
                TagColwidget.setClearButtonEnabled(True)
                #TagColwidget.textChanged.connect(self.TagColtext_changed)
                # 正在编辑
                #widget.textEdited.connect(self.text_edited)
                self.ModifiedWidgetList.append(TagColwidget)
                x = 10 + 100.0*((len(self.ModifiedWidgetList)-1)%12)
                y = 400 + 30.0*((len(self.ModifiedWidgetList)-1)//12)
                #TagColwidget.move(10, 350)
                TagColwidget.move(x, y)

            #-------modified module------------------------------------------


        CheckinAssetBtn = QPushButton('check in', self)
        CheckinAssetBtn.setCheckable(True)
        CheckinAssetBtn.move(10, 370)
        CheckinAssetBtn.clicked[bool].connect(self.checkinAsset)
                
        SearchAssetBtn = QPushButton('search', self)
        SearchAssetBtn.setCheckable(True)
        SearchAssetBtn.move(210, 370)
        SearchAssetBtn.clicked[bool].connect(self.displaySearchAsset)

        ModifyAssetBtn = QPushButton('modify', self)
        ModifyAssetBtn.setCheckable(True)
        ModifyAssetBtn.move(10, 520)
        ModifyAssetBtn.clicked[bool].connect(self.modifiedAsset)

        DownloadAssetBtn = QPushButton('download', self)
        DownloadAssetBtn.setCheckable(True)
        DownloadAssetBtn.move(310, 370)
        DownloadAssetBtn.clicked[bool].connect(self.downloadAsset)

        playAssetBtn = QPushButton('play/stop', self)
        playAssetBtn.setCheckable(True)
        playAssetBtn.move(410, 370)
        playAssetBtn.clicked[bool].connect(self.playAsset)

        SearchAssetBtn = QPushButton('delete', self)
        SearchAssetBtn.setCheckable(True)
        SearchAssetBtn.move(610, 520)
        SearchAssetBtn.clicked[bool].connect(self.deleteAsset)


        MetadataBtn = QPushButton('add metadata', self)
        MetadataBtn.setCheckable(True)
        MetadataBtn.move(10, 650)
        DeleteBtn = QPushButton('Delete Metadata', self)
        DeleteBtn.setCheckable(True)
        DeleteBtn.resize(110, 30)
        DeleteBtn.move(380, 650)
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
        TextColwidget.move(10, 570)
        
        AlbumColwidget = QLineEdit(self)
        # 设置最长输入字符10个
        #AlbumColwidget.setMaxLength(10)
        # 输入框提示
        AlbumColwidget.setPlaceholderText("Album")
        AlbumColwidget.setClearButtonEnabled(True)
        AlbumColwidget.textChanged.connect(self.AlbumColtext_changed)
        # 正在编辑
        #widget.textEdited.connect(self.text_edited)
        AlbumColwidget.move(10, 600)

        Artistwidget = QLineEdit(self)
        # 设置最长输入字符10个
        #Artistwidget.setMaxLength(10)
        # 输入框提示
        Artistwidget.setPlaceholderText("Artist")
        Artistwidget.textChanged.connect(self.Artisttext_changed)
        Artistwidget.setClearButtonEnabled(True)
        # 正在编辑
        #widget.textEdited.connect(self.text_edited)
        Artistwidget.move(110, 600)

    #todo: lock modified when not open table!!!!
    def modifiedAsset(self, pressed):
        jsonfilepath = self.StorePath + self.AssetJsonPath
        with open(jsonfilepath, encoding='utf-8') as a:
            # 读取文件
            self.AudioAssetDataJson = json.load(a)
        #-------------------------------------------------------------------------------
        #self.AudioAssetDataJson[1].get('AssetList').index(self.displayAssetList[0])
        #print(self.AudioAssetDataJson[1].get('AssetList').index(self.displayAssetList[0]))#this is index
        for idx in range(0, len(self.SearchCheckList)):
            if self.SearchCheckList[idx].isChecked():
                currentIdx = self.AudioAssetDataJson[1].get('AssetList').index(self.displayAssetList[idx])
                #targetDict = self.AudioAssetDataJson[1].get('AssetList')[currentIdx]#this is target dict
                #print(currentIdx)

                #for idx in range(0, len(self.ModifiedWidgetList)):
                    #self.ModifiedWidgetList[idx].text()#todo modified
                    #self.AudioAssetDataJson[1].get('AssetList')[currentIdx][toEnterTag]

                #---modified dict content----------------------------------------------------------------------------------------
                for secondIdx in range(0, len(self.ModifiedWidgetList)):
                    if self.jsonContent[0].get('SaveTag')[secondIdx].get('ComboBox') == 'True':
                        if self.ModifiedWidgetList[secondIdx].currentItem() != None:
                            self.AudioAssetDataJson[1].get('AssetList')[currentIdx][self.jsonContent[0].get('SaveTag')[secondIdx].get('TagName')] = self.ModifiedWidgetList[secondIdx].currentItem().text()
                    else:
                        if self.ModifiedWidgetList[secondIdx].text() != '':
                            self.AudioAssetDataJson[1].get('AssetList')[currentIdx][self.jsonContent[0].get('SaveTag')[secondIdx].get('TagName')] = self.ModifiedWidgetList[secondIdx].text()
                #----------------------------------------------------------------------------------------------------------------

                #---move file if path change-------------------------------------------------------------------------------------
                storefilepath = self.AudioAssetDataJson[1].get('AssetList')[currentIdx][self.jsonContent[0].get('SaveTag')[0].get('TagName')]+'/'+self.AudioAssetDataJson[1].get('AssetList')[currentIdx][self.jsonContent[0].get('SaveTag')[1].get('TagName')]+'/'+self.AudioAssetDataJson[1].get('AssetList')[currentIdx][self.jsonContent[0].get('SaveTag')[2].get('TagName')]
                actualpath = self.AudioAssetDataJson[1].get('AssetList')[currentIdx]['ActualFilePath']
                fileName = self.AudioAssetDataJson[1].get('AssetList')[currentIdx]['FileName']
                if actualpath != storefilepath:
                    self.AudioAssetDataJson[1].get('AssetList')[currentIdx]['ActualFilePath'] = storefilepath
                    if os.path.isdir(self.StorePath + actualpath +'/'+ fileName):
                        if os.path.exists(self.StorePath + storefilepath +'/'+ fileName):
                            if os.path.exists(self.StorePath + 'TrashBinForAudioAssetManager'+'/'+os.path.basename(fileName)):
                                shutil.rmtree(self.StorePath + 'TrashBinForAudioAssetManager'+'/'+os.path.basename(fileName))
                            shutil.copytree(self.StorePath + storefilepath +'/'+ fileName, self.StorePath + 'TrashBinForAudioAssetManager'+'/'+os.path.basename(fileName))
                            shutil.rmtree(self.StorePath + storefilepath +'/'+ fileName)
                        shutil.copytree(self.StorePath + actualpath +'/'+ fileName, self.StorePath + storefilepath +'/'+ fileName)
                        shutil.rmtree(self.StorePath + actualpath +'/'+ fileName)
                    else:
                        self.copyFile(self.StorePath + actualpath +'/'+ fileName, self.StorePath + storefilepath)
                        os.remove(self.StorePath + actualpath +'/'+ fileName)
                #----------------------------------------------------------------------------------------------------------------
                self.textBrowser.setText('modify '+ fileName)
        #-------------------------------------------------------------------------------
        with open(jsonfilepath, 'w', encoding='utf-8') as r:
            json.dump(self.AudioAssetDataJson, r, ensure_ascii=False)


    def downloadAsset(self, pressed):
        #-------------------------------------------------------------------------------
        #self.AudioAssetDataJson[1].get('AssetList').index(self.displayAssetList[0])
        #print(self.AudioAssetDataJson[1].get('AssetList').index(self.displayAssetList[0]))#this is index
        for idx in range(0, len(self.SearchCheckList)):
            if self.SearchCheckList[idx].isChecked():
                #currentIdx = self.AudioAssetDataJson[1].get('AssetList').index(self.displayAssetList[idx])
                #---copy file to app's folder------------------------------------------------------------------------------------
                actualpath = self.displayAssetList[idx]['ActualFilePath']
                fileName = self.displayAssetList[idx]['FileName']
                if os.path.isdir(self.StorePath + actualpath +'/'+ fileName):
                    #os.system(self.StorePath + actualpath +'/'+ fileName)
                    subprocess.run(['explorer',os.path.realpath(self.StorePath + actualpath +'/'+ fileName)])
                else:
                    self.copyFile(self.StorePath + actualpath +'/'+ fileName, './')
                #----------------------------------------------------------------------------------------------------------------


    def playAsset(self, pressed):
        #-------------------------------------------------------------------------------
        #self.AudioAssetDataJson[1].get('AssetList').index(self.displayAssetList[0])
        #print(self.AudioAssetDataJson[1].get('AssetList').index(self.displayAssetList[0]))#this is index
        if pressed:
            for idx in range(0, len(self.SearchCheckList)):
                if self.SearchCheckList[idx].isChecked():
                    #currentIdx = self.AudioAssetDataJson[1].get('AssetList').index(self.displayAssetList[idx])
                    #---copy file to app's folder------------------------------------------------------------------------------------
                    actualpath = self.displayAssetList[idx]['ActualFilePath']
                    fileName = self.displayAssetList[idx]['FileName']
                    if os.path.isdir(self.StorePath + actualpath +'/'+ fileName):
                        #os.system(self.StorePath + actualpath +'/'+ fileName)
                        subprocess.run(['explorer',os.path.realpath(self.StorePath + actualpath +'/'+ fileName)])
                    else:
                        self.copyFile(self.StorePath + actualpath +'/'+ fileName, './AudioAssetManagerTempFolder')#copy to temp folder
                        self.play('./AudioAssetManagerTempFolder' +'/'+ fileName)
                    break#just play the first checked audio and then break the loop
                    #----------------------------------------------------------------------------------------------------------------
        else:
            self.stop()
            self.player.setSource(QUrl.fromLocalFile(''))#release source
            shutil.rmtree('./AudioAssetManagerTempFolder')#delete temp folder


    def play(self, filepath):
        # `QMediaPlayer.setMedia` 方法已从Qt6中移除，使用`.setSource`
        self.player.setSource(QUrl.fromLocalFile(filepath))
        #self.player.setSource(filepath)
        self.player.play()
    
    def stop(self):
        self.player.stop()

    #@Slot()
    def positionChanged(self, position):
        print(f'positionChanged: {position}')

    #@Slot()
    def durationChanged(self, duration):
        print(f'durationChanged: {duration}')

    #@Slot()
    def stateChanged(self, state):
        print(f'stateChanged: {state}')

    #@Slot()
    def _player_error(self, error, error_string):
        print(error, error_string)





    def deleteAsset(self, pressed):
        jsonfilepath = self.StorePath + self.AssetJsonPath
        with open(jsonfilepath, encoding='utf-8') as a:
            # 读取文件
            self.AudioAssetDataJson = json.load(a)
        #-------------------------------------------------------------------------------
        #self.AudioAssetDataJson[1].get('AssetList').index(self.displayAssetList[0])
        #print(self.AudioAssetDataJson[1].get('AssetList').index(self.displayAssetList[0]))#this is index
        for idx in range(0, len(self.SearchCheckList)):
            if self.SearchCheckList[idx].isChecked():
                #currentIdx = self.AudioAssetDataJson[1].get('AssetList').index(self.displayAssetList[idx])
                self.AudioAssetDataJson[1].get('AssetList').remove(self.displayAssetList[idx])#remove the same dict
                #---move file to temp folder in case miss delete-----------------------------------------------------------------
                actualpath = self.displayAssetList[idx]['ActualFilePath']
                fileName = self.displayAssetList[idx]['FileName']
                if os.path.isdir(self.StorePath + actualpath +'/'+ fileName):
                    if os.path.exists(self.StorePath + 'TrashBinForAudioAssetManager'+'/'+os.path.basename(fileName)):
                        shutil.rmtree(self.StorePath + 'TrashBinForAudioAssetManager'+'/'+os.path.basename(fileName))
                    shutil.copytree(self.StorePath + actualpath +'/'+ fileName, self.StorePath + 'TrashBinForAudioAssetManager'+'/'+os.path.basename(fileName))
                    shutil.rmtree(self.StorePath + actualpath +'/'+ fileName)
                else:
                    self.copyFile(self.StorePath + actualpath +'/'+ fileName, self.StorePath + 'TrashBinForAudioAssetManager')
                    os.remove(self.StorePath + actualpath +'/'+ fileName)
                #----------------------------------------------------------------------------------------------------------------
                self.textBrowser.setText('deleted '+ fileName)
        #-------------------------------------------------------------------------------
        with open(jsonfilepath, 'w', encoding='utf-8') as r:
            json.dump(self.AudioAssetDataJson, r, ensure_ascii=False)



    def displaySearchAsset(self, pressed):
        self.displayAssetList = self.searchAsset()
        if len(self.displayAssetList) != 0:
            row = len(self.displayAssetList)
            col = len(self.displayAssetList[0])
            self.SearchTable = QTableWidget(row, col)
            tempLabelList = []
            for k in self.displayAssetList[0]:
                tempLabelList.append(k)
            self.SearchTable.setHorizontalHeaderLabels(tempLabelList)
            self.SearchTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            self.SearchTable.setEditTriggers(QAbstractItemView.NoEditTriggers)
            self.SearchTable.resize(1000,500)

            self.SearchCheckList = []
            for i in range(0, row):
                for j in range(0, col):
                    if j == 0:
                        CheckBox = QCheckBox(str(self.displayAssetList[i].get(tempLabelList[j])))
                        self.SearchTable.setCellWidget(i, j, CheckBox)
                        self.SearchCheckList.append(CheckBox)
                    else:
                        self.SearchTable.setItem(i, j, QTableWidgetItem(str(self.displayAssetList[i].get(tempLabelList[j]))))

            #print(self.SearchCheckList[0].checkState())
            #print(self.SearchCheckList[1].isChecked())

            self.SearchTable.show()
            #SearchTable.setVisible()
            #SearchTable.resize(500, 1000)
        else:
            self.textBrowser.setText('no matching result!!!\nDont press modified and delete options, although they would be useless in theory!')

        #for asset in displayAsset:


    def searchAsset(self):
        jsonfilepath = self.StorePath + self.AssetJsonPath
        with open(jsonfilepath, encoding='utf-8') as a:
            # 读取文件
            self.AudioAssetDataJson = json.load(a)

        tempSearchGroup = self.AudioAssetDataJson[1].get('AssetList')

        for idx in range(0, len(self.TagInputWidgetList)):
            if self.jsonContent[0].get('SaveTag')[idx].get('ComboBox') == 'True':
                if self.TagInputWidgetList[idx].currentItem() != None:
                    tempSearchGroup2 = []
                    for asset in tempSearchGroup:
                        if asset.get(self.jsonContent[0].get('SaveTag')[idx].get('TagName')) == self.TagInputWidgetList[idx].currentItem().text():
                            tempSearchGroup2.append(asset)
                    tempSearchGroup = tempSearchGroup2#按标签匹配一轮一轮缩小范围

        for idx in range(0, len(self.TagInputWidgetList)):
            if self.jsonContent[0].get('SaveTag')[idx].get('ComboBox') != 'True':
                if self.TagInputWidgetList[idx].text() != '':
                    searchContent = self.TagInputWidgetList[idx].text()
                    tempSearchGroup2 = []
                    for asset in tempSearchGroup:
                        assetContent = asset.get(self.jsonContent[0].get('SaveTag')[idx].get('TagName'))
                        print(self.jsonContent[0].get('SaveTag')[idx].get('TagName'))
                        if assetContent != None and assetContent != '':
                            print(asset)
                            print(assetContent)
                            print(self.compareContent(searchContent, assetContent))
                            if self.compareContent(searchContent, assetContent):
                                tempSearchGroup2.append(asset)
                    tempSearchGroup = tempSearchGroup2
        return tempSearchGroup



    def compareContent(self, contentA, contentB):
        return (contentA in contentB) or (contentB in contentA) or (self.difflibRatio(contentA, contentB) > self.SearchGate)


    def difflibRatio(self, strA, strB):
        return difflib.SequenceMatcher(None, strA, strB).quick_ratio()


    def checkinAsset(self, pressed):
        if len(self.audiopath) == 0:
            self.textBrowser.setText('drag in .wav files to set the audio path first!!!')
            return

        self.text = 'check in:\n'
        for filepath in self.audiopath:
            tempdir = self.updateJson(filepath)
            copydir = self.StorePath + tempdir
            if os.path.isdir(filepath):
                self.copyFolder(filepath, os.path.join(copydir,os.path.basename(filepath)))
            else:
                self.copyFile(filepath, copydir)
            self.text += filepath + '->' + copydir + '\n'

        self.text += 'completed :)'
        self.audiopath.clear()
        self.textBrowser.setText(self.text)

    def copyFile(self, src, dir):#dir just enter folder, don't enter file name!!!
        if not os.path.exists(dir):
            os.makedirs(dir)
        shutil.copy2(src, dir)

    def copyFolder(self, src, dir):
        if not os.path.exists(dir):
            os.makedirs(dir)
        if os.path.exists(dir):
            if os.path.exists(self.StorePath + 'TrashBinForAudioAssetManager'+'/'+os.path.basename(dir)):
                shutil.rmtree(self.StorePath + 'TrashBinForAudioAssetManager'+'/'+os.path.basename(dir))
            shutil.copytree(dir, self.StorePath + 'TrashBinForAudioAssetManager'+'/'+os.path.basename(dir))
            shutil.rmtree(dir)
        shutil.copytree(src, dir)

    def updateJson(self, actualfilepath):
        jsonfilepath = self.StorePath + self.AssetJsonPath
        with open(jsonfilepath, encoding='utf-8') as a:
            # 读取文件
            self.AudioAssetDataJson = json.load(a)
        
        tempdict = {}
        tempdict.update({"AssetID": self.AudioAssetDataJson[0].get("AssetIDCount")})
        tempdict.update({"FileName": os.path.basename(actualfilepath)})
        for idx in range(0, len(self.TagInputWidgetList)):
            if self.jsonContent[0].get('SaveTag')[idx].get('ComboBox') == 'True':
                if self.TagInputWidgetList[idx].currentItem() == None:
                    self.text += 'please select attributes '+ str(idx+1) +'\n'
                    self.textBrowser.setText(self.text)
                else:
                    #print(self.TagInputWidgetList[idx].currentItem().text())
                    tempdict.update({self.jsonContent[0].get('SaveTag')[idx].get('TagName'): self.TagInputWidgetList[idx].currentItem().text()})   
            else:
                #print(self.TagInputWidgetList[idx].text())
                tempdict.update({self.jsonContent[0].get('SaveTag')[idx].get('TagName'): self.TagInputWidgetList[idx].text()})
        storefilepath = tempdict[self.jsonContent[0].get('SaveTag')[0].get('TagName')]+'/'+tempdict[self.jsonContent[0].get('SaveTag')[1].get('TagName')]+'/'+tempdict[self.jsonContent[0].get('SaveTag')[2].get('TagName')]
        tempdict.update({"ActualFilePath": storefilepath})
        self.AudioAssetDataJson[0]["AssetIDCount"] += 1
        self.AudioAssetDataJson[1].get('AssetList').append(tempdict)
        with open(jsonfilepath, 'w', encoding='utf-8') as r:
            json.dump(self.AudioAssetDataJson, r, ensure_ascii=False)
        #print(storefilepath)
        return storefilepath

                
        
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

    #def Compare(self, A,B):
        #if self.is_chinese(A[0]) and self.ModelLevel == 'medium':
            #self.textBrowser.setText('aaaaaaaaa')
            #B = zhconv.convert(B, 'zh-cn')
            #self.textBrowser.setText('bbbbbbbbbbbb')
        #return difflib.SequenceMatcher(None, A, B).quick_ratio()

    def is_chinese(self, char):
        if '\u4e00' <= char <= '\u9fff':
            return True
        else:
            return False

    def closeEvent(self, event) -> None:
        sys.exit(0)


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