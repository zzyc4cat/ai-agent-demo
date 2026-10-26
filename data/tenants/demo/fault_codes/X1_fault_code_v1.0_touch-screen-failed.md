---
source: https://wiki.bambulab.com/zh/x1/troubleshooting/touch-screen-failed
fetched_at: 2026-10-26
title: 触摸屏功能失效
media_count: 11
---

> 来源：https://wiki.bambulab.com/zh/x1/troubleshooting/touch-screen-failed｜抓取日期：2026-10-26｜仅供本地检索演示，版权归原作者

触摸屏功能失效
X1系列触摸屏功能失效排查

---


## 问题现象

启动打印机，显示屏能正常亮起并显示正常，但触摸屏功能失效或失控。

## 原因及解决方案

1. 显示屏未正确连接， 需重新连接显示屏；
2. 显示屏排线损坏，需更换连接排线；
3. AP主板损坏，需更换AP主板；
4. AP板端的FPC连接器接触不良，需重连接FPC；
5. 显示屏内部排线连接不良，需拆装显示屏重新连接；
6. 显示屏损坏，需要更换显示屏。

## 安全和操作提示

在进行拆装作业时，需要确认打印机是断电状态。

## 所需的工具

- H1.5/H2.0 内六角扳手
- 镊子

## 排查指引

### 步骤1 - 检查显示屏端的连接状态，重装LCD显示屏

操作步骤：请点击 [更换高清显示屏](https://wiki.bambulab.com/zh/x1/maintenance/replace-high-resolution-screen)了解显示屏的拆除和安装操作，检查连接状态和FPC的外观，确认无异常后，重新连接显示屏，然后开机确认问题是否已解决，如未能解决，请进行下一步检查AP主板的外观。

注意事项：

1、需要先关闭打印机电源；

2、拆除显示屏时，请必务正确解除显示屏的锁定；

![](https://wiki.bambulab.com/x1/maintenance/replace-high-resolution-screen/350px-press_to_unlock.png)

3、重新安装前，请先检查接口和PIN针有无异常，FPC排线有无损伤， 如果排线有损伤，请 [更换显示屏FPC](https://wiki.bambulab.com/zh/x1/maintenance/replace-fpc-from-ap-to-display)。

### 步骤2 - 检查AP板的关联元器件，确认无脱落

揭开AP主板盖， 在下图所示的位置，找到对应的元器件，确认红框内的元器件无脱落、松动或烧坏的现象。如果一切正常，请进行下一步检查AP主板端的FPC连接器状态，如果有异常，[更换AP主板](https://wiki.bambulab.com/zh/x1/maintenance/replace-ap-board)。

|  |  |  |
| --- | --- | --- |

### 步骤3 - 检查AP主板端的FPC连接器状态

如果上述两个步骤没能解决问题，请关闭电源，参考 [更换AP主板](https://wiki.bambulab.com/zh/x1/maintenance/replace-ap-board) 检查显示屏FPC在AP板上的连接状态，如发现在倾斜或松脱的现象，请重新连接。

注意：此处的FPC有用UV胶进行加固，如果需要重新连接排线，建议先使用电吹风加热UV胶后再去除。

![](https://wiki.bambulab.com/x1/maintenance/replace-ap-board/350px-fpc_connected.png)

重新连接好后，可以在不锁AP板螺丝的情况下直接开启打印机电源，以检查问题是否能解决；如果检查无异常或重新连接未能解决问题，请进行下一步拆解显示屏。

### 步骤4 - 拆解显示屏，重装内部排线

移除显示屏后盖上的3颗螺丝，将显示屏后盖移除。请注意，后盖内部有卡扣，拆卸螺丝后需要将后盖撬开。

|  |  |  |
| --- | --- | --- |

打开连接器锁扣，移除UV胶，拔出软排线。（可以尝试用电吹风吹热UV胶后去除UV胶，但不建议使用热风枪，因为过高的温度会直接损坏连接器）

|  |  |
| --- | --- |

有时候因为UV胶的原因，可能会导致排线接触不良，而造成触摸功能失效或失控，清除排线上的UV胶残胶，重新连接好排线，安装好显示屏，然后开启打印机重新确认触摸屏功能是否恢复正常。我们已经对点胶位置进行了变更，如下图。

![](https://wiki.bambulab.com/x1/troubleshooting/touch-screen-failed/new_uv_glue.jpg)

### 步骤5 - 更换显示屏

如果以上步骤未能解决问题，请 [更换高清显示屏](https://wiki.bambulab.com/zh/x1/maintenance/replace-high-resolution-screen)。

## 媒体资源

- img: https://wiki.bambulab.com/x1/maintenance/replace-high-resolution-screen/350px-press_to_unlock.png
- img: https://wiki.bambulab.com/x1/troubleshooting/black-screen/open_the_ap_cover1.jpg
- img: https://wiki.bambulab.com/x1/troubleshooting/touch-screen-failed/location_components.jpg
- img: https://wiki.bambulab.com/x1/troubleshooting/touch-screen-failed/components.png
- img: https://wiki.bambulab.com/x1/maintenance/replace-ap-board/350px-fpc_connected.png
- img: https://wiki.bambulab.com/x1/troubleshooting/touch-screen-failed/3_screws.jpg
- img: https://wiki.bambulab.com/x1/troubleshooting/touch-screen-failed/buckles.jpg
- img: https://wiki.bambulab.com/x1/troubleshooting/touch-screen-failed/screendddd.gif
- img: https://wiki.bambulab.com/x1/troubleshooting/touch-screen-failed/rear_cover_removed.png
- img: https://wiki.bambulab.com/x1/troubleshooting/touch-screen-failed/uv_glue_on_the_connector.png
- img: https://wiki.bambulab.com/x1/troubleshooting/touch-screen-failed/new_uv_glue.jpg

