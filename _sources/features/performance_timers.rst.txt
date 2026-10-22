性能监控
========================

.. image:: /_images/Nuke10.5_2021-12-07_17-28-42.png


用于节点性能调试，开启后渲染新的帧进行测试。

绿色的节点速度快，红色的节点渲染速度慢。 


.. image:: /_images/Nuke10.5_2021-12-07_17-33-32.png

开始
----------------

开始性能监控，重复开始无作用。

对应 ``nuke.startPerformanceTimers`` API。

结束
-----------------

结束性能监控。

对应 ``nuke.stopPerformanceTimers`` API。

重置
---------------------

重置性能监控计数，等同于结束再开始。

对应 ``nuke.resetPerformanceTimers`` API。
