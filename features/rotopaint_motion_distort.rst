RotoPaint 运动扭曲
========================

.. image:: /_images/Nuke10.5_2020-08-18_14-20-31.png

.. image:: /_images/Nuke10.5_2020-08-18_14-20-36.png

基于 motion 层对 RotoPaint 笔画进行创建动画。

和 :doc:`/features/motion_distort` 不同此命令仅支持 RotoPaint 但输出为矢量笔画方便修改。

在菜单中选择 :guilabel:`编辑` - :guilabel:`RotoPaint 运动扭曲` 进行创建。

执行命令将为所有选中的 RotoPaint 节点中无动画且可见的笔画创建一个带动画的副本，并隐藏锁定原始笔画。

.. image:: /_images/Nuke10.5_2020-08-18_15-17-53.png

执行命令需要先进行设置。

.. image:: /_images/Nuke10.5_2020-08-18_15-29-18.png

为笔画创建的动画副本会带 ``.MotionDistort`` 后缀，重复执行此命令将会根据基准帧重新生成动画，覆盖原有数据。

.. tip::

  可对生成的笔画手动修改后，可用修改的帧作为基准帧生成之后或之前的帧。
