# -*- coding: UTF-8 -*-

import os
import colorsys
import random

import nuke

VERSION = 1.01

def all_knobs_name(node):
    _ret = []
    for n in node.allKnobs() :
        _ret.append(n.name())
    return _ret

def rename_all_nodes():
    for i in nuke.allNodes('BackdropNode'):
        _nodes = i.getNodes();
        j = i['label'].value().split('\n')[0].split(' ')[0];
        for k in _nodes:
            if k.Class() == 'Group' and not '_' in k.name() and not (k['disable'].value()):
                m = k.name().rstrip('0123456789');
                k.setName(m + '_' + j + '_1', updateExpressions=True);
            elif  not '_' in k.name() and (not nuke.exists(k.name() + '.disable') or not (k['disable'].value())):
                k.setName(k.Class() + '_' + j + '_1', updateExpressions=True);

def SwapKnobValue( ka, kb ):
    va, vb = ka.value(), kb.value()
    ka.setValue( vb )
    kb.setValue( va )

def panel_show( keyword ):
    def _node_name(node) :
        return node.name()
    list1 = []
    for i in nuke.allNodes():
        a = 0
        try:
            a = not i['disable'].value()
        except:
            pass
        if s in i.name() and a:
            list1.append( i )
    list1.sort( key=_node_name, reverse=True )
    for i in list1:
        i.showControlPanel()

def UpdateToolsets( s , path ):
    for i in nuke.allNodes():
       if s in i.name() and 'python' not in i[ 'label' ].value() :
           i.selectOnly()
           n = nuke.loadToolset( path )
           for k in i.allKnobs() :
               kn = k.name()
               if kn in [ 'name', '', 'label' ] :
                   pass
               elif kn in allKnobsName( n ) :
                   n[ kn ].setValue( i[ kn ].value() )
           nuke.delete( i )

def channels_rename(prefix='PuzzleMatte'):

    n = nuke.selectedNode()

    # Record viewer status
    n_vw = nuke.activeViewer()
    _raw = dict.fromkeys(['has_viewer', 'viewer_input', 'viewer_channels'])
    _raw_viewer = {}
    if n_vw:
        n_vwn = n_vw.node()
        _raw['has_viewer'] = True
        _raw['viewer_input'] = n_vwn.input(0)
        if not _raw['viewer_input']:
            n_vwn.setInput(0, n)
        for knob in n_vwn.knobs():
            _raw_viewer[knob] = n_vwn[knob].value()
    else:
        _raw['has_viewer'] = False
        n_vwn = nuke.createNode('Viewer')
        n_vwn.setInput(0, n)

    # Set viewer
    nuke.activeViewer().activateInput(0)
    n_lcs = nuke.nodes.LayerContactSheet(showLayerNames=1)
    n_lcs.setInput(0, n)
    n_vwn.setInput(0, n_lcs)
    n_vwn['channels'].setValue('rgba')

    # Prepare dictionary
    _D = {}
    for i in n.channels():
        if i.startswith(prefix):
            _D[i] = ''
    _L = _D.keys()

    # Sort object on rgba order
    rgbaOrder = lambda s: s.replace(prefix + '.', '!.').replace('.red', '.0_').replace('.green', '.1_').replace('.blue', '.2_').replace('.alpha', '.3_')
    _L.sort(key=rgbaOrder)

    # Set text style
    _text_stylize = lambda s: s.replace('.red', '.<span style=\"color:#FF4444\">red</span>').replace('.green', '.<span style=\"color:#44FF44\">green</span>').replace('.blue', '.<span style=\"color:#4444FF\">blue</span>')
    _L_stylized = map(_text_stylize, _L)

    # Set panel from dictionary
    p = nuke.Panel('MaskShuffle')
    for i in range(len(_L)):
        p.addSingleLineInput(_L_stylized[i], _D[_L[i]])

    # Show panel
    p.show()
    nuke.delete(n_lcs)

    # Recover Viewer Status
    if _raw['has_viewer']:
        n_vwn.setInput(0, _raw['viewer_input'])
        for knob in n_vwn.knobs():
            try:
                n_vwn[knob].setValue(_raw_viewer[knob])
            except:
                pass
    else:
        nuke.delete(n_vwn)
    n.selectOnly()

    # Create copy
    for i in range(len(_L)):
        # Create copy node every 4 channels
        count = i % 4
        if count == 0:
            c = nuke.createNode('Copy')
            # Set two input to same node
            if c.input(1):
                c.setInput(0, c.input(1))
            elif c.input(0):
                c.setInput(1, c.input(0))
        # Prepare 'to' channel name
        _input = p.value(_L_stylized[i])
        if _input:
            to = 'mask_extra.' + _input.replace(' ', '_').replace('.', '_')
            nuke.Layer('mask_extra', [to])
        else:
            to = 'none'
        # Set node
        c['from' + str(count)].setValue(_L[i])
        c['to' + str(count)].setValue(to)
        # Delete empty copy node
        if count == 3:
            if  c['to0'].value() == c['to1'].value() == c['to2'].value() == c['to3'].value() == 'none':
                c.input(0).selectOnly()
                nuke.delete(c)

def splitByBackdrop():
    text_saveto = '保存至:'
    text_ask_if_create_new_folder = '目标文件夹不存在, 是否创建?'
    
    # Panel
    p = nuke.Panel('splitByBackdrop')
    p.addFilenameSearch(text_saveto, os.getenv('TEMP'))
    p.show()
    
    # Save splited .nk file
    save_path = p.value(text_saveto).rstrip('\\/')
    noname_count = 0
    for i in nuke.allNodes('BackdropNode'):
        label = repr(i['label'].value()).strip("'").replace('\\', '_').replace('/', '_')
        if not label:
            noname_count += 1
            label = 'noname_{0:03d}'.format(noname_count)
        if not os.path.exists(save_path):
            if not nuke.ask(text_ask_if_create_new_folder):
                return False
        dir_ = save_path + '/splitnk/'
        dir_ = os.path.normcase(dir_)
        if not os.path.exists(dir_):
            os.makedirs(dir_)
        filename = dir_ + label + '.nk'
        i.selectOnly()
        i.selectNodes()
        nuke.nodeCopy(filename)
    os.system('explorer "' + dir_ + '"')   
    return True

def linkZDefocus():
    _ZDefocus = nuke.toNode('_ZDefocus')
    if not _ZDefocus:
        return False
    for i in nuke.allNodes('ZDefocus2'):
        if not i.name().startswith('_'):
            i[ 'size' ].setExpression( '_ZDefocus.size' )
            i[ 'max_size' ].setExpression( '_ZDefocus.max_size' )
            i[ 'disable' ].setExpression( '( [ exists _ZDefocus ] ) ? !_ZDefocus.disable : 0')
            i[ 'center' ].setExpression( '( [exists _ZDefocus] ) ? _ZDefocus.center : 0' )
            i[ 'dof' ].setExpression( '( [exists _ZDefocus] ) ? _ZDefocus.dof : 0' )
            i[ 'label' ].setValue( '[\n'
                                   'set trg parent._ZDefocus\n'
                                   'if { [ exists $trg ] } {\n'
                                   '    knob this.math [value $trg.math]\n'
                                   '    knob this.z_channel [value $trg.z_channel]\n'
                                   '}\n'
                                   ']' )
    return True


def getMinMax( srcNode, channel='depth.Z' ):
    '''
    Return the min and max values of a given node's image as a tuple
    args:
       srcNode  - node to analyse
       channels  - channels to analyse. This can either be a channel or layer name
    '''
    MinColor = nuke.nodes.MinColor( channels=channel, target=0, inputs=[srcNode] )
    Inv = nuke.nodes.Invert( channels=channel, inputs=[srcNode])
    MaxColor = nuke.nodes.MinColor( channels=channel, target=0, inputs=[Inv] )
    
    curFrame = nuke.frame()
    nuke.execute( MinColor, curFrame, curFrame )
    minV = -MinColor['pixeldelta'].value()
    
    nuke.execute( MaxColor, curFrame, curFrame )
    maxV = MaxColor['pixeldelta'].value() + 1
    
    for n in ( MinColor, MaxColor, Inv ):
        nuke.delete( n )
    return minV, maxV
    
def randomGlColor(n):
    if 'gl_color' in list(i.name() for i in n.allKnobs()) and not n['gl_color'].value() and not n.name().startswith('_'):
        color = colorsys.hsv_to_rgb(random.random(), 0.8, 1)
        color = tuple(hex(int(i * 255))[2:] for i in color)
        n['gl_color'].setValue(eval('0x{}{}{}{}'.format(color[0],color[1],color[2],'00')))
    else:
        return False
        
def enableRSMB(prefix='_'):
    for i in nuke.allNodes('OFXcom.revisionfx.rsmb_v3'):
        if i.name().startswith(prefix):
            i['disable'].setValue(False)


def fix_error_read():
    while True:
        _created_node = []
        for i in filter(lambda x : x.hasError(), nuke.allNodes('Read')):
            _filename = nuke.filename(i)
            if os.path.basename(_filename).lower() == 'thumbs.db':
                nuke.delete(i)
            if os.path.isdir(_filename):
                _filename_list = nuke.getFileNameList(_filename)
                for file in _filename_list:
                    _read = nuke.createNode('Read', 'file "{}"'.format('/'.join([_filename, file])))
                    _created_node.append(_read)
                nuke.delete(i)
        if not _created_node:
            break

def delete_unused_nodes(message=False):
    def _is_used(n):
        if n.name().startswith('_') or n.Class() in ['BackdropNode', 'Read', 'Write', 'Viewer', 'GenerateLUT']:
            return True

        nodes_dependent_this = filter(lambda n: n.Class() not in [''] or n.name().startswith('_') ,n.dependent())
        return bool(nodes_dependent_this)

    c = 0
    while True:
        for i in nuke.allNodes():
            if not _is_used(i):
                nuke.delete(i)
                c += 1
                break
        else:
            break
            
    print('Deleted {} unused nodes.'.format(c))
    if message:
        nuke.message('<font size=5>删除了 {} 个未使用的节点。</font>\n<i>名称以"_"(下划线)开头的节点及其上游节点将不会被删除</i>'.format(c))

def replace_sequence():
    '''
    Replace all read node to specified frame range sequence.
    '''
    # Prepare Panel
    p = nuke.Panel('单帧替换为序列')
    render_path_text = '限定只替换此文件夹中的读取节点'
    p.addFilenameSearch(render_path_text, 'z:/SNJYW/Render/')
    first_text = '设置工程起始帧'
    p.addExpressionInput(first_text, int(nuke.Root()['first_frame'].value()))
    last_text = '设置工程结束帧'
    p.addExpressionInput(last_text, int(nuke.Root()['last_frame'].value()))

    ok = p.show()
    if ok:
        render_path = p.value(render_path_text)

        first = int(p.value(first_text))
        last = int(p.value(last_text))
        flag_frame = None

        nuke.Root()['proxy'].setValue(False)
        nuke.Root()['first_frame'].setValue(first)
        nuke.Root()['last_frame'].setValue(last)

        for i in nuke.allNodes('Read'):
            file_path = nuke.filename(i)
            if file_path.startswith(render_path):
                search_result = re.search(r'\.([\d]+)\.', file_path)
                if search_result:
                    flag_frame = search_result.group(1)
                file_path = re.sub(r'\.([\d#]+)\.', lambda matchobj: r'.%0{}d.'.format(len(matchobj.group(1))), file_path)
                i['file'].setValue(file_path)
                i['format'].setValue('HD_1080')
                i['first'].setValue(first)
                i['origfirst'].setValue(first)
                i['last'].setValue(last)
                i['origlast'].setValue(last)

        _Write = nuke.toNode('_Write')
        if _Write:
            if flag_frame:
                flag_frame = int(flag_frame)
                _Write['custom_frame'].setValue(flag_frame)
                nuke.frame(flag_frame)
            _Write['use_custom_frame'].setValue(True)

def setProjectRootByName(path='E:'):
    nuke.root()['project_directory'].setValue(os.path.dirname(path + '/' + os.path.basename(nuke.scriptName()).split('.')[0].replace('_', '/')))

def split_layers(node):
    
    '''
    Splits each and every layer from the selected node into their own pipes
    '''
    
    ch = node.channels()
    
    layers = []
    valid_channels = ['red', 'green', 'blue', 'alpha', 'black', 'white']
    
    for each in ch:
        layer_name = each.split( '.' )[0]
        tmp = []
        for channel in ch:
            if channel.startswith( layer_name ) == True:
                tmp.append( channel )
        if len( tmp ) < 4:
            for i in range( 4 - len( tmp ) ):
                tmp.append( layer_name + ".white" )
        if tmp not in layers:
            layers.append( tmp )
            
    for each in layers:
        layer = each[0].split( '.' )[0]
        ch1 = each[0].split( '.' )[1]
        ch2 = each[1].split( '.' )[1]
        ch3 = each[2].split( '.' )[1]
        ch4 = each[3].split( '.' )[1]
        
        if ch1 not in valid_channels:
            ch1 = "red red"
        else:
            ch1 = '%s %s' % ( ch1, ch1 )
            
        if ch2 not in valid_channels:
            ch2 = "green green"
        else:
            ch2 = '%s %s' % ( ch2, ch2 )
            
        if ch3 not in valid_channels:
            ch3 = "blue blue"
        else:
            ch3 = '%s %s' % ( ch3, ch3 )
            
        if ch4 not in valid_channels:
            ch4 = "alpha alpha"
        else:
            ch4 = '%s %s' % ( ch4, ch4 )
            
        prefs = "in %s %s %s %s %s" % (layer, ch1, ch2, ch3, ch4)
        shuffle = nuke.createNode( 'Shuffle', prefs, inpanel=False )
        # shuffle.knob( 'label' ).setValue( layer )
        shuffle.setInput( 0, node )

def shuffle_rgba(node):
    channel = ['red','green','blue','alpha']
    for c in channel:
        shuffle = nuke.nodes.Shuffle( name='Shuffle%s'%c[0].upper() )
        shuffle.setInput(0, node)
        for color in channel:
            shuffle[color].setValue(c)

def nodes_to_relpath(nodes):
    perfix = r'[value root.project_directory]'
    projDir = nuke.root().knob('project_directory').getValue()
    rNodes = nodes
    for rNode in rNodes:
        if rNode.knob('file') is not None:
            origPath = rNode.knob('file').getValue()
            newPath = origPath.replace(projDir,perfix)
            rNode.knob('file').setValue(newPath)

def nodes_add_dots(nodes=None):
    if not nodes:
        nodes = nuke.selectedNodes()
    
    def _add_dot(output_node, input_num):
        input_node = output_node.input(input_num)
        if not input_node or input_node.Class() in ['Dot'] or abs(output_node.xpos() - input_node.xpos())<output_node.screenWidth() or abs(output_node.ypos() - input_node.ypos())<=output_node.screenHeight():
            return None
        if output_node.Class() in ['Viewer'] or output_node['hide_input'].value():
            return None

        _dot = nuke.nodes.Dot(inputs=[input_node])
        output_node.setInput(input_num, _dot)
        _dot.setXYpos(
            input_node.xpos()+input_node.screenWidth()/2-_dot.screenWidth()/2,
            output_node.ypos()+output_node.screenHeight()/2-_dot.screenHeight()/2 - (_dot.screenHeight()+5)*input_num
        )
        
    def _all_input_add_dot(node):
        for input_num in range(node.inputs()):
            _add_dot(node, input_num)

    for n in nodes:
        if n.Class() in ['Dot']:
            continue
        _all_input_add_dot(n)

def gizmo_to_group(gizmo):
    if not isinstance(gizmo, nuke.Gizmo):
        return gizmo
    
    _selected = gizmo['selected'].value()
    _group = gizmo.makeGroup()

    # Set Input.
    for i in range(gizmo.inputs()):
        _group.setInput(i, gizmo.input(i))
    # Set Output.
    for n in nuke.allNodes():
        for i in range(n.inputs()):
            if n.input(i) is gizmo:
                n.setInput(i, _group)

    # Set position and name.
    if gizmo.shown():
        _group.showControlPanel()
    _group.setXYpos(gizmo.xpos(), gizmo.ypos())
    _name = gizmo['name'].value()
    nuke.delete(gizmo)
    _group.setName(_name)
    _group['selected'].setValue(_selected)
    
    return _group
    
def all_gizmo_to_group():
    for n in nuke.allNodes():
        # Avoid scripted gizmo.
        if nuke.knobChangeds.get(n.Class()):
            continue

        gizmo_to_group(n)

if __name__ == '__main__':
    gizmo_to_group(nuke.selectedNode())