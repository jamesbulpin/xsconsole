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

from XSConsoleBases import *
from XSConsoleLang import *

class Field:
    FLOW_INVALID=0
    FLOW_NONE=1
    FLOW_RIGHT=2
    FLOW_RETURN=3
    FLOW_DOUBLERETURN=4

    LAYOUT_MINWIDTH = 48 # Minimum width for dialogue

    def Flow(self):
        return self.flow

    def UpdateWidth(self, inWidth):
        pass

class SeparatorField(Field):
    def __init__(self, flow):
        ParamsToAttr()
        
    def Render(self, inPane, inX, inY):
        pass

    def Width(self):
        return 0

    def Height(self):
        return 1

class InputField(Field):
    MIN_WIDTH = 40 # Minimum width for input fields
    
    def __init__(self, text, colour, selectedColour, flow, lengthLimit):
        ParamsToAttr()
        self.activated = False
        self.cursorPos = len(self.text)
        self.hideText = False
        self.selected = True
        self.scrollPos = 0
        self.width = self.MIN_WIDTH
        if self.lengthLimit is None:
            self.lengthLimit = 4096
        
    def HideText(self):
        self.hideText = True
    
    def Activate(self):
        self.activated = True
        self.cursorPos = len(self.text)
        self.selected = (len(self.text) > 0)
        
    def Deactivate(self):
        self.activated = False
    
    def Content(self):
        return self.text
    
    def UpdateWidth(self, inWidth):
        self.width = max(self.MIN_WIDTH, inWidth)
        
    def Render(self, inPane, inX, inY):
        colour = self.colour
        suffix = ' '
        if self.selected and self.activated:
            colour = self.selectedColour
            suffix = ''
        
        # Adjust scroll point so that the cursor is within the field area
        self.scrollPos = min(self.scrollPos, self.cursorPos) # Move if cursor is outside of field to left
        self.scrollPos = max(self.scrollPos, self.cursorPos - self.width + 1) # Move if cursor is outside of field to right
        
        clippedStr = self.text
        # Move according to scrollPos
        clippedStr = clippedStr[self.scrollPos:]
        # Clip on right edge
        clippedStr = clippedStr[:self.width]
        
        
        if self.hideText:
            inPane.AddText("*" * len(clippedStr)+suffix, inX, inY, colour)
        else:
            inPane.AddText(clippedStr+suffix, inX, inY, colour)
        if self.selected:
            # Make cursor the right colour
            inPane.AddText(' ', inX+len(clippedStr), inY, self.colour)
            
        if self.activated:
            inPane.CursorOn(inX+self.cursorPos-self.scrollPos, inY)

    def Width(self):
        return max(self.MIN_WIDTH, len(self.text))
    
    def Height(self):
        return 1
        
    def HandleKey(self, inKey):
        handled = True
        
        if self.selected: # Handle keypress when the input text is selected
            if inKey == 'KEY_LEFT' or inKey == 'KEY_HOME':
               self.cursorPos = 0 # Move cursor to start
            elif inKey == 'KEY_RIGHT' or inKey == 'KEY_END':
                pass # Leave cursor at end
            elif inKey == 'KEY_UP' or inKey == 'KEY_DOWN':
                pass # Don't delete
            else:
                self.text = '' # First keypress deletes text
            self.selected = False
            
        # Constain cursor within string (in case we deleted the string contents above)
        self.cursorPos = min(self.cursorPos, len(self.text))

        if inKey == 'KEY_LEFT':
            self.cursorPos = max(0, self.cursorPos - 1) # Move cursor left
        elif inKey == 'KEY_RIGHT':
            self.cursorPos = min(len(self.text), self.cursorPos + 1) #Move cursor right
        elif inKey == 'KEY_HOME':
            self.cursorPos = 0 #Move cursor to home
        elif inKey == 'KEY_END':
            self.cursorPos = len(self.text) #Move cursor to end
        elif inKey == 'KEY_DC':
            self.text = self.text[:self.cursorPos] + self.text[self.cursorPos+1:] # Delete on right
        elif inKey == 'KEY_BACKSPACE':
            if (self.cursorPos > 0):
                self.cursorPos -= 1
                self.text = self.text[:self.cursorPos] + self.text[self.cursorPos+1:] # Delete on left
        elif len(inKey) == 1 and inKey[0] >= ' ':
            if len(self.text) < self.lengthLimit:
                self.text = self.text[:self.cursorPos] + inKey[0] + self.text[self.cursorPos:] # Insert char
                self.cursorPos += 1
        else:
            handled = False
        return handled

class TextField(Field):
    def __init__(self, text, colour, flow):
        ParamsToAttr()
        
    def Render(self, inPane, inX, inY):
        inPane.AddWrappedText(self.text, inX, inY, self.colour)

    def Width(self):
        return len(self.text)

    def Height(self):
        return 1
        
class WrappedTextField(Field):
    def __init__(self, text, colour, flow):
        ParamsToAttr()
        self.wrappedWidth = None
        self.wrappedText = []
        self.centred = False
        
    def SetCentred(self):
        self.centred = True
        
    def UpdateWidth(self, inWidth):
        if self.wrappedWidth is None or self.wrappedWidth != inWidth:
            self.wrappedWidth = inWidth
            self.wrappedText = Language.ReflowText(self.text, self.wrappedWidth)

    def Render(self, inPane, inXPos, inYPos):
        yPos = inYPos
        for line in self.wrappedText:
            if self.centred:
                offset = (self.wrappedWidth - len(line)) / 2
                inPane.AddText(line, inXPos+offset, yPos, self.colour)
            else:
                inPane.AddText(line, inXPos, yPos, self.colour)
                        
            yPos += 1

    def Width(self):
        retVal = 1
        for line in self.wrappedText:
            retVal = max(retVal, len(line))
        return retVal

    def Height(self):
        return max(1, len(self.wrappedText))

class MenuField(Field):
    def __init__(self, menu, colour, highlight, height, flow):
        ParamsToAttr()
        self.scrollPoint = 0
        self.height = min(self.height, len(self.menu.ChoiceDefs()))
    
    def Width(self):
        if len(self.menu.ChoiceDefs()) == 0:
            return 0
        return max(len(choice.name) for choice in self.menu.ChoiceDefs() )

    def Height(self):
        return self.height
        
    def Render(self, inPane, inXPos, inYPos):
        # This rendering doesn't necessarily deal with scrolling menus where the choice names
        # are of different lengths.  More erase/overwrite operations may be required to do that.
        
        # Move the scroll point if the selected option would otherwise be off the screen
        choiceIndex = self.menu.ChoiceIndex()
        if self.scrollPoint > choiceIndex:
            # Move so the choiceIndex is at the top
            self.scrollPoint = choiceIndex
        elif self.scrollPoint + self.height <= choiceIndex:
            # Move so the choiceIndex is at the bottom
            self.scrollPoint = choiceIndex - self.height + 1

        choiceDefs = self.menu.ChoiceDefs()
        for i in range(min(self.height, len(choiceDefs) - self.scrollPoint)):
            choiceNum = self.scrollPoint + i
            if choiceNum == choiceIndex:
                colour = self.highlight
            else:
                colour = self.colour
                
            inPane.AddText(choiceDefs[choiceNum].name, inXPos, inYPos + i, colour)

class FieldGroup:
    def __init__(self):
        self.Reset()
        
    def Reset(self):
        self.bodyFields = []
        self.bodyFieldNames = []
        self.staticFields = []
        self.staticFieldNames = []
        # Fields are ordered, so the order of field names is recorded here and the fields themselves are in bodyFields
        self.inputOrder = []
        self.inputTags = {}
        
    def NumStaticFields(self):
        return len(self.staticFields)

    def NumInputFields(self):
        return len(self.inputOrder)

    def BodyFields(self):
        return self.bodyFields

    def StaticFields(self):
        return self.staticFields

    def InputField(self, inIndex):
        return self.inputOrder[inIndex]
        
    def BodyFieldAdd(self, inTag, inField):
        self.bodyFields.append(inField)
        
    def StaticFieldAdd(self, inTag, inField):
        self.staticFields.append(inField)
    
    def InputFieldAdd(self, inTag, inField):
        # Three reference to the same field
        self.inputTags[inTag] = inField
        self.inputOrder.append(inField)
        self.bodyFields.append(inField)

    def GetFieldValues(self):
        retVal = {}
        for key, field in self.inputTags.iteritems():
            retVal[key] = field.Content()

        return retVal
        
class FieldArranger:
    BOXWIDTH = 1
    BORDER = 1
    
    def __init__(self, inFieldGroup, inXSize, inYSize):
        self.fieldGroup = inFieldGroup
        self.baseXSize = inXSize
        self.baseYSize = inYSize
        self.hasBox = False
        self.Reset()
    
    def Reset(self):
        self.layoutXSize = None
        self.layoutYSize = None
        
    def XSizeSet(self, inXSize):
        self.baseXSize = inXSize
        self.layoutXSize = None
        self.layoutYSize = None
    
    def YSizeSet(self, inYSize):
        self.baseYSize = inYSize
        self.layoutXSize = None
        self.layoutYSize = None
    
    def XSize(self):
        if self.layoutXSize is None:
            self.layoutXSize = max(self.BodyLayout().pop().xpos, self.StaticLayout().pop().xpos)
        return max(self.layoutXSize, Field.LAYOUT_MINWIDTH)
    
    def YSize(self):
        if self.layoutYSize is None:
            self.layoutYSize = self.BodyLayout().pop().ypos # Static layout not included
        return self.layoutYSize
    
    def XBounds(self):
        if self.hasBox:
            retVal = self.XSize()+4
        else:
            retVal = self.XSize()+2
        return retVal
            
    def YBounds(self):
        if self.hasBox:
            retVal = self.YSize()+3
        else:
            retVal = self.YSize()+1
        return retVal
        
    def AddBox(self):
        self.hasBox = True

    def LayoutFields(self, inFields, inYStep):
        if self.hasBox:
            xOffset = self.BOXWIDTH
            yOffset = self.BOXWIDTH
            xSize = self.baseXSize - self.BOXWIDTH
            ySize = self.baseYSize - self.BOXWIDTH
        else:
            xOffset = 0
            yOffset = 0
            xSize = self.baseXSize
            ySize = self.baseYSize
    
        xStart = xOffset+self.BORDER
        if inYStep >= 0:
            yStart = yOffset+self.BORDER
        else:
            # If inYStep is negative, start from the bottom
            yStart = ySize - self.BORDER
        
        xPos = xStart
        yPos = yStart
        
        xMax = xPos
        yMax = yPos
        
        retVal = []
        for field in inFields:            
            flow = field.Flow()
            
            retVal.append(Struct(xpos = xPos, ypos = yPos))
            
            # UpdateWidth can rewrap text and change the field width and height 
            field.UpdateWidth((xSize - self.BORDER) - xPos)
            xMax = max(xMax, xPos + field.Width())
            if field.Width() > 0:
                yMax = yPos + inYStep * field.Height() # Only advance yMax for non-blank lines
                
            if flow == Field.FLOW_RIGHT:
                xPos += field.Width() + 1
            elif flow == Field.FLOW_RETURN:
                xPos = xStart
                yPos += inYStep * field.Height()
            elif flow == Field.FLOW_DOUBLERETURN:
                xPos = xStart
                yPos += inYStep * (field.Height()+1)
            elif flow == Field.FLOW_NONE:
                pass # Leave xPos and yPos as they are
            else:
                raise Exception("Unknown flow type: "+str(flow))
        
        retVal.append(Struct(xpos = xMax, ypos = yMax)) # End marker

        return retVal

    def BodyLayout(self):
        return self.LayoutFields(self.fieldGroup.BodyFields(), 1)

    def StaticLayout(self):
        return self.LayoutFields(self.fieldGroup.StaticFields(), -1)

class FieldInputTracker:
    def __init__(self, inFieldGroup):
        self.fieldGroup = inFieldGroup
        self.inputIndex = None
    
    def ActivateNextInput(self): 
        self.InputIndexSet((self.inputIndex + 1) % self.fieldGroup.NumInputFields())
            
    def ActivatePreviousInput(self):
        numFields = self.fieldGroup.NumInputFields()
        self.InputIndexSet((self.inputIndex + numFields - 1) % numFields)
            
    def IsLastInput(self):
        return self.inputIndex + 1 == self.fieldGroup.NumInputFields()

    def CurrentInput(self):
        if self.inputIndex is not None:
            retVal = self.fieldGroup.InputField(self.inputIndex)
        else:
            retVal = None
        return retVal

    def InputIndex(self):
        return self.inputIndex

    def InputIndexSet(self, inIndex):
        if self.inputIndex is not None:
            self.CurrentInput().Deactivate()
        
        self.inputIndex = inIndex
        
        if self.inputIndex is not None:
            self.CurrentInput().Activate()

    def NeedsCursor(self):
        if self.inputIndex is not None:
            retVal = True
        else:
            retVal = False
        return retVal
