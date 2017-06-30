# -*- coding=UTF-8 -*-
# Preset Backdrop 1.2
# Copyright (c) 2011 Victor Perez.  All Rights Reserved.

import nuke, colorsys, operator

### Preset Backdrop
def create_backdrop():
    customPreset = None
    sep = '"'
    presets = ['Elements','Output','Roto','Camera_Projection','Camera_Setup','CG','Color_Correction','Despill','Edge_Fixes','FX','Key','Matte','Lens_Flare','Light_Setup','Relight','Stereo_Fixes','Temp','Test']
    p = nuke.Panel('Preset Backdrop')
    p.addEnumerationPulldown('Preset',' '.join(presets))
    p.addSingleLineInput('Custom Label','')
    if p.show():
        customPreset = p.value('Preset')
        customLabel = p.value('Custom Label')
    
    # Backdrop presets
    if customPreset == 'Elements':
        presetLabel = 'Elements'
        presetIcon = 'Read.png'
        presetColor = colorsys.hsv_to_rgb(0.233, 0.15, 0.465)
		
		        
    elif customPreset == 'Output':
        presetLabel = 'Output'
        presetIcon = 'Write.png'
        presetColor = colorsys.hsv_to_rgb(0.167, 1, 0.373)
		
    elif customPreset == 'Roto':
        presetLabel = 'Roto'
        presetIcon = 'Roto.png'
        presetColor = colorsys.hsv_to_rgb(0.333, 0.430, 0.384)
        
    elif customPreset == 'Camera_Projection':
        presetLabel = 'Camera Projection'
        presetIcon = 'Card.png'
        presetColor = colorsys.hsv_to_rgb(0.42, 0.78, 0.455)
        
    elif customPreset == 'Camera_Setup':
        presetLabel = 'Camera Setup'
        presetIcon = 'Camera.png'
        presetColor = colorsys.hsv_to_rgb(0, 0.635, 0.58)
        
    elif customPreset == 'CG':
        presetLabel = 'CG'
        presetIcon = 'Shader.png'
        presetColor = colorsys.hsv_to_rgb(0.062, 1, 0.5)
            
    elif customPreset == 'Color_Correction':
        presetLabel = 'Color Correction'
        presetIcon = 'ColorLookup.png'
        presetColor = colorsys.hsv_to_rgb(0.58, 0.384, 0.465)
        
    elif customPreset == 'Despill':
        presetLabel = 'Despill'
        presetIcon = 'HueCorrect.png'
        presetColor = colorsys.hsv_to_rgb(0.539, 0.172, 0.46)
        
    elif customPreset == 'Edge_Fixes':
        presetLabel = 'Edge Fixes'
        presetIcon = 'EdgeDetect.png'
        presetColor = colorsys.hsv_to_rgb(0.256, 0.354, 0.5)
        
    elif customPreset == 'FX':
        presetLabel = 'FX'
        presetIcon = ':qrc/images/ToolbarFilter.png'
        presetColor = colorsys.hsv_to_rgb(0.65, 0.23, 0.497)
        
    elif customPreset == 'Key':
        presetLabel = 'Key'
        presetIcon = 'Keyer.png'
        presetColor = colorsys.hsv_to_rgb(0.333, 1, 0.5)
        
    elif customPreset == 'Matte':
        presetLabel = 'Matte'
        presetIcon = 'Radial.png'
        presetColor = colorsys.hsv_to_rgb(0.5, 1, 0.1)
        
    elif customPreset == 'Lens_Flare':
        presetLabel = 'Lens Flare'
        presetIcon = 'Flare.png'
        presetColor = colorsys.hsv_to_rgb(0.152, 0.354, 0.5)
        
    elif customPreset == 'Light_Setup':
        presetLabel = 'Light Setup'
        presetIcon = 'SpotLight.png'
        presetColor = colorsys.hsv_to_rgb(0.152, 0, 0.5)
        
    elif customPreset == 'Relight':
        presetLabel = 'Relight'
        presetIcon = 'ReLight.png'
        presetColor = colorsys.hsv_to_rgb(0.938, 1, 0.5)
        
    elif customPreset == 'Stereo_Fixes':
        presetLabel = 'Stereo Fixes'
        presetIcon = 'Anaglyph.png'
        presetColor = colorsys.hsv_to_rgb(0.5, 1, 0.267)
        
    elif customPreset == 'Temp':
        presetLabel = 'Temp'
        presetIcon = 'CheckerBoard.png'
        presetColor = colorsys.hsv_to_rgb(0.52, 0.84, 0.58)
        
    elif customPreset == 'Test':
        presetLabel = 'Test'
        presetIcon = 'ClipTest.png'
        presetColor = colorsys.hsv_to_rgb(0, 0, 0.3)
        
        
    ### Backdrop creation based on presets
    if customPreset is not None:
        # RGB to HEX
        r = presetColor[0]
        g = presetColor[1]
        b = presetColor[2]
        hexColour = int('%02x%02x%02x%02x' % (r*255,g*255,b*255,1), 16)
        
        if presetIcon == '':
            icon = ''
        else:
            icon = '<img src='+sep+presetIcon+sep+'> '
            
        selNodes = nuke.selectedNodes()
        if not selNodes:
            if customLabel == '':
                return nuke.nodes.BackdropNode(label = '<center>'+icon+presetLabel, tile_color = hexColour, note_font_size = 30)
            else:
                return nuke.nodes.BackdropNode(label = '<center>'+icon+customLabel, tile_color = hexColour, note_font_size = 30)
    
       
        # Find Min. and Max. of Positions
        positions = [(i.xpos(), i.ypos()) for i in selNodes]
        xPos = sorted(positions, key = operator.itemgetter(0))
        yPos = sorted(positions, key = operator.itemgetter(1))
        xMinMaxPos = (xPos[0][0], xPos[-1:][0][0])
        yMinMaxPos = (yPos[0][1], yPos[-1:][0][1])
        
        if customLabel == '':
            n = nuke.nodes.BackdropNode(xpos = xMinMaxPos[0]-10, bdwidth = xMinMaxPos[1]-xMinMaxPos[0]+110, ypos = yMinMaxPos[0]-85, bdheight = yMinMaxPos[1]-yMinMaxPos[0]+160, label = '<center>'+icon+presetLabel, tile_color = hexColour, note_font_size = 30)
        else:
            n = nuke.nodes.BackdropNode(xpos = xMinMaxPos[0]-10, bdwidth = xMinMaxPos[1]-xMinMaxPos[0]+110, ypos = yMinMaxPos[0]-85, bdheight = yMinMaxPos[1]-yMinMaxPos[0]+160, label = '<center>'+icon+customLabel, tile_color = hexColour, note_font_size = 30)
            
        n['selected'].setValue(False)
       
        # Revert to Previous Selection
        [i['selected'].setValue(True) for i in selNodes]
        
        return n
    else:
        pass