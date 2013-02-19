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

class SyslogDialogue(InputDialogue):
    def __init__(self):
        self.custom = {
            'title' : Lang("Change Logging Destination"),
            'info' : Lang("Please enter the hostname or IP address for remote logging (or blank for none)"), 
            'fields' : [ [Lang("Destination", 20), Data.Inst().host.logging.syslog_destination(''), 'destination'] ]
            }
        InputDialogue.__init__(self)

    def HandleCommit(self, inValues):
        Layout.Inst().TransientBanner(Lang("Setting Logging Destination..."))

        hostname = inValues['destination']
        if hostname != '':
            IPUtils.AssertValidNetworkName(hostname)
        Data.Inst().LoggingDestinationSet(hostname)
        Data.Inst().Update()

        if hostname == '':
            message = Lang("Remote logging disabled.")
        else:
            message = Lang("Logging destination set to '")+hostname + "'."
        return Lang('Logging Destination Change Successful'), message        


class XSFeatureSyslog:
    @classmethod
    def StatusUpdateHandler(cls, inPane):
        data = Data.Inst()
        inPane.AddTitleField(Lang("Remote Logging (syslog)"))
    
        if data.host.logging.syslog_destination('') == '':
            inPane.AddWrappedTextField(Lang("Remote logging is not configured on this host.  Press <Enter> to activate and set a destination address."))
        else:
            inPane.AddWrappedTextField(Lang("The remote logging destination for this host is"))
            inPane.NewLine()
            inPane.AddWrappedTextField(data.host.logging.syslog_destination())
        
        inPane.AddKeyHelpField( {
            Lang("<Enter>") : Lang("Reconfigure"),
            Lang("<F5>") : Lang("Refresh")
        })
        
    @classmethod
    def ActivateHandler(cls):
        DialogueUtils.AuthenticatedOnly(lambda: Layout.Inst().PushDialogue(SyslogDialogue()))
        
    def Register(self):
        Importer.RegisterNamedPlugIn(
            self,
            'SYSLOG', # Key of this plugin for replacement, etc.
            {
                'menuname' : 'MENU_REMOTE',
                'menupriority' : 100,
                'menutext' : Lang('Remote Logging (syslog)') ,
                'statusupdatehandler' : self.StatusUpdateHandler,
                'activatehandler' : self.ActivateHandler
            }
        )

# Register this plugin when module is imported
XSFeatureSyslog().Register()
