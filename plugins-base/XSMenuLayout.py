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

class XSMenuLayout:
    def UpdateFieldsPROPERTIES(self, inPane):

        inPane.AddTitleField(Lang("Hardware and BIOS Information"))
    
        inPane.AddWrappedTextField(Lang("Press <Enter> to view processor, memory, disk controller and BIOS details for this system."))
        
    def UpdateFieldsAUTH(self, inPane):

        inPane.AddTitleField(Lang("Authentication"))
    
        if Auth.Inst().IsAuthenticated():
            username = Auth.Inst().LoggedInUsername()
        else:
            username = "<none>"

        inPane.AddStatusField(Lang("User", 14), username)
        
        inPane.NewLine()
        
        if Auth.Inst().IsAuthenticated():
            inPane.AddWrappedTextField(Lang("You are logged in."))
        else:
            inPane.AddWrappedTextField(Lang("You are currently not logged in."))

        inPane.NewLine()
        inPane.AddWrappedTextField(Lang("Only logged in users can reconfigure and control this server.  "
            "Press <Enter> to change the login password and auto-logout timeout."))
        
        inPane.AddKeyHelpField( { Lang("<F5>") : Lang("Refresh")})


    def UpdateFieldsNETWORK(self, inPane):
        data = Data.Inst()
        
        inPane.AddTitleField(Lang("Network and Management Interface"))
        
        inPane.AddWrappedTextField(Lang("Press <Enter> to configure the management network connection, hostname, and network time (NTP) settings."))
        inPane.NewLine()

        if len(data.derived.managementpifs([])) == 0:
            inPane.AddWrappedTextField(Lang("Currently, no management interface is configured."))
        else:
            inPane.AddTitleField(Lang("Current Management Interface"))
            if data.chkconfig.ntpd(False):
                ntpState = 'Enabled'
            else:
                ntpState = 'Disabled'
            
            for pif in data.derived.managementpifs([]):
                inPane.AddStatusField(Lang('Device', 16), pif['device'])
                inPane.AddStatusField(Lang('MAC Address', 16),  pif['MAC'])
                inPane.AddStatusField(Lang('DHCP/Static IP', 16),  pif['ip_configuration_mode'])

                inPane.AddStatusField(Lang('IP address', 16), data.ManagementIP(''))
                inPane.AddStatusField(Lang('Netmask', 16),  data.ManagementNetmask(''))
                inPane.AddStatusField(Lang('Gateway', 16),  data.ManagementGateway(''))
                inPane.AddStatusField(Lang('Hostname', 16),  data.host.hostname(''))
                inPane.AddStatusField(Lang('NTP', 16),  ntpState)

        inPane.AddKeyHelpField( { Lang("<F5>") : Lang("Refresh")})
            
    def UpdateFieldsMANAGEMENT(self, inPane):
        data = Data.Inst()
                
        inPane.AddTitleField(Lang("Keyboard and Timezone"))
    
        inPane.AddWrappedTextField(Lang(
            "This menu configures keyboard language and timezone."))
        
        inPane.NewLine()
        if data.timezones.current('') != '':
            inPane.AddWrappedTextField(Lang("The current timezone is"))
            inPane.NewLine()
            inPane.AddWrappedTextField(data.timezones.current(Lang('<Unknown>')))
            inPane.NewLine()
            
        if data.keyboard.currentname('') != '':
            inPane.AddWrappedTextField(Lang("The current keyboard type is"))
            inPane.NewLine()
            inPane.AddWrappedTextField(data.keyboard.currentname(Lang('<Default>')))

    def UpdateFieldsVM(self, inPane):
        hotData = HotData.Inst()

        inPane.AddTitleField(Lang("Virtual Machines"))
        
        inPane.AddWrappedTextField(Lang('Press <Enter> to view the Virtual Machines menu.  This menu '
            'can start, stop and migrate existing Virtual Machines on this host, and display '
            'performance information.'))
        inPane.NewLine()

    def UpdateFieldsDISK(self, inPane):
        data = Data.Inst()
        inPane.AddTitleField(Lang("Disks and Storage Repositories"))
    
        inPane.AddWrappedTextField(Lang("Press <Enter> to create and attach Storage Repositories, select local  "
            "disks to use as Storage Repositories, "
            "and specify destinations for Suspend and Crash Dump images for this host."))
        inPane.NewLine()
    
        inPane.AddWrappedBoldTextField(Lang('Suspend Image SR'))
        if data.host.suspend_image_sr(False):
            inPane.AddWrappedTextField(data.host.suspend_image_sr.name_label())
        else:
            inPane.AddWrappedTextField(Lang('<Not Configured>'))
            
        inPane.NewLine()
            
        inPane.AddWrappedBoldTextField(Lang('Crash Dump SR'))
        if data.host.crash_dump_sr(False):
            inPane.AddWrappedTextField(data.host.crash_dump_sr.name_label())
        else:
            inPane.AddWrappedTextField(Lang('<Not Configured>'))
            
        inPane.AddKeyHelpField( {
            Lang("<F5>") : Lang("Refresh")
        })
    
    def UpdateFieldsPOOL(self, inPane):
        data = Data.Inst()
        inPane.AddTitleField(Lang("Resource Pool Configuration"))
    
        inPane.AddWrappedTextField(Lang('A Resource Pool allows a number of hosts to share resources '
            'and migrate running Virtual Machines between hosts.  Press <Enter> to add this host a Resource Pool '
            'or remove it from its current Pool.'))
        inPane.NewLine()

    def UpdateFieldsREBOOTSHUTDOWN(self, inPane):
        inPane.AddTitleField(Lang("Reboot or Shutdown"))
    
        inPane.AddWrappedTextField(Lang(
            "This option can reboot or shutdown this server, and enter or exit Maintenance Mode."))
        
    def UpdateFieldsTECHNICAL(self, inPane):
        inPane.AddTitleField(Lang("Technical Support"))
    
        inPane.AddWrappedTextField(Lang(
            "From this menu you can "
            "validate the configuration of this server and upload or save bug reports."))

    def UpdateFieldsREMOTE(self, inPane):
        data = Data.Inst()
        inPane.AddTitleField(Lang("Remote Service Configuration"))
    
        inPane.AddWrappedTextField(Lang("This menu configures remote services, such as access by "
            "remote shell (ssh) and remote logging (syslog) to other servers."))

    def UpdateFieldsBUR(self, inPane):
        inPane.AddTitleField(Lang("Backup, Restore and Update"))
   
        inPane.AddWrappedTextField(Lang(
            "From this menu you can backup and restore the system database and Virtual Machine metadata, and apply "
            "software updates to the system."))

    def ActivateHandler(self, inName):
        Layout.Inst().TopDialogue().ChangeMenu(inName)

    def Register(self):
        data = Data.Inst()
        
        rootMenuDefs = [
            [ 'MENU_NETWORK', Lang("Network and Management Interface"),
                lambda: self.ActivateHandler('MENU_NETWORK'), self.UpdateFieldsNETWORK ],
            [ 'MENU_AUTH', Lang("Authentication"),
                lambda: self.ActivateHandler('MENU_AUTH'), self.UpdateFieldsAUTH ],
            [ 'MENU_VM', Lang("Virtual Machines"),
                lambda: self.ActivateHandler('MENU_VM'), self.UpdateFieldsVM ],
            [ 'MENU_DISK', Lang("Disks and Storage Repositories"),
                lambda: self.ActivateHandler('MENU_DISK'), self.UpdateFieldsDISK ],
            [ 'MENU_POOL', Lang("Resource Pool Configuration"),
                lambda: self.ActivateHandler('MENU_POOL'), self.UpdateFieldsPOOL],
            [ 'MENU_PROPERTIES', Lang("Hardware and BIOS Information"),
                lambda: self.ActivateHandler('MENU_PROPERTIES'), self.UpdateFieldsPROPERTIES ],
            [ 'MENU_MANAGEMENT', Lang("Keyboard and Timezone"),
                lambda: self.ActivateHandler('MENU_MANAGEMENT'), self.UpdateFieldsMANAGEMENT ],
            [ 'MENU_REMOTE', Lang("Remote Service Configuration"),
                lambda: self.ActivateHandler('MENU_REMOTE'), self.UpdateFieldsREMOTE ],
            [ 'MENU_BUR', Lang("Backup, Restore and Update"),
                lambda: self.ActivateHandler('MENU_BUR'), self.UpdateFieldsBUR ],
            [ 'MENU_TECHNICAL', Lang("Technical Support"),
                lambda: self.ActivateHandler('MENU_TECHNICAL'), self.UpdateFieldsTECHNICAL ],
            [ 'MENU_REBOOTSHUTDOWN', Lang("Reboot or Shutdown"),
                lambda: self.ActivateHandler('MENU_REBOOTSHUTDOWN'), self.UpdateFieldsREBOOTSHUTDOWN ]
        ]
        
        priority = 100
        for menuDef in rootMenuDefs:

            Importer.RegisterMenuEntry(
                self,
                'MENU_ROOT', # Name of the menu this item is part of
                {
                    'menuname' : menuDef[0], # Name of the menu this item leads to when selected
                    'menutext' : menuDef[1],
                    'menupriority' : priority,
                    'activatehandler' : menuDef[2],
                    'statusupdatehandler' : menuDef[3]
                }
            )
            priority += 100

# Register this plugin when module is imported
XSMenuLayout().Register()
