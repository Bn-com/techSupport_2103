#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
__title__ = bnStandalongeTools
__author__ = Ben 
__mtime__ = 2021/4/5 : 14:10
__description__: 

THEOREM: A good programmer should wipe the butts of his predecessors in an amicable way,
    instead of reinventing a new butt.
        As long as this , code is far away from bugs, and with the god animal protecting
            I love animals. They taste delicious.
"""
import sys,re,os,copy,inspect,random,time
import xml.etree.ElementTree as xml
import subprocess
try:
    from cStringIO import StringIO
except:
    from io import StringIO

if str(sys.executable).endswith("maya.exe"):
    import maya.OpenMayaUI as mui
    try:
        import shiboken as sbk
    except:
        import shiboken2 as sbk
try:
    from PySide.QtGui import *
    from PySide.QtCore import *
    from PySide.QtUiTools import QUiLoader
    import pysideuic as uic
except:
    from PySide2.QtWidgets import *
    from PySide2.QtGui import *
    from PySide2.QtCore import *
    from PySide2.QtUiTools import QUiLoader
    import pyside2uic as uic
def getMayaWindow():
    ptr = mui.MQtUtil.mainWindow()
    if ptr is not None:
        return sbk.wrapInstance(long(ptr), QWidget)
def loadUiType(uiFile):
    parsed = xml.parse(uiFile)
    widget_class = parsed.find('widget').get('class')
    form_class = parsed.find('class').text
    with open(uiFile, 'r') as f:
        o = StringIO()
        frame = {}
        uic.compileUi(f, o, indent=0)
        pyc = compile(o.getvalue(), '<string>', 'exec')
        exec(pyc,frame)
        # Fetch the base_class and form class based on their type in the xml from designer
        form_class = frame['Ui_%s' % form_class]
        base_class = eval('%s' % widget_class)
    return form_class, base_class
## live tempelate require variables b B  BnStandaloneTools nStandaloneTools
ui_name = 'bnStandaloneTools.ui'
import command as cmd
import upEnv
import optTxtEdt
import diyPallet
import execTxtEdt;reload(execTxtEdt)

import logging
logger = logging.getLogger(__name__)

class QtHandler(logging.Handler):

    def __init__(self):
        logging.Handler.__init__(self)

    def emit(self, record):
        record = self.format(record)
        optTxtEdt.XStream.stdout().write("{}\n".format(record))

handler = QtHandler()
handler.setFormatter(logging.Formatter("[%(levelname)s] < %(module)s::%(funcName)s::%(lineno)04d>: %(message)s"))
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)





class BnStandaloneTools_UI(QMainWindow):
    def __init__(self, parent=None):
        super(BnStandaloneTools_UI, self).__init__(parent)
        # dir_path = os.path.dirname(sys.argv[0])
        dir_path = os.path.dirname(__file__)
        ui_file = os.path.normpath(os.path.join(dir_path, "uis/{}".format(ui_name)))
        form, base = loadUiType(ui_file)
        self.bs = base()
        self.ui = form()
        self.ui.setupUi(self)
        try: 1/0; import BnStandaloneTools_2py as xx;self.ui = xx.Ui_BnStandaloneTools_mainWin()
        except: pass
        self.pb_lst = self.findChildren(QPushButton)
        # self.ui.grp_exec.setStyleSheet("QGroupBox:title {color: #80C8FA;}")
        self.move(200,200)
        # self.resize()
        #---------------------variables-------------------------
        self.maya_version = None
        self._maya_location = None
        self._python_home = None
        self._exec = None
        self._mayapy_path = None
        self._searchDir = None
        self._outputDir = cmd.joinpath(os.getenv('temp'),'MayaStandaonle_output{0}'.format(time.strftime('%Y%m%d_%H%M%S')))
        self.setupUi2()
        #---------------connection-------------------------------

    def setupUi2(self):
        self.buttonGroup = QButtonGroup(self)
        self.buttonGroup.addButton(self.ui.rb_myvs_16)
        self.buttonGroup.addButton(self.ui.rb_myvs_18)
        self.buttonGroup.addButton(self.ui.rb_myvs_19)
        self.buttonGroup.addButton(self.ui.rb_myvs_oth)
        # self.ui.
        self.opt = optTxtEdt.OptTxEdt(self.ui.frm_opt)
        self.opt_ly = QVBoxLayout(self.ui.frm_opt)
        self.opt_ly.addWidget(self.opt)

        for e_bt in self.pb_lst:
            # print(e_pt.objectName())
            if e_bt.objectName() not in ['pb_run']:
                _fuction = getattr(self, "_cmd_{}".format(e_bt.objectName()))  if "_cmd_{}".format(e_bt.objectName()) in self.__class__.__dict__ else lambda :self.someFunc(e_bt)
                e_bt.clicked.connect(_fuction)
        try:
            self.ui.pb_run.clicked.connect(self.runIt)
        except:
            pass
        self.exec_txt = execTxtEdt.ExecTxtEdt(self.ui.frm_exec)
        self.ui.vlyout_4.addWidget(self.exec_txt)
        self.exec_txt.SgExecObj.connect(self._set_exec_txt)
        # self._diyplatter = diyPallet.MyPaletter(self)
        # self._diyplatter._setPalette()
        self._setPalette()
        self._preprocess()

        # self.ui.grp_exec.setStyleSheet('QGroupBox {color: green;background-color: #21323F}')
        self.fn_set_autlayer2defualt_exec()
        # ==============connect =========================================
        self.buttonGroup.buttonClicked.connect(self.update_mayaloc)
        self.ui.le_myvsn.editingFinished.connect(self.update_mayaloc)
        #================set ui element ================================
        self.ui.le_opt.setText(self._outputDir)
        # self.opt.redirectOPT()
    @Slot()
    def _set_exec_txt(self,q=None):
        """
            set execute text edit contents....
        """
        # if not q: q=self._exec
        self._exec = q
        self.exec_txt.setText(self._exec )
        print(">>> Execute Set to File > {}".format(self._exec))
    def _setup_exec_group(self):
        self.ui.grp_exec.setAcceptDrops(True)
        self.ui.txt_cmd.setAcceptDrops(False)

    def reset(self):
        self.maya_version = None
        self._maya_location = None
        self._python_home = None
    def runIt(self):
        if not self._mayapy_path:
            logger.error("DO NOT FIND mayapy.exe !!!!!")
            return
        print(">>>Output Director : < {} >".format(self._outputDir))
        print("Ready to ...............")
        self._invoke_mayapy()
        # print("Em.......................")
        # try:
        #     import maya.standalone
        #     maya.standalone.initialize(name='python')
        # except Exception as e:
        #     print(str(e))
        #     # self.fn_set_env()
        #     # print("\n".join(sys.path))
        #     import maya.standalone
        #     maya.standalone.initialize(name='python')
        # print(".....................................em...........????")
    def _invoke_mayapy(self):
        # replace mayaPath with the path on your system to mayapy.exe
        # replace scriptPath with the path to the script you just saved
        # def massAddRenderLayer(filenames,layername):
        pr_maya = subprocess.Popen([self._mayapy_path,self._exec],shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        out,err = pr_maya.communicate()
        exitcode = pr_maya.returncode
        if str(exitcode) != '0':
            print(err)
            logger.error(">>> some thing wrong!!!...")
        else:
            logger.info(">>>Successful!!!!")
    def update_mayaloc(self):
        """
            radiobutton connected
        """
        print(">>> switch to >>> ")
        self._preprocess()
    def _preprocess(self):
        self.reset()
        self._fn_maya_location()
        self._set_mayapy()
    def someFunc(self,q):
        print(q.objectName())
    def _fn_q_maya_version(self):
        sel_rb_vsn  = self.buttonGroup.checkedButton()
        vs_str = str(sel_rb_vsn.text())
        mayaVsn = None
        if vs_str in ['other']:
            mayaVsn = str(self.ui.le_myvsn.text())
        else:
            mayaVsn = vs_str
        return mayaVsn
    def _set_mayapy(self):
        """
            set mayapy lable text
        """
        print("....mayapy.exe ........locate.....")
        print(self._maya_location)
        if self._maya_location:
            self._mayapy_path = cmd.joinpath(self._maya_location, 'bin', 'mayapy.exe')
            self.ui.lb_mayapy.setText(">>>" +  self._mayapy_path)
        else:
            self._mayapy_path = None
            self.ui.lb_mayapy.setText(">>>" + u"????????????maya{}????????????".format(self.maya_version))

    def _fn_maya_location(self):
        self.maya_version = self._fn_q_maya_version()
        print(self.maya_version)
        winenv = upEnv.Win32Environment()
        winenv.subkey=r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Autodesk Maya {}".format(self.maya_version)
        winenv.name="InstallLocation"
        maya_loc = winenv.getenv()
        if not maya_loc:
            # logger.info(u"??????????????????????????? maya{} ???????????????".format(self.maya_version))
            return
        self._maya_location = maya_loc
        self._python_home = cmd.normalJoinpath(maya_loc,'Python')
        return True
    def fn_set_autlayer2defualt_exec(self):
        """
            set default exec py file
        :return:
        """
        moduleDir = cmd.tierpath(sys.argv[0],1)
        autoLayer_py = cmd.joinpath(moduleDir,'execs','anAutoLayer.py')
        self._exec = autoLayer_py
        self.exec_txt.setText(self._exec)
    def fn_set_env(self):
        os.environ["MAYA_LOCATION"] = self._maya_location
        os.environ["PYTHONHOME"] = self._python_home
        # os.environ["PATH"] = cmd.normalJoinpath(self._maya_location,'bin;') + os.environ["PATH"]
        cmd.update_env("PATH",cmd.normalJoinpath(self._maya_location,'bin;'))
        #-------------sys.path...---------------------------------------
        cmd.sysPathAppend(cmd.normalJoinpath(self._python_home,"lib","site-packages","setuptools-0.6c9-py2.6.egg"))
        # cmd.sysPathAppend("C:\Program Files\Autodesk\Maya2014\Python\lib\site-packages\pymel-1.0.0-py2.6.egg")
        cmd.sysPathAppend(cmd.normalJoinpath(self._python_home,"lib","site-packages","pymel-1.0.0-py2.6.egg"))
        # cmd.sysPathAppend("C:\Program Files\Autodesk\Maya2014\Python\lib\site-packages\ipython-0.10.1-py2.6.egg")
        cmd.sysPathAppend(cmd.normalJoinpath(self._python_home,"lib","site-packages","ipython-0.10.1-py2.6.egg"))
        # cmd.sysPathAppend("C:\Program Files\Autodesk\Maya2014\Python\lib\site-packages\ply-3.3-py2.6.egg")
        cmd.sysPathAppend(cmd.normalJoinpath(self._python_home,"lib","site-packages","ply-3.3-py2.6.egg"))
        # cmd.sysPathAppend("C:\Program Files\Autodesk\Maya2014\\bin\python26.zip")
        cmd.sysPathAppend(cmd.normalJoinpath(self._maya_location,"bin","python26.zip"))
        # cmd.sysPathAppend("C:\Program Files\Autodesk\Maya2014\Python\DLLs")
        cmd.sysPathAppend(cmd.normalJoinpath(self._python_home,"DLLs"))
        # cmd.sysPathAppend("C:\Program Files\Autodesk\Maya2014\Python\lib")
        cmd.sysPathAppend(cmd.normalJoinpath(self._python_home, "lib"))
        # cmd.sysPathAppend("C:\Program Files\Autodesk\Maya2014\Python\lib\plat-win")
        cmd.sysPathAppend(cmd.normalJoinpath(self._python_home, "lib", "plat-win"))
        # cmd.sysPathAppend("C:\Program Files\Autodesk\Maya2014\Python\lib\lib-tk")
        cmd.sysPathAppend(cmd.normalJoinpath(self._python_home, "lib", "lib-tk"))
        # cmd.sysPathAppend("C:\Program Files\Autodesk\Maya2014\\bin")
        cmd.sysPathAppend(cmd.normalJoinpath(self._maya_location, "bin"))
        # cmd.sysPathAppend("C:\Program Files\Autodesk\Maya2014\Python")
        cmd.sysPathAppend(cmd.normalJoinpath(self._maya_location, "bin"))
        # cmd.sysPathAppend("C:\Program Files\Autodesk\Maya2014\Python\lib\site-packages")
        cmd.sysPathAppend(cmd.normalJoinpath(self._python_home,"lib","site-packages"))
    def _setPalette(self):
        # self.setStyle("Windows")
        # self.setStyle(QStyleFactory.create('Windows'))
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(1, 22, 39))
        # palette.setColor(QPalette.Window, QColor(33, 33, 33))
        # palette.setColor(QPalette.Window, QColor(60, 66, 72))
        palette.setColor(QPalette.WindowText, QColor(255, 128, 0))
        # palette.setColor(QPalette.Base, QColor(25, 25, 25))
        palette.setColor(QPalette.Base, QColor(33, 50, 63))
        palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        palette.setColor(QPalette.ToolTipBase, Qt.green)
        palette.setColor(QPalette.ToolTipText, Qt.white)
        palette.setColor(QPalette.Text, QColor(255, 128, 0))
        # palette.setColor(QPalette.Button, QColor(0, 0, 0))
        palette.setColor(QPalette.ButtonText, QColor(88, 155, 122))
        palette.setColor(QPalette.BrightText, Qt.red)
        palette.setColor(QPalette.Link, QColor(42, 130, 218))
        palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        palette.setColor(QPalette.HighlightedText, QColor(127, 235, 255))
        self.setPalette(palette)
def main_ui():
    for widget in qApp.allWidgets():
        if hasattr(widget, "objectName"):
            # if widget.objectName() == '****':
            if widget.objectName() == "BnStandaloneTools_mainWin": #'Ui_MainWindow'
                widget.close()
    view = BnStandaloneTools_UI(parent=getMayaWindow())
    view.show()        
if __name__ == '__main__':
    import sys
    """
import sys
sys.path.append(r'&FILE PATH PASTE HERE& ')
from PySide2.QtWidgets import *

import bnStandaloneTools as xxx;reload(xxx)
#xxx.main_ui()
for widget in qApp.allWidgets():
    if hasattr(widget, "objectName"):
        if widget.objectName() == "BnStandaloneTools_mainWin":
            widget.close()
xx = xxx.BnStandaloneTools_UI(xxx.getMayaWindow())
xx.show()
    """

    app = QApplication(sys.argv)
    # view = UI()
    view = BnStandaloneTools_UI()
    view.show()
    sys.exit(app.exec_())
    