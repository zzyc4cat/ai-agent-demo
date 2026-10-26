---
source: https://wiki.bambulab.com/zh/x1/troubleshooting/black-flicker-screen
fetched_at: 2026-10-26
title: 显示屏黑屏、闪屏故障排查
media_count: 20
---

> 来源：https://wiki.bambulab.com/zh/x1/troubleshooting/black-flicker-screen｜抓取日期：2026-10-26｜仅供本地检索演示，版权归原作者

显示屏黑屏、闪屏故障排查

---


## 问题现象:

1、启动打印机，但LCD显示屏无显示，LCD背光灯也没有亮；

**注：该案例图片为 X1 系列打印机的屏幕**

![](https://wiki.bambulab.com/x1/troubleshooting/black-screen/black_screen.jpg)

2、启动打印机，但LCD显示屏无显示，LCD背光灯有亮起；

**注：该案例图片为 P1 系列打印机的屏幕**

![](https://wiki.bambulab.com/x1/troubleshooting/black-screen/%E9%BB%91%E5%B1%8F%E6%9C%89%E8%83%8C%E5%85%89.jpg)

3、启动打印机，LCD显示屏闪烁或出现条纹。

**注：该案例图片为 A1 mini 打印机的屏幕**

![](https://wiki.bambulab.com/x1/troubleshooting/black-screen/%E5%B1%8F%E5%B9%95%E8%8A%B1%E5%B1%8F.jpg)

## 原因及解决方案

### 显示屏完全黑屏：

1. MicroSD 卡故障，需更换 MicroSD 卡；
2. AP主板供电异常，需检查AP主板的电源连接线；
3. AP主板损坏，需更换AP主板；
4. 机箱LED灯条电缆短路，导致AP主板启动失败；
5. 显示屏未正确连接， 需重新连接显示屏；
6. AP板端的FPC连接器接触不良，需重连接FPC；
7. 显示屏排线损坏，需更换连接排线；
8. 显示屏损坏，需更换显示屏。

### 显示屏黑屏但背光灯亮，闪烁或出现条纹：

1. 显示屏未正确连接， 需重新连接显示屏；
2. AP板端的FPC连接器接触不良，需重连接FPC；
3. 显示屏排线损坏，需更换连接排线；
4. 显示屏损坏，需更换显示屏。

## 安全和操作提示

在进行拆装作业时，需要确认打印机是断电状态。

## 所需的工具

- H2.0 内六角扳手
- 镊子

## 排查指引

### 一. 排查 MicroSD 卡

启动打印机后，若显示屏黑屏无显示，首先可排查 MicroSD 卡问题。

**注意事项：在进行以下操作前，请务必先关闭打印机电源**

1. 关闭打印机电源，并小心地从打印机中拔出 MicroSD 卡。

2. 重启打印机，观察显示屏是否能正常亮起。若显示屏在拔出 MicroSD 卡后能正常显示，那么请在关机状态下将 MicroSD 卡重新插入打印机，并再次开机以验证是否因 MicroSD 卡故障导致之前的黑屏问题。

![](https://wiki.bambulab.com/x1/troubleshooting/circuit-board-power-failure/x1-sd.jpg)

### 二、检查 AP 板的工作工状态，根据 AP 主板的状态选择对应该的处理方案

打印机开机的状态下，揭开 AP 主板盖， 根据 AP 主板上的提示灯确认 AP 主板的工作状态。

![](https://wiki.bambulab.com/x1/troubleshooting/black-screen/open_the_ap_cover1.jpg)

#### 情形1：AP 板正常工作

AP 主板上的工作状态指示灯（闪烁）和电源指示灯（常亮）均处于正常状态。

![](https://wiki.bambulab.com/x1/troubleshooting/black-screen/normal_ap2.jpg)

**解决方案：**AP 板无异常，需继续确认[显示屏](https://wiki.bambulab.com/zh/x1/maintenance/replace-high-resolution-screen)和连接[FPC](https://wiki.bambulab.com/zh/x1/maintenance/replace-fpc-from-ap-to-display)。

#### 情形2：AP 主板未正常供电

AP 主板上的电源指示灯和工作状态指示灯均处于关闭状态。

![](https://wiki.bambulab.com/x1/troubleshooting/black-screen/no_power.jpg)

**解决方案：**检查 AP 板电源连接线

**操作步骤：**

1、关闭打印机电源， 拔下 AP 主板电源连接线，并重新接上，确认安装到位，然后开启打印机电源，检查指示状态，如果没有恢复正常，需继续检查该电源线在 MC 板上的连接状态；

![](https://wiki.bambulab.com/x1/troubleshooting/black-screen/power_connector_on_ap_board.jpg)

2、断开打印机电源连接，拆除背板，拔下 MC 板上 AP 板电源线插头，并重新接上，确认安装到位，然后开启打印机，再次检查 AP 板指示灯状态，如果没有恢复正常，联系售后确认。

![](https://wiki.bambulab.com/x1/troubleshooting/black-screen/power_connector_on_mc_board.jpg)

#### 情形3：AP 板供电正常，但工作状态异常

AP 主板上的工作状态指示灯熄灭，电源指示灯（常亮）正常。

![](https://wiki.bambulab.com/x1/troubleshooting/black-screen/ap_board_failed.jpg)

**解决方案：**

1. LED 灯条电缆短路，断开LED电缆连接，重新启动打印机，如AP主板能正常启动，说明可能是LED灯电缆短路了，需更换LED灯条；
2. AP主板故障，如重启不能解决，需更换AP主板。

**操作步骤：**

1. 请点击  [更换机箱LED灯条](https://wiki.bambulab.com/zh/x1/maintenance/replace-the-chamber-led) 了解更换LED灯条的具体操作;

2. 请点击  [更换AP主板](https://wiki.bambulab.com/zh/x1/maintenance/replace-ap-board) 了解更换AP主板的具体操作。

### 三、重装LCD显示屏（同时检查FPC排线外观）

在已经确认AP主板能正常工作的情况下，可以尝试重新连接显示屏。

操作步骤：请点击 [更换高清显示屏](https://wiki.bambulab.com/zh/x1/maintenance/replace-high-resolution-screen)了解显示屏的拆除和安装操作，然后开机确认问题是否已解决，如未能解决，再进行下一步确认AP主板端的FPC连接器状态。

注意事项：

1、需要先关闭打印机电源；

2、拆除显示屏时，请必务正确解除显示屏的锁定；

![](https://wiki.bambulab.com/x1/maintenance/replace-high-resolution-screen/350px-press_to_unlock.png)

3、重新安装前，请先检查接口和PIN针有无异常，FPC排线有无损伤， 如果排线有损伤，请点击 [更换显示屏FPC](https://wiki.bambulab.com/zh/x1/maintenance/replace-fpc-from-ap-to-display)了解显示屏连接排线的更换操作。

|  |  |  |
| --- | --- | --- |

### 四、 检查 AP 主板端的 FPC 连接器状态

如果重新安装 LCD 显示屏没能解决问题，也没有发现 FPC 排线和接口的异常损坏，请关闭电源，参考请点击[更换AP主板](https://wiki.bambulab.com/zh/x1/maintenance/replace-ap-board) 检查显示屏 FPC 在 AP 板上的连接状态，如发现在倾斜或松脱的现象，请重新连接。

注意：此处的 FPC 有用UV胶进行加固，如果需要重新连接排线，请务必先使用电吹风加热UV胶后再去除。

![](https://wiki.bambulab.com/x1/maintenance/replace-ap-board/350px-fpc_connected.png)

重新连接好后，可以在不锁 AP 板螺丝的情况下直接开启打印机电源，以检查问题是否能解决； 如果未能解决，请联系售后处理。

## 其他 后盖拆装

### 步骤1 - 拆除后盖螺丝

注意：这个过程涉及到很多螺丝，请将它们区分开来，并把它们放在不同的区域，以免弄混。

如图所示，取下后盖上的10颗螺丝和4颗螺丝。这是两种类型的螺丝，所以要把它们分开。

|  |  |
| --- | --- |

如图所示，断开电源连接后，取下后盖上的10颗螺丝和4颗螺丝。这是两种类型的螺丝，所以要把它们分开。

### 步骤2 -拆除后盖

拆下后盖，先将后盖从左侧（面向后盖）皮带张紧口的位置松开，再松开右侧（面向后盖）皮带张紧口的位置，以免卡住。

|  |  |
| --- | --- |

### 步骤3 - 安装后盖

安装后盖时，应首先穿过PTFE管支架和装好右侧的皮带张紧口位置。

|  |  |
| --- | --- |

#### 步骤4 - 锁紧后盖螺丝

用螺丝将后盖重新固定。注意使用的不同类型的螺丝(如下图所示的10颗螺丝和4颗螺丝)。

|  |  |
| --- | --- |



## 媒体资源

- img: https://wiki.bambulab.com/x1/troubleshooting/black-screen/black_screen.jpg
- img: https://wiki.bambulab.com/x1/troubleshooting/black-screen/%E9%BB%91%E5%B1%8F%E6%9C%89%E8%83%8C%E5%85%89.jpg
- img: https://wiki.bambulab.com/x1/troubleshooting/black-screen/%E5%B1%8F%E5%B9%95%E8%8A%B1%E5%B1%8F.jpg
- img: https://wiki.bambulab.com/x1/troubleshooting/circuit-board-power-failure/x1-sd.jpg
- img: https://wiki.bambulab.com/x1/troubleshooting/black-screen/open_the_ap_cover1.jpg
- img: https://wiki.bambulab.com/x1/troubleshooting/black-screen/normal_ap2.jpg
- img: https://wiki.bambulab.com/x1/troubleshooting/black-screen/no_power.jpg
- img: https://wiki.bambulab.com/x1/troubleshooting/black-screen/power_connector_on_ap_board.jpg
- img: https://wiki.bambulab.com/x1/troubleshooting/black-screen/power_connector_on_mc_board.jpg
- img: https://wiki.bambulab.com/x1/troubleshooting/black-screen/ap_board_failed.jpg
- img: https://wiki.bambulab.com/x1/maintenance/replace-high-resolution-screen/350px-press_to_unlock.png
- img: https://wiki.bambulab.com/x1/troubleshooting/black-screen/check_the_fpc.jpg
- img: https://wiki.bambulab.com/x1/troubleshooting/black-screen/check_the_lcd_connector.jpg
- img: https://wiki.bambulab.com/x1/troubleshooting/black-screen/check_the_fpc_connector.jpg
- img: https://wiki.bambulab.com/x1/maintenance/replace-ap-board/350px-fpc_connected.png
- img: https://wiki.bambulab.com/x1/maintenance/replace-ac-board/350px-10_screws.png
- img: https://wiki.bambulab.com/x1/maintenance/replace-ac-board/350px-4_screws.png
- img: https://wiki.bambulab.com/x1/maintenance/replace-ac-board/336px-left_side_belt_tension_port.png
- img: https://wiki.bambulab.com/x1/maintenance/replace-ac-board/350px-the_right_side_belt_tension_port.png
- img: https://wiki.bambulab.com/x1/maintenance/replace-ac-board/350px-install_the_rear_cover.png

