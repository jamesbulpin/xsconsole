# Copyright (c) 2007-2009 Citrix Systems Inc.
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

import re

from XSConsoleAuth import *
from XSConsoleBases import *
from XSConsoleConfig import *
from XSConsoleCurses import *
from XSConsoleData import *
from XSConsoleDialoguePane import *
from XSConsoleDialogueBases import *
from XSConsoleFields import *
from XSConsoleImporter import *
from XSConsoleLang import *
from XSConsoleMenus import *

class RootDialogue(Dialogue):
    
    def __init__(self, inLayout, inParent):
        Dialogue.__init__(self, inLayout, inParent)
        menuPane = self.NewPane(DialoguePane(self.parent, PaneSizerFixed(1, 2, 39, 21)), 'menu')
        menuPane.ColoursSet('MENU_BASE', 'MENU_BRIGHT', 'MENU_HIGHLIGHT', 'MENU_SELECTED')
        statusPane = self.NewPane(DialoguePane(self.parent, PaneSizerFixed(40, 2, 39, 21)), 'status')
        statusPane.ColoursSet('HELP_BASE', 'HELP_BRIGHT', None, None, None, 'HELP_FLASH')
        self.menu = Importer.BuildRootMenu(self)
        self.menuName = 'MENU_ROOT'
        self.UpdateFields()

    def UpdateFields(self):
        self.menu.SetMenu(self.menuName, Importer.RegenerateMenu(self.menuName, self.menu.GetMenu(self.menuName)))
        currentMenu = self.menu.CurrentMenu()
        currentChoiceDef = currentMenu.CurrentChoiceDef()

        menuPane = self.Pane('menu')
        menuPane.ResetFields()
        menuPane.ResetPosition()
        menuPane.AddTitleField(currentMenu.Title())

        menuPane.AddMenuField(currentMenu, 16) # Allow extra height for this menu
        
        statusPane = self.Pane('status')

        try:
            statusPane.ResetFields()
            statusPane.ResetPosition()
            
            statusUpdateHandler = currentChoiceDef.StatusUpdateHandler()
            if statusUpdateHandler is not None:
                if currentChoiceDef.handle is not None:
                    statusUpdateHandler(statusPane, currentChoiceDef.handle)
                else:
                    statusUpdateHandler(statusPane)
                    
            else:
                raise Exception(Lang("Missing status handler"))

        except Exception, e:
            statusPane.ResetFields()
            statusPane.ResetPosition()
            statusPane.AddTitleField(Lang("Information not available"))
            statusPane.AddWrappedTextField(Lang(e))
        
        keyHash = { Lang("<Up/Down>") : Lang("Select") }
        if self.menu.CurrentMenu().Parent() != None:
            keyHash[ Lang("<Esc/Left>") ] = Lang("Back")
        else:
            if currentChoiceDef.OnAction() is not None:
                keyHash[ Lang("<Enter>") ] = Lang("OK")

        menuPane.AddKeyHelpField( keyHash )
        
        if statusPane.NumStaticFields() == 0: # No key help yet
            if statusPane.NeedsScroll():
                statusPane.AddKeyHelpField( {
                    Lang("<Page Up/Down>") : Lang("Scroll"),
                    Lang("<F5>") : Lang("Refresh"),
                })
    
    def HandleKey(self, inKey):
        currentMenu = self.menu.CurrentMenu()

        handled = currentMenu.HandleKey(inKey)

        if not handled and inKey == 'KEY_PPAGE':
            self.Pane('status').ScrollPageUp()
            handled = True
            
        if not handled and inKey == 'KEY_NPAGE':
            self.Pane('status').ScrollPageDown()
            handled = True
            
        if handled:
            self.UpdateFields()
            self.Pane('menu').Refresh()
            self.Pane('status').Refresh()
            
        return handled

    def ChangeMenu(self, inName):
        self.menu.SetMenu(inName, Importer.RegenerateMenu(inName, self.menu.GetMenu(inName)))
        self.menuName = inName
        self.menu.ChangeMenu(inName)
        self.menu.CurrentMenu().HandleEnter()
    
    def Reset(self):
        self.menu.Reset()
        self.UpdateFields()
        self.Pane('menu').Refresh()
        self.Pane('status').Refresh()
