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

class OEMBackupDialogue(FileDialogue):
    def __init__(self):

        self.custom = {
            'title' : Lang("Backup Server State"),
            'searchregexp' : r'.*\.xbk$',  # Type of backup file is .xbk
            'deviceprompt' : Lang("Select the backup device"), 
            'fileprompt' : Lang("Choose the backup filename"),
            'filename' : 'backup.xbk',
            'confirmprompt' : Lang("Press <F8> to begin the backup process"),
            'mode' : 'rw'
        }
        FileDialogue.__init__(self) # Must fill in self.custom before calling __init__
        
    def DoAction(self):
        filename = self.vdiMount.MountedPath(self.filename)
        if os.path.isfile(filename):
            Layout.Inst().PushDialogue(QuestionDialogue(
                Lang("File already exists.  Do you want to overwrite it?"), lambda x: self.DoOverwriteChoice(x)))
        else:
            self.DoCommit()
    
    def DoOverwriteChoice(self, inChoice):
        if inChoice == 'y':
            filename = self.vdiMount.MountedPath(self.filename)
            os.remove(filename)
            self.DoCommit()
        else:
            self.ChangeState('FILES')
    
    def DoCommit(self):
        success = False
        
        Layout.Inst().PopDialogue()
        
        Layout.Inst().PushDialogue(BannerDialogue(
            Lang("Saving to backup... This may take several minutes.  Press <Ctrl-C> to abort.")))
            
        try:
            try:
                Layout.Inst().Refresh()
                Layout.Inst().DoUpdate()
                
                hostRef = Data.Inst().host.uuid(None)
                if hostRef is None:
                    raise Exception("Internal error 1")
                    
                filename = self.vdiMount.MountedPath(self.filename)
                FileUtils.AssertSafePath(filename)
                command = "/opt/xensource/bin/xe host-backup file-name='"+filename+"' host="+hostRef
                status, output = commands.getstatusoutput(command)
                
                if status != 0:
                    raise Exception(output)
                
                Layout.Inst().PopDialogue()
                Layout.Inst().PushDialogue(InfoDialogue(
                    Lang("Backup Successful")))
                XSLog('Backup successful')

            except Exception, e:
                try: os.unlink(filename)
                except: pass
                Layout.Inst().PopDialogue()
                Layout.Inst().PushDialogue(InfoDialogue( Lang("Backup Failed"), Lang(e)))
                
        finally:
            try:
                self.PreExitActions()
            except Exception, e:
                Layout.Inst().PushDialogue(InfoDialogue( Lang("Backup Failed"), Lang(e)))


class XSFeatureOEMBackup:
    @classmethod
    def StatusUpdateHandler(cls, inPane):
        data = Data.Inst()
        inPane.AddTitleField(Lang("Backup Server State"))

        inPane.AddWrappedTextField(Lang(
            "Press <Enter> to backup the server state to removable media."))
            
        inPane.AddKeyHelpField( { Lang("<Enter>") : Lang("Backup") } ) 
        
    @classmethod
    def ActivateHandler(cls):
        DialogueUtils.AuthenticatedOnly(lambda: Layout.Inst().PushDialogue(OEMBackupDialogue()))
        
    def Register(self):
        Importer.RegisterNamedPlugIn(
            self,
            'BACKUP', # Key of this plugin for replacement, etc.
            {
                'menuname' : 'MENU_BUR',
                'menupriority' : 200,
                'menutext' : Lang('Backup Server State') ,
                'statusupdatehandler' : self.StatusUpdateHandler,
                'activatehandler' : self.ActivateHandler
            }
        )

# Register this plugin when module is imported
XSFeatureOEMBackup().Register()
