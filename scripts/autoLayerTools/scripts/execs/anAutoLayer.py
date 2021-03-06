#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os,re,yaml,copy,sys,time
import glob,fnmatch
# MAYA_LOCATION = "C:/Program Files/Autodesk/Maya2018"
# os.environ["MAYA_LOCATION"] = MAYA_LOCATION
# PYTHON_LOCATION = MAYA_LOCATION + "/Python/Lib/site-packages"
# os.environ["PYTHONPATH"] = PYTHON_LOCATION
# sys.path.append(PYTHON_LOCATION)
try:
    from maya import standalone
    standalone.initialize()
except Exception as e:
    print(e)

import pymel.core as pm

# if str(sys.executable).endswith("maya.exe"):
import maya.cmds as mc
import pymel.core as pm
import maya.OpenMaya as om
import maya.api.OpenMaya as om2
sys.setrecursionlimit(10000)
class AnAutoLayer(object):
    def __init__(self,anFile=None):
        # ======file name part============
        self._anFile = anFile
        self._anScname = None # pm.sceneName()
        self._shotID,self._stage=None,None
        self._proj = None   # self._anScname.basename().split('_')[0]
        self._fileformat = 'ma'
        self._fileformatSpare = 'mb'
        self._2basename_bg,self._2basename_chr = None,None
        self._2fpth_bg,self._2fpth_chr= None,None
        self._fps = 24
        self.assetRefs = []
        #==========render layer part =======================
        self._layertemplateDir = None
        self._lytmpFpth = None
        self._renderer = None
        # ============parse need========================
        self._profiles = None
        self._configData = None
        self._shotCams,self._shotCamShps = [],[]
        self._rndLayers = {}
        self._projRoot = None
        self._save2dir = None
        self._searchdir = None
        self._shotType = 2
        self._assetDir_chr,self._assetDir_prop,self._assetDir_setting=None,None,None
        self._resolution_w = 1920
        self._resolution_h = 1080
        self._mayaDefaultRenderGlobal,self._mayaDefaultResolution = None,None
        self._minTime,self._maxTime = None,None
        self._outputPrefix = ""
        self.issue = {}
        self.issueLogfile = None
        self.layered_bg_already = False
        self.layered_chr_already = False
        self.override = False
        self.save2folder = ""
        self.imageFormat = 'exr'
        self.saveHoldTiers = True
        self.refAnim = None
        self._aoSubDivSet_name = 'aoSubDivSet'
        self._aosubdivset_node = None
        #====================run mode =====================
        self._runmode = "reference"
        self._mayaFileTypeDesc= {'ma':'mayaAscii','mb':'mayaBinary'}
        self.fileFormatSymmetry = {'mb': 'ma', 'ma': 'mb'}
    def reset(self):
        self._anFile = None
        self._anScname = None  # pm.sceneName()
        self._shotID, self._stage = None, None
        self._proj = None  # self._anScname.basename().split('_')[0]
        self._fileformat = 'ma'
        self._fileformatSpare = 'mb'
        self._2basename_bg, self._2basename_chr = None, None
        self._2fpth_bg, self._2fpth_chr = None, None
        self._fps = 24
        self.assetRefs = []
        # ==========render layer part =======================
        self._layertemplateDir = None
        self._lytmpFpth = None
        self._renderer = None
        # ============parse need========================
        self._profiles = None
        self._configData = None
        self._shotCams, self._shotCamShps = [], []
        self._rndLayers = {}
        self._projRoot = None
        self._save2dir = None
        self._searchdir = None
        self._shotType = 2
        self._assetDir_chr, self._assetDir_prop, self._assetDir_setting = None, None, None
        self._resolution_w = 1920
        self._resolution_h = 1080
        self._mayaDefaultRenderGlobal, self._mayaDefaultResolution = None, None
        self._minTime, self._maxTime = None, None
        self._outputPrefix = ""
        self.issue = {}
        self.issueLogfile = None
        self.layered_bg_already = False
        self.layered_chr_already = False
        self.override = False
        self.save2folder = ""
        self.imageFormat = 'exr'
        self.saveHoldTiers = True
        self.refAnim = None
        self._aoSubDivSet_name = 'aoSubDivSet'
        self._aosubdivset_node = None
    @property
    def anFile(self):
        return self._anFile
    @anFile.setter
    def anFile(self,filepath):
        self._anFile = filepath
    @property
    def profiles(self):
        return self._profiles
    @profiles.setter
    def profiles(self,fpth):
        self._profiles = fpth
    @property
    def shotCams(self):
        if not self._shotCams:
            for e_cam_nm in pm.listCameras():
                # e_cam_nm = pm.listCameras()[0]
                e_cam = pm.PyNode(e_cam_nm)
                if not e_cam.isReferenced(): continue
                if e_cam.referenceFile() == self.refAnim:
                    self._shotCams.append(e_cam)
        return self._shotCams
    @property
    def shotCamShps(self):
        if not self._shotCamShps:
            if self.shotCams:
                for e_cam in self._shotCams:
                    if e_cam.nodeType() in ['transform']:
                        camShp = e_cam.getShape()
                        self._shotCamShps.append(camShp)
                    else:
                        self._shotCamShps.append(e_cam)
        return self._shotCamShps
    # @property
    def fn_listRndLayers(self):
        for e_ly in pm.ls(type='renderLayer'):
            lyname = e_ly.name()
            if re.search('defaultRenderLayer', lyname):
                e_ly.renderable.set(0)
            if re.search('^shadow',lyname,re.I): self._rndLayers['shadow'] = e_ly
            elif re.search('^mask',lyname,re.I): self._rndLayers['mask']=e_ly
            elif re.search('^chcolor',lyname,re.I):self._rndLayers['ch'] = e_ly
            elif re.search('^chrgb',lyname,re.I):self._rndLayers['chidp'] = e_ly
            elif re.search('^bg',lyname,re.I):self._rndLayers['bg'] = e_ly
        # return self._rndLayers
    @property
    def runmode(self):
        return self._runmode
    @runmode.setter
    def runmode(self,mode):
        self._runmode = mode
    @property
    def fileformat(self):
        return self._fileformat
    @fileformat.setter
    def fileformat(self,fmt):
        self._fileformat = fmt
        self._fileformatSpare = self.fileFormatSymmetry[fmt]
    @property
    def fileformatSpare(self):
        return self._fileformatSpare
    @property
    def save2dir(self):
        return self._save2dir
    @save2dir.setter
    def save2dir(self,dir):
        self._save2dir = dir
        self._searchdir = dir
    def readConfData(self,profiles=None):
        """
            read profiles get config data
        """
        if not profiles: profiles = self.profiles
        data = None
        with open(profiles,'r') as rf:
            data = yaml.load(rf)
        self.confData = copy.deepcopy(data['RENDER'])
        self._resolution_w,self._resolution_h = float(self.confData['resolution']['width']),float(self.confData['resolution']['height'])
        self._renderer = self.confData['renderer'] if self.confData.has_key('renderer') else 'arnolder'
        self._projRoot = self.confData['projRoot'] if self.confData.has_key('projRoot') else ""
        self._assetDir_chr = re.sub(r"\\","/",os.path.normpath(self.confData['AssetDir']['character']))
        self._assetDir_prop = re.sub(r"\\","/",os.path.normpath(self.confData['AssetDir']['prop']))
        self._assetDir_setting = re.sub(r"\\","/",os.path.normpath(self.confData['AssetDir']['setting']))
        self._lightSuffxi_bg = self.confData['lightSuffix']['BG']
        self._lightSuffxi_chr = self.confData['lightSuffix']['CH']
        self._shotType = int(self.confData['shotType'])
        self._fps = int(self.confData['fps'])
        self._outputPrefix = self.confData['outputPrefix']
        self.imageFormat = self.confData['image format'] if self.confData.has_key('image format') else 'exr'
        print(">>> config data settled........")
    def analyseAnFilePath(self,dealFile=None):
        """
            via animation file analyse needed argument
        :return:
        """
        if not dealFile: dealFile = self.anFile
        self.anDir = os.path.dirname(dealFile)
        self.anBasename = os.path.basename(dealFile)
        self.anBsnmStrip, self.anExt = os.path.splitext(self.anBasename)
        self.anBsnmSplt = self.anBsnmStrip.split('_')
        self._proj = self.anBsnmSplt[0]
        # print(yml_fpth)
        self.yml_fpth = os.path.join(os.path.dirname(__file__), "confs", self._proj, "autoLayerConf.yml")
        if not self._profiles: self.profiles = self.yml_fpth

    def analyseFilename(self):
        """
        analyse file name
        :return:
        """
        # nameSplt = self._anScname.basename().split('_')
        # self._proj = nameSplt[0]


        self._shotID = "_".join(self.anBsnmSplt[1:self._shotType])
        shotID_last = self.anBsnmSplt[self._shotType]
        shotID_lastReg = re.sub(".?\w*$", "", shotID_last)
        self._shotID += "_{}".format(shotID_lastReg)
        self.annameAsNamespace = "{}_{}".format(self._proj,self._shotID)
        self._2basename_chr = "{0}_{1}_{2}.{3}".format(self._proj,self._shotID,self._lightSuffxi_chr,self.fileformat)
        self._2basename_chr_spare = "{0}_{1}_{2}.{3}".format(self._proj,self._shotID,self._lightSuffxi_chr,self.fileformatSpare)
        self._2basename_bg = "{0}_{1}_{2}.{3}".format(self._proj,self._shotID,self._lightSuffxi_bg,self.fileformat)
        self._2basename_bg_spare = "{0}_{1}_{2}.{3}".format(self._proj,self._shotID,self._lightSuffxi_bg,self.fileformatSpare)
        # self.save2folder = self._fn_outputFolderTier(self.anFile,self._shotType) if self.saveHoldTiers else ""
        self.save2folder = "/".join(self.anBsnmSplt[1:self._shotType])
        print(">>> via file name calculates output file name........DONE!!!!")
    def varsFromMaya(self):
        self._mayaDefaultResolution = pm.PyNode("defaultResolution")
        self._mayaDefaultRenderGlobal = pm.PyNode("defaultRenderGlobals")
        # self._minTime = pm.env.minTime
        # self._maxTime = pm.env.maxTime
        print(">>> Some Maya nodes asign to variables....DONE!!!")
    def fn_parsNecessityVars(self):
        """
            assign value to every necessity variables
            :return:
        """
        # ???????????????????????? ???????????? ?????????????????????????????????
        self.analyseAnFilePath()
        # ??????????????????????????????????????????
        self.readConfData()
        # ??? ???????????????????????????????????? ??????????????????
        self.analyseFilename()
        # ????????????????????????????????????
        self.varsFromMaya()
        # ?????????????????????
        if self.confData.has_key('templateDir'):
            self._layertemplateDir = self.confData['templateDir']
        else:
            self._layertemplateDir = os.path.join(self._projRoot,'layerTemplate')
        if self.confData.has_key("outputDir") and self.confData["outputDir"]:
            if not self.save2dir:
                self.save2dir = self.confData["outputDir"]
        else:
            if not self.save2dir:
                self.save2dir = os.path.dirname(self.anFile)
        if self.confData.has_key("searchDir") and self.confData["searchDir"]:
            if not self._searchdir:
                self._searchdir = self.confData["searchDir"]
        else:
            if not self._searchdir:
                self._searchdir = self.save2dir
        ## renderlayer template file
        if not os.path.isdir(os.path.join(self.save2dir,self.save2folder)): os.makedirs(os.path.join(self.save2dir,self.save2folder))
        self._get_template_fPath()
        if not self._lytmpFpth: return None
        # ????????????????????? ????????????????????? ?????????
        self._2fpth_chr = os.path.normpath(os.path.join(self.save2dir,self.save2folder,self._2basename_chr))
        self._2fpth_chr_spare = os.path.normpath(os.path.join(self.save2dir,self.save2folder,self._2basename_chr_spare))
        self._2fpth_bg = os.path.normpath(os.path.join(self.save2dir,self.save2folder,self._2basename_bg))
        self._2fpth_bg_spare = os.path.normpath(os.path.join(self.save2dir,self.save2folder,self._2basename_bg_spare))
        self._srch_fpth_chr = os.path.normpath(os.path.join(self._searchdir,self.save2folder,self._2basename_chr))
        self._srch_fpth_chr_spare = os.path.normpath(os.path.join(self._searchdir,self.save2folder,self._2basename_chr_spare))
        self._srch_fpth_bg = os.path.normpath(os.path.join(self._searchdir,self.save2folder,self._2basename_bg))
        self._srch_fpth_bg_spare = os.path.normpath(os.path.join(self._searchdir, self.save2folder,self._2basename_bg_spare))
        self.issueLogfile = os.path.join(self.save2dir,self.save2folder,'{}_lyingIssue.log'.format(self.annameAsNamespace))
        print(">>> all necessity variables settled................DONE!!!!")
        return True
    def fn_wr2issuefile(self):
        wr2f_str = ""
        for k,v in self.issue.iteritems():
            wr2f_str += k + os.linesep
            for item in v:
                wr2f_str += "\t\t{}{}".format(item,os.linesep)
        with open(self.issueLogfile, 'w') as wf:
            wf.write(wr2f_str)

    def _referenceAnim(self):
        """
            reference animation file to current scene
        :return:
        """
        self.refAnim = pm.createReference(self.anFile, namespace=self.annameAsNamespace,prompt=False)

    def fn_list_assets(self):
        self.assetRefs = pm.listReferences(parentReference=self.refAnim)


    def _openAnim(self):
        pm.openFile(self.anFile,f=True,prompt=False)

    def _setCamera(self):
        """
            set render camera
        :return:
        """
        for e_cam in pm.ls(type='camera'):
            if e_cam not in self.shotCamShps:
                try:
                    e_cam.renderable.set(0)
                except:
                    pass
            else:
                try:
                    e_cam.renderable.set(1)
                except:
                    pass
        print(">>> Camera setting Done!!!!!!")
    def run_autoLayer(self):
        """
            auto layer
        :return:
        """

        # step0 get necessity variables
        pm.newFile(f=True)
        print(u">>> out put dir >>> {}".format(os.path.join(self.save2dir,self.save2folder)))
        print(u">>> search dir >>> {} ".format(os.path.join(self._searchdir,self.save2folder)))
        self.vars = self.fn_parsNecessityVars()
        if not self.vars:
            print(">>> Don't Find template file..")
            self.fn_wr2issuefile()
        # detect output file exist or not
        needRun = self._fn_detect_optOrNot()
        if not needRun:
            print(">>>Files Alread Exist...Skipped..................")
            return
        print(">>>                  STEP:  open anim file get time range.....")
        self.fn_getAnimTimerange()
        # step1 animation file ( open or reference )
        print(">>>                  STEP:  reference animation file.......")
        self._referenceAnim()
        print(">>>                  STEP: list all assets .....................")
        self.fn_list_assets()
        # create subdivision set
        self.fn_create_arnold_set()
        # stpe2 set camera and resolution,fps,timerange
        print(">>>                  STEP: set some arugments ....................")
        self.config_renderBasic()
        self._setCamera()
        self.fn_setFPS()
        self.fn_setTimeRange()
        # step3 import layer template file
        print(">>>                 STEP: ready import layer template ...............")
        self.imp_layerTemp()
        # step 3-4  list render layers
        print(">>>                 STEP: list all render layers.......................")
        self.fn_listRndLayers()
        # step4 layer assets
        print(">>>                 STEP: LAYER  PROCEDURE.............................")
        self.layerAllAssets2Rndlyer()
        # step add
        print(">>>                  STEP: set render parameters ......................")
        self.fn_setRenderParameters()
        # step5 save as bg
        print(">>>>>>>>>>>>        STEP:  SAVE AS FILE ---------------------------------")
        try:
            if self.layered_bg_already:
                if self.override: self._saveAsBG()
            else:
                self._saveAsBG()
        except Exception as e:
            print(e)
            self.issue.update({"Save Fialed":["bg lighting file"]})
            print(">>> File Save BG Lighting file Failed......................")
        # step 6 save as chr
        try:
            if self.layered_chr_already:
                if self.override: self._saveAsChr()
            else:
                self._saveAsChr()
        except Exception as e:
            print(e)
            self.issue.update({"Save Fialed": ["chr lighting file"]})
            print(">>> File Save CHR Lighting file Failed......................")
        if self.issue:
            self.fn_wr2issuefile()
    def _saveAsBG(self):
        """
            export bg file
        :return:
        """
        for type, layer in self._rndLayers.iteritems():
            if type not in ['bg']:
                layer.renderable.set(0)
            else:
                layer.renderable.set(1)
        savedPath = None
        try:
            pm.renameFile(self._2fpth_bg,type=self._mayaFileTypeDesc[self.fileformat])
            savedPath = self._2fpth_bg
        except:
            pm.renameFile(self._2fpth_bg_spare,type =self._mayaFileTypeDesc[self.fileformatSpare])
            savedPath = self._2fpth_bg_spare
        pm.saveFile(f=True)
        print(">>> file saved successful  <{}>".format(savedPath))
    def _saveAsChr(self):
        for type, layer in self._rndLayers.iteritems():
            if type not in ['bg']:
                layer.renderable.set(1)
            else:
                layer.renderable.set(0)
        savedPath = None
        try:
            pm.renameFile(self._2fpth_chr, f=True,type=self._mayaFileTypeDesc[self.fileformat])
            savedPath = self._2fpth_chr
        except:
            pm.renameFile(self._2fpth_chr_spare, f=True, type=self._mayaFileTypeDesc[self.fileformatSpare])
            savedPath = self._2fpth_chr_spare
        pm.saveFile(f=True)
        print(">>> file saved successful  <{}>".format(savedPath))
    def config_renderBasic(self):
        self._mayaDefaultResolution.height.set(self._resolution_h)
        self._mayaDefaultResolution.width.set(self._resolution_w)
        if self._mayaDefaultRenderGlobal.currentRenderer.get() != self._renderer:
            if self._renderer == 'anorld':
                try:
                    if not mc.pluginInfo('mtoa.mll', query=True, loaded=True):
                        mc.loadPlugin('mtoa.mll')
                    self._mayaDefaultRenderGlobal.currentRenderer.set('arnold')
                except:
                    om.MGlobal.displayError(u'Arnold?????????????????????????????????????????????')

    def _get_template_fPath(self):
        """
            get the template file path
        :return:
        """
        self._lytmpFpth = os.path.join(self._layertemplateDir,"layer_pass_{0}.mb".format(self._renderer))
        if not os.path.isfile(self._lytmpFpth):
            self._lytmpFpth = os.path.join(self._layertemplateDir, "layer_pass_{0}.ma".format(self._renderer))
        if not os.path.isfile(self._lytmpFpth):
            pm.warning("layer templeate file did not exist {0} <{1}>".format(os.linesep,self._lytmpFpth))
            self.issue.update({'Missed Template file':[self._lytmpFpth]})
    def imp_layerTemp(self):
        """
            import layer template file
        """
        pm.importFile(self._lytmpFpth,defaultNamespace=False)
    
    def layerAllAssets2Rndlyer(self):
        # self.assetRefs = pm.listReferences()
        for e_ref in self.assetRefs:
            self.layerAsset2layer(e_ref)
    def layerAsset2layer(self,oneRef):
        """
            layer asset to corresponding renderlayer
        :param oneRef:
        :return:
        """
        refSort = self.sort_asset2(oneRef)
        print(">>>     Deal with No.{} Referecen:  {}".format(self.assetRefs.index(oneRef),oneRef.path))
        if not oneRef.isLoaded():
            if not os.path.exists(oneRef.path):
                if 'Missed Reference File' in self.issue:
                    self.issue['Miss Reference File'].append(oneRef.path)
                else:
                    self.issue.update({'Miss Reference File':[oneRef.path]})
                return
            oneRef.load(prompt=False,f=True)
        refMembers = self._list_ref_members(oneRef)
        if not refMembers['topGrp']:
            self.issue.update({"Top Group Error":[oneRef.path]})
            mc.warning(">>> WARNING: Procedure Can not find the top group of current reference")
        if not refMembers['models']:
            self.issue.update({"Models Error": [oneRef.path]})
            mc.warning(">>> WARNING: Procedure Can not find the models of current reference")
        #----add on Apr 17 2021 ---- for arnold subdivision
        if refSort in ['PRO', 'CHR']:
            if refMembers['models']: self._aosubdivset_node.addMembers(refMembers['models'])
            else:
                if refMembers['topGrp']:self._aosubdivset_node.addMembers(refMembers['models'])
        #-------------------------------------------------------------
        # bgcolor
        bg_rndly = self._rndLayers['bg']
        if refSort in ['BG']:
            if refMembers['topGrp']:
                bg_rndly.addMembers(refMembers['topGrp'])
                print(">>>Add Top Grp to BG  renderLayer DONE!!!")
            else:
                print(">>> Missed Top Group...BG CLOR LAYER Failed!!!")
        #chcolor
        ch_lyer = self._rndLayers['ch']
        if refSort in ['PRO', 'CHR']:
            if refMembers['models']:
                try:
                    ch_lyer.addMembers(refMembers['models'])
                    print(">>>ADD Meshes to character color  Render Layer DONE!!!")
                except:
                    for m in refMembers['models']:
                        try:
                            ch_lyer.addMembers(m)
                        except:
                            m_shp = m.getShape()
                            try:
                                ch_lyer.addMembers(m_shp)
                            except:
                                mc.warning(">>> Oops!!! model can not add to {} layer".format(ch_lyer.name()))
                                if 'shadow layer issue' in self.issue:
                                    self.issue['ch color layer issue'].append(m_shp.name())
                                else:
                                    self.issue.update({'color layer issue': [m_shp.name()]})
            else:
                print(">>> Missed Modles ...chr CLOR LAYER Failed!!!")
        #chrgblgt
        chidp_lyer = self._rndLayers['chidp']
        if refSort in ['PRO', 'CHR']:
            if refMembers['models']:
                try:
                    chidp_lyer.addMembers(refMembers['models'])
                    print(">>>ADD Meshes to character idp  Render Layer DONE!!!")
                except:
                    for m in refMembers['models']:
                        try:
                            chidp_lyer.addMembers(m)
                        except:
                            m_shp = m.getShape()
                            try:
                                chidp_lyer.addMembers(m_shp)
                            except:
                                mc.warning(">>> Oops!!! model can not add to {} layer".format(chidp_lyer.name()))
                                if 'shadow layer issue' in self.issue:
                                    self.issue['ch idp layer issue'].append(m_shp.name())
                                else:
                                    self.issue.update({'ch idp layer issue': [m_shp.name()]})
            else:
                print(">>> Missed Modles ...chr IDP LAYER Failed!!!")
        # mask layer
        msk_lyer = self._rndLayers['mask']
        if refMembers['topGrp']:
            msk_lyer.addMembers(refMembers['topGrp'])
            print(">>>ADD Meshes to MASK Render Layer DONE!!!")
        else:
            print(">>> Missed Top Group...MASK LAYER Failed!!!")
        # shadow layer
        sh_lyer = self._rndLayers['shadow']
        if refMembers['models']:
            try:
                sh_lyer.addMembers(refMembers['models'])
                print(">>>ADD Meshes to shadow Render Layer DONE!!!")
            except:
                for m in refMembers['models']:
                    try:
                        sh_lyer.addMembers(m)
                    except:
                        m_shp = m.getShape()
                        try:
                            sh_lyer.addMembers(m_shp)
                        except:
                            mc.warning(">>> Oops!!! model can not add to {} layer".format(sh_lyer.name()))
                            if 'shadow layer issue' in self.issue:
                                self.issue['shadow layer issue'].append(m_shp.name())
                            else:
                                self.issue.update({'shadow layer issue': [m_shp.name()]})
            print(">>>Add Meshes to Shadow Layer DONE!!!")
        else:
            print(">>> Missed Models...Shadow LAYER Failed!!!")
        pm.editRenderLayerGlobals(currentRenderLayer=sh_lyer)
        overAttr_dict = {'BG': {'castsShadows':0},
                              'PRO': {'primaryVisibility':0},
                              'CHR': {'primaryVisibility':0} }
        for etrn in refMembers['models']:
            e_shp = etrn.getShape()
            for attr_nm,v in overAttr_dict[refSort].iteritems():
                overAttr = e_shp.attr(attr_nm)
                if overAttr.isLocked():continue
                pm.editRenderLayerAdjustment(overAttr, layer=sh_lyer)
                overAttr.set(v)
        print(">>>Shdow Layer Set Mesh PrimaryVisibility Done!!!")
        print(">>>...No.{} {} Asset layered.........<{}>".format(self.assetRefs.index(oneRef),refSort,oneRef.path))
    def _list_ref_members(self,oneRef):
        refTop = self.fn_getReferenceTopGrp(oneRef)
        models = [eshp.getParent() for eshp in refTop.getChildren(ad=True, type='mesh', ni=True) if
                     eshp.primaryVisibility.get()]
        return dict(topGrp = refTop,
                    models= models)

    @staticmethod
    def _fn_outputFolderTier(path, tier):
        u"""
            ????????????????????????????????????????????? ??????????????????
        :param path:
        :param tier:
        :return:
        """
        tier_1_pth = os.path.realpath(os.path.join(path, '../'))
        remain_tiers = os.path.realpath(os.path.join(path, '../' * tier))
        return os.path.relpath(tier_1_pth, remain_tiers)

    @staticmethod
    def fn_getReferenceTopGrp(oneRef):
        refTop = None
        for e_n in oneRef.nodes():
            if e_n.nodeType() == 'transform':
                if e_n.getShape():
                    if e_n.getShape().nodeType() in ['nurbsCurve']:
                        refTop = e_n
                        break
                    else:
                        continue
                else:
                    if not e_n.nodeType() in ['transform']: continue
                    else:
                        refTop = e_n
                        break
        return refTop
    @staticmethod
    def sort_asset(oneRef):
        """
            sort reference asset sort, return asset sort
        """
        refPathSplt = oneRef.path.split('/')
        for f in refPathSplt:
            if re.search("(PRO)|(CHR)|(BG)", f):
                return re.search("(PRO)|(CHR)|(BG)", f).group()
        return None
    def sort_asset2(self,oneRef):
        """
            via specified dir , estimate asset sort
        :param oneRef:
        :return:
        """
        refPath_union  = re.sub(r"\\","/",os.path.normpath(oneRef.path))
        re_chr = re.compile(self._assetDir_chr,re.I)
        if re_chr.search(refPath_union): return "CHR"
        re_prop = re.compile(self._assetDir_prop,re.I)
        if re_prop.search(refPath_union):return "PRO"
        re_setting = re.compile(self._assetDir_setting,re.I)
        if re_setting.search(refPath_union): return "BG"
        return None
    def fn_setFPS(self):
        pm.currentUnit(time='{}fps'.format(self._fps))

    def fn_setTimeRange(self):
        """

        :return:
        """
        print(".........................waiting.......................")
        pm.env.setMinTime(self._minTime)
        pm.env.setMaxTime(self._maxTime)
    def _setDefaultRenderGlobal(self):
        """
            set default render global node
        :return:
        """
        rndGlbNode = pm.PyNode("defaultRenderGlobals")
        rndGlbNode.animation.set(1)
        rndGlbNode.outFormatControl.set(0)
        rndGlbNode.putFrameBeforeExt.set(1)
        rndGlbNode.imageFilePrefix.set(self._outputPrefix)
        rndGlbNode.startFrame.set(self._minTime)
        rndGlbNode.endFrame.set(pm.env.maxTime)
    def fn_setRenderParameters(self):
        """
            about render setting
        :return:
        """
        self._setDefaultRenderGlobal()
        if self._renderer == 'arnold':
            pm.setAttr("defaultArnoldRenderOptions.abortOnError", 0)
            pm.setAttr("defaultArnoldDriver.ai_translator", 'exr', type='string')
            pm.setAttr("defaultArnoldDriver.mergeAOVs", 1)

    def fn_getAnimTimerange(self):
        pm.newFile(f=True)
        try:
            pm.openFile(self.anFile, loadNoReferences=True, f=True,prompt=False)
        except Exception as e:
            print(e)
            print("OPEN FILE FAILED: < {} >".format(self.anFile))
            # mc.error("...................Oops ...some issues....")
        self._minTime = pm.env.minTime
        self._maxTime = pm.env.maxTime
        pm.newFile(f=True)
    def _fn_detect_optOrNot(self):
        u"""
            ????????????????????????????????????????????????????????????????????? ???????????? ???????????????
        :return:
        """
        if os.path.isfile(self._srch_fpth_bg_spare) or os.path.isfile(self._srch_fpth_bg):
            self.layered_bg_already = True
        if os.path.isfile(self._srch_fpth_chr) or os.path.isfile(self._srch_fpth_chr_spare):
            self.layered_chr_already = True
        if self.layered_chr_already and self.layered_bg_already:
            if self.override: return True
            else: return False
        else:
            return True
    def fn_create_arnold_set(self,):
        """
            add a arnold subdivision set group
        :return:
        """

        if not mc.objExists(self._aoSubDivSet_name):
            mc.sets(name=self._aoSubDivSet_name,em=True)
            mc.addAttr(self._aoSubDivSet_name,ln='aiSubdivType',at='enum',en='none:catclark:linear',dv=1)
            mc.addAttr(self._aoSubDivSet_name,ln='aiSubdivIterations',at='byte',dv=2)
        self._aosubdivset_node = pm.PyNode(self._aoSubDivSet_name)

    def fn_allRefs2aoSubSet(self):
        """
            add all reference to subdiv set
        :return:
        """
        # --- determin arnold subdivision set
        self.fn_create_arnold_set()
        # ---- list top animation ref file.
        topAnimRef = pm.listReferences()[0]
        asset_refs = pm.listReferences(parentReference=topAnimRef)
        for e_ref in asset_refs:
            self.fn_add_ref_meshes2sets(e_ref)
        pm.saveFile(f=True)
        print(">>> Add Arnold Subdivision Sets Done!!!!..................................")
    def fn_add_ref_meshes2sets(self, oneRef):
        """
            add reference meshes to arnold sub div set
        :param oneRef:
        :return:
        """
        refSort = self.sort_asset2(oneRef)
        print(">>>     Deal with No.{} Referecen:  {}".format(self.assetRefs.index(oneRef), oneRef.path))
        if not oneRef.isLoaded():
            if not os.path.exists(oneRef.path):
                if 'Missed Reference File' in self.issue:
                    self.issue['Miss Reference File'].append(oneRef.path)
                else:
                    self.issue.update({'Miss Reference File': [oneRef.path]})
                return
            oneRef.load(prompt=False, f=True)
        refMembers = self._list_ref_members(oneRef)
        if not refMembers['topGrp']:
            self.issue.update({"Top Group Error": [oneRef.path]})
            mc.warning(">>> WARNING: Procedure Can not find the top group of current reference")
        if not refMembers['models']:
            self.issue.update({"Models Error": [oneRef.path]})
            mc.warning(">>> WARNING: Procedure Can not find the models of current reference")
        # ----add on Apr 17 2021 ---- for arnold subdivision
        if refSort in ['PRO', 'CHR']:
            if refMembers['models']:
                self._aosubdivset_node.addMembers(refMembers['models'])
            else:
                if refMembers['topGrp']: self._aosubdivset_node.addMembers(refMembers['models'])
        print(">>> add mesh or group  to subdivision set...........")
def _fn_findAllMayaFile(dir):
    opr_maya_files = []
    for root, dirnames, filenames in os.walk(dir):
        for filename in fnmatch.filter(filenames, '*.mb'):
            opr_maya_files.append(os.path.join(root, filename))
        for filename in fnmatch.filter(filenames, '*.ma'):
            opr_maya_files.append(os.path.join(root, filename))
    return opr_maya_files
def main(anim_dir,out_dir):
    if not os.path.isdir(out_dir): os.makedirs(out_dir)
    fileLst = _fn_findAllMayaFile(anim_dir)
    for e_f in fileLst:
        try:
            autoLayer = AnAutoLayer()
            autoLayer.reset()
            autoLayer.anFile = e_f
            # if saveRespective: autoLayer.save2folder = "{}/{}".format(up2_foldername,up1_foldername)
            autoLayer.saveHoldTiers = True
            autoLayer.save2dir = out_dir
            autoLayer.run_autoLayer()
        except Exception as e:
            print(e)


if __name__ == "__main__":
   main(sys.argv[1],sys.argv[2])
