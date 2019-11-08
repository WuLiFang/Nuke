Draw
====
绘制,用于得到自定输出

Flicker
-------

灯光抖动生成器

.. image:: /_images/Flicker_node.png

控制
**********

.. image:: /_images/Flicker_panel.png

|wlf_Lightwrap_icon| wlf_Lightwrap
-------------------------------------------

.. image:: /_images/wlf_Lightwrap_node.png

修改过的灯光包裹,比自带的灯光包裹效果更好

.. figure:: /_images/wlf_Lightwrap_before.png

  启用前

.. figure:: /_images/wlf_Lightwrap_after.png

  启用后

控制
**********

.. image:: /_images/wlf_Lightwrap_panel.png

.. |wlf_Lightwrap_icon| image:: /_images/wlf_Lightwrap_icon.png


.. _VectorTestPattern:

VectorTestPattern
-----------------------

提供和输入尺寸相同的 :ref:`GenerateVector` 专用测试图案。

.. _GenerateVector:

GenerateVector
------------------------------

生成向量数据，配合 :ref:`VectorTestPattern` 使用。

输入:

<无名称>

  向量数据和此输入合并。

before

  应用向量之前的测试图案，仅识别rg通道。

after

  应用向量之后的测试图案，仅识别rg通道。

控制:

output

  向量输出通道，默认为motion，输出4个通道，后2个通道数据和前两个通道相同。

.. figure:: /_images/Nuke10.5_2019-11-08_17-51-32.png

  用法示例

.. figure:: /_images/Nuke10.5_2019-11-08_17-51-38.png

  用法示例对应的效果
