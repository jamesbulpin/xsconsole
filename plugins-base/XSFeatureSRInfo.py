# Copyright (c) 2008-2009 Citrix Systems Inc.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; version 2 only.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

if __name__ == "__main__":
    raise Exception("This script is a plugin for xsconsole and cannot run independently")
    
from XSConsoleStandard import *

class XSFeatureSRInfo:
    
    @classmethod
    def StatusUpdateHandler(cls, inPane):
        inPane.AddTitleField(Lang("Storage Repository Information"))
    
        inPane.AddWrappedTextField(Lang(
            "Press <Enter> to display detailed information about Storage Repositories, and to Detach, Destroy or Forget Storage Repositories."))

    @classmethod
    def NoSRStatusUpdateHandler(cls, inPane):
        inPane.AddTitleField(Lang("Storage Repository Information"))

        inPane.AddWrappedTextField(Lang("There are no Storage Repositories known to this host."))

    @classmethod
    def InfoStatusUpdateHandler(cls, inPane, inHandle):
        db = HotAccessor()
        srUtils = Importer.GetResource('SRUtils')
        sr = db.sr[inHandle]
        if sr is None:
            inPane.AddWrappedTextField(Lang("This Storage Repository is no longer present"))
        else:
            inPane.AddWrappedBoldTextField(sr.name_label(Lang('<Name Unknown>')))

            inPane.NewLine()
            if int(sr.physical_size(0)) != 0:
                freeSize = int(sr.physical_size(0)) - int(sr.physical_utilisation(0))
                inPane.AddStatusField(Lang('Size', 10), SizeUtils.SRSizeString(sr.physical_size(0)) +
                    Lang(' total, '+SizeUtils.SRSizeString(freeSize)+Lang(' free')))
            inPane.AddStatusField(Lang('Type', 10), srUtils.TypeName(sr.type()))

            inPane.AddStatusField(Lang('Shared', 10), sr.shared() and Lang('Yes') or Lang('No'))
            
            attached = False
            for pbd in sr.PBDs:
                if pbd.host.uuid() == db.local_host.uuid():
                    if pbd.currently_attached(False):
                        attached = True
                    devConfig = pbd.device_config
                    if devConfig.location() is not None:
                        inPane.AddStatusField(Lang('Location', 10), devConfig.location())
                    if devConfig.device() is not None:
                        inPane.AddStatusField(Lang('Device', 10), devConfig.device())
                    if devConfig.server() is not None and devConfig.serverpath() is not None:
                        inPane.AddStatusField(Lang('Server', 10), devConfig.server()+':'+devConfig.serverpath())
                    if devConfig.SCSIid() is not None:
                        inPane.AddStatusField(Lang('SCSI ID', 10), devConfig.SCSIid())
                    if devConfig.target() is not None:
                        inPane.AddStatusField(Lang('Target', 10), devConfig.target())
                    if devConfig.port() is not None:
                        inPane.AddStatusField(Lang('Port', 10), devConfig.port())
                    if devConfig.targetIQN() is not None:
                        inPane.AddStatusField(Lang('Target IQN', 10), devConfig.targetIQN())
            

            flags = srUtils.SRFlags(sr)
            if 'default' in flags and 'suspend' in flags and 'crashdump' in flags:
                default = Lang('Yes')
            elif 'default' in flags or 'suspend' in flags or 'crashdump' in flags:
                default = Lang('Partial')
            else:
                default = Lang('No')
            inPane.AddStatusField(Lang('Default', 10), default)

            inPane.NewLine()
            if len(sr.PBDs()) == 0:
                inPane.AddWarningField(Lang('This Storage Repository is detached and not usable by this host.'))
            elif not attached:
                inPane.AddWarningField(Lang('This Storage Repository is unplugged and not usable by this host.'))
                
            if sr.name_description('') != '':
                inPane.AddWrappedBoldTextField(Lang('Description'))
                inPane.AddWrappedTextField(sr.name_description(''))

        inPane.AddKeyHelpField( { Lang("<Enter>") : Lang("Control This Storage Repository") } )
    
    @classmethod
    def ActivateHandler(cls):
        Layout.Inst().TopDialogue().ChangeMenu('MENU_SRINFO')
    
    @classmethod
    def InfoActivateHandler(cls, inHandle):
        dialogue = Importer.GetResource('SRControlDialogue')
        DialogueUtils.AuthenticatedOnly(lambda: Layout.Inst().PushDialogue(dialogue(inHandle)))
    
    @classmethod
    def MenuRegenerator(cls, inList, inMenu):
        retVal = copy.copy(inMenu)
        retVal.RemoveChoices()
        # inList is a list of HotOpaqueRef objects
        srList = [ sr for sr in HotAccessor().visible_sr if sr.other_config({}).get('xensource_internal', '') != 'true' ]
        
        # Sort list by SR shared flag then name
        srList.sort(lambda x, y: cmp(y.shared(False), x.shared(False)) or cmp (x.name_label(''), y.name_label()))
        
        srUtils = Importer.GetResource('SRUtils')
        for sr in srList:
            name = srUtils.AnnotatedName(sr)
            retVal.AddChoice(name = name,
                                        onAction = cls.InfoActivateHandler,
                                        statusUpdateHandler = cls.InfoStatusUpdateHandler,
                                        handle = sr.HotOpaqueRef())
            
        if retVal.NumChoices() == 0:
            retVal.AddChoice(name = Lang('<No Storage Repositories Present>'),
                statusUpdateHandler = cls.NoSRStatusUpdateHandler)
            
        return retVal

    
    def Register(self):
        Importer.RegisterMenuEntry(
            self,
            'MENU_DISK', # Name of the menu this item is part of
            {
                'menuname' : 'MENU_SRINFO', # Name of the menu this item leads to when selected
                'menutext' : Lang('Current Storage Repositories'),
                'menupriority' : 100,
                'menuregenerator' : XSFeatureSRInfo.MenuRegenerator,
                'activatehandler' : XSFeatureSRInfo.ActivateHandler,
                'statusupdatehandler' : XSFeatureSRInfo.StatusUpdateHandler
            }
        )

# Register this plugin when module is imported
XSFeatureSRInfo().Register()
