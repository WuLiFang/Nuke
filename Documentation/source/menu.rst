菜单
========

编辑
----

.. _同时编辑多个节点:

同时编辑多个节点
****************
同时设置多个同类型节点
常用于设置Read节点帧范围

.. autoclass:: edit_panels.MultiEdit

分离图层
********
为选中节点的每个图层(Layer)创建一个Shuffle

.. autofunction:: edit.split_layers

分离rgba
********
为选中节点的rgba通道各创建一个shuffle

.. autofunction:: edit.shuffle_rgba

重命名PuzzleMatte
******************
为选中节点中的PuzzleMatte通道指定新的名称
提升节点可读性

.. autoclass:: edit_panels.ChannelsRename

.. _标记为稍后启用:

标记为稍后启用
****************

将选中节点标为稍后启用, 用于加快预览

在首选项中有相关设置使其在保存时自动重新开启

可以使用 :ref:`禁用所有稍后启用节点` 来快速禁用所有

.. autofunction:: edit.mark_enable

输出当前帧png
**************
为选中节点当前帧创建一张png

.. autofunction:: comp.render_png

设置帧范围
**********
为选中读取节点设置帧范围

.. tip::

    适用情况较限定, 推荐使用\ :ref:`同时编辑多个节点`\ 代替

.. autofunction:: edit.dialog_set_framerange

转换为相对路径
****************

将选中读取节点的素材路径转为相对路径

.. attention::

    这是从老版本插件继承的功能,尚未测试

.. autofunction:: edit.nodes_to_relpath

.. _禁用所有稍后启用节点:

禁用所有稍后启用节点
*************************
将所有\ :ref:`标记为稍后启用`\ 的节点禁用

.. automethod:: edit.Nodes.disable

修正读取错误
**************
在读取节点错误时先拖入正确的素材
会比较文件名将报错的素材替换为同名正确的素材

.. autofunction:: asset.fix_error_read

Reload所有
******************
一次性点击所有读取节点的Reload

.. autofunction:: edit.reload_all_read_node

检查缺帧
********
检查所有读取节点的素材缺帧状况

.. automethod:: asset.DropFrames.check

检查素材更新
********************
比较素材修改日期和当前脚本工程文件日期

.. autofunction:: asset.warn_mtime

转换单帧为序列
********************
将所有单帧的读取节点转换为序列

.. autofunction:: edit.replace_sequence 

合成
----

自动合成
*********
自动合成当前导入的素材

.. autofunction:: comp.Comp

Redshift预合成
***************
将选中的Redshift素材节点进行分层预合成

.. autofunction:: precomp.redshift


CGTeamWork
-----------
此菜单只在安装了CGTeamWork之后才会出现

登录
****
用于自动登录失效时临时进行手动登录, 推荐之后重开Nuke和CGTeamWork使用自动登录

.. autofunction:: cgtwn.dialog_login

添加note
*********
为CGTeamWork上的对应镜头添加备注

.. automethod:: cgtwn.CurrentShot.ask_add_note(self)

提交单帧
*********
将\ :ref:`wlf_Write`\ 节点输出的单帧提交

.. warning::

    正规的提交不应该是单帧应是mov

.. automethod:: cgtwn.CurrentShot.submit_image

提交视频
********
将\ :ref:`wlf_Write`\ 节点输出的视频提交

.. automethod:: cgtwn.CurrentShot.submit_video

创建项目色板
****************
为项目创建色板

.. note::

    准备将此功能集成至CGTeamWork上

.. autoclass:: cgtwn.ContactSheetPanel

创建项目文件夹
******************
为项目中的每个匹配镜头建立一个空文件夹

.. autofunction:: cgtwn.dialog_create_dirs()

帮助
----

吾立方插件 文档
***************
本文档的入口

吾立方网站
**********
公司官网

工具
----
每次使用前带需要设置的操作

批量自动合成
************
合成/自动合成的批量版本
直接自动合成大量镜头

.. warning::

    使用多线程, 渲染同时进行批量自动合成可能导致死机

.. automethod:: comp.Comp.show_dialog

.. _创建色板:

创建色板
********
为一个文件夹中的图像文件(.jpg, .png, .jpeg)创建html色板

.. autofunction:: wlf.csheet.dialog_create_html

上传工具
********
上传工作成果至服务器或CGTeamWork

.. autoclass:: wlf.uploader.Dialog

扫描空文件夹
************
用于快速找出无素材的镜头

.. autofunction:: scanner.call_from_nuke

分离exr
*******
把多层的exr文件分成多个单层的exr文件

.. autoclass:: splitexr.Dialog

分割当前文件(根据背板)
**********************
把多包含多个镜头的文件根据背板(Backdrop)分离成多个单镜头的文件

.. autofunction:: edit.split_by_backdrop
