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

from XSConsoleConfig import *
from XSConsoleLangErrors import *

import XenAPI # For XenAPI.Failure


# Global function
def Lang(inLabel, inPad = 0):
    retStr = Language.ToString(inLabel)
    if inPad > 0:
        retStr = retStr.ljust(inPad, ' ')
    return retStr
    
class Language:
    instance = None
    stringHook = None
    errorHook = None
    errorLoggingHook = None
    
    def __init__(self):
        self.brandingMap = Config.Inst().BrandingMap()
    
    @classmethod
    def SetStringHook(cls, inHook):
        cls.stringHook = inHook
    
    @classmethod
    def SetErrorHook(cls, inHook):
        cls.errorHook = inHook

    @classmethod
    def SetErrorLoggingHook(cls, inHook):
        cls.errorLoggingHook = inHook

    @classmethod
    def Inst(self):
        if self.instance is None:
            self.instance = Language()
        return self.instance
    
    @classmethod
    def Quantity(cls, inText, inNumber):
        if inNumber == 1:
            return Lang(inText)
        else:
            return Lang(inText+"s")

    @classmethod
    def XapiError(cls, inList):
        retVal = LangErrors.Translate(inList[0])
        for i in range(1, len(inList)):
            retVal = retVal.replace('{'+str(i-1)+'}', inList[i])
        return retVal

    @classmethod
    def LogError(cls, inValue): # For internal use
        if cls.errorLoggingHook is not None:
            cls.errorLoggingHook(inValue)
        if cls.errorHook is not None:
            cls.errorHook(inValue)

    @classmethod
    def ToString(cls, inLabel):
        if isinstance(inLabel, XenAPI.Failure):
            retVal = cls.XapiError(inLabel.details)
            cls.LogError(retVal)
        elif isinstance(inLabel, Exception):
            exn_strings = []
            for arg in inLabel.args:
                if isinstance(arg, unicode):
                    exn_strings.append(arg.encode('utf-8'))
                else:
                    exn_strings.append(str(arg))
            retVal = str(tuple(exn_strings))
            cls.LogError(retVal)
        else:
            if isinstance(inLabel, unicode):
                inLabel = inLabel.encode('utf-8')
            retVal = inLabel
            if cls.stringHook is not None:
                cls.stringHook(retVal)
        return retVal

    @classmethod
    def ReflowText(cls, inText, inWidth):
        # Return an array of string that are at most inWidth characters long
        retArray = []
        text = inText+" "
        while len(text) > 0:
            spacePos = text.rfind(' ', 0, inWidth+1) # returns max (lastParam-1), i.e. 'aaaaa'.rfind('a', 0, 3) == 2
            retPos = text.find("\r", 0, inWidth+1)
            if retPos == -1:
                retPos = text.find("\n", 0, inWidth+1)
            if retPos != -1:
                spacePos = retPos
            if spacePos == -1:
                lineLength = inWidth
            else:
                lineLength = spacePos
            
            thisLine = text[:lineLength]
            thisLine = thisLine.replace("\t", " ") # Tab is used as a non-breaking space
            thisLine = thisLine.replace("\r", "RET") # Debugging
            thisLine = thisLine.strip() # Remove leading whitespace (generally the second space in a double space)
            if len(thisLine) > 0 or retPos != -1: # Only add blank lines if they follow a return
                retArray.append(thisLine)
            
            if spacePos == -1:
                text = text[lineLength:] # Split at non-space/return, so keep
            else:
                text = text[lineLength+1:] # Split at space or return so discard
            
        return retArray

    def Branding(self, inText):
        # Return either the value in the hash or (if not present) the unchanged parameter
        return self.brandingMap.get(inText, inText)
