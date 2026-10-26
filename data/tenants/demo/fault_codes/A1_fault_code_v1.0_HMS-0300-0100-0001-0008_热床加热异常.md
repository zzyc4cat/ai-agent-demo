---
source: https://wiki.bambulab.com/zh/a1/troubleshooting/hmscode/0300_0100_0001_0008
fetched_at: 2026-10-26
title: HMS_0300-0100-0001-0008: 热床加热过程中出现异常， 加热模块可能故障。
media_count: 19
---

> 来源：https://wiki.bambulab.com/zh/a1/troubleshooting/hmscode/0300_0100_0001_0008｜抓取日期：2026-10-26｜仅供本地检索演示，版权归原作者

HMS_0300-0100-0001-0008: 热床加热过程中出现异常， 加热模块可能故障。
0300-0100-0001-0008

---


## 故障描述

在热床加热的过程中，机器内部的状态均受到了打印机的严格监控。当打印机发现热床的加热状态不符合预期时（例如AC控制线断开、AC板失效、热床线开裂、热床失效等情况），打印机会停止加热以保证系统的安全，同时提示热床可能出现故障。

![表1eng.png](https://wiki.bambulab.com/h2/troubleshooting/hmscode/0300-0100-0001-0008/%E8%A1%A81eng.png)

**可能的原因：**

- AC控制线松动或断开
- AC板坏了
- 热床信号线开裂
- 热床失效

## 故障排除

这种情况一般是热床的供电异常，导致热床无法加热。当出现该报错时，为了确保安全，**请立即停止继续使用打印机，并将打印机电源关闭。**

> **安全提示 ！** 热床是直接使用市电加热的，有高压危险，需要确保在断电的情况下进行故障排查。 在打印机开启的状态下，在屏幕上的控制界面，将热床置于较中间高度的位置，方便后面的操作。

### 工具、设备及材料

- H 2.0 六角扳手
- H 1.5 六角扳手
- 十字螺丝刀
- 镊子
- 万用表
- 电吹风

### 故障隔离流程

1. 目视检查热床电源线、电路板的连接状态
2. 断电状态下，使用万用表测量热床电阻
3. 检查AC板输出（高压危险，需要有电工基础）

## 针对A1, A1 mini 打印机

- **热床电阻测量**
 [A1](https://wiki.bambulab.com/zh/a1/troubleshooting/heatbed-not-heat-up)
 [A1 mini](https://wiki.bambulab.com/zh/a1-mini/troubleshooting/heatbed-not-heat-up)
- **更换AC板**
 [A1](https://wiki.bambulab.com/zh/a1/maintenance/ac-board-replacement)
 [A1 mini 参考主板更换](https://wiki.bambulab.com/zh/a1-mini/maintenance/mc-board-replacement-guide)
- **更换MC板**
 [A1 参考主板更换](https://wiki.bambulab.com/zh/a1/maintenance/bottom-base)
 [A1 mini 参考主板更换](https://wiki.bambulab.com/zh/a1-mini/maintenance/mc-board-replacement-guide)
- **更换热床**
 [A1](https://wiki.bambulab.com/zh/a1/maintenance/heatbed)
 [A1 mini](https://wiki.bambulab.com/zh/a1-mini/maintenance/heatbed-replacement-guide)

## 针对X1, P1系列打印机

![](https://wiki.bambulab.com/x1/troubleshooting/heatbed-not-heat-up/not_0.jpg)

### 拆解

#### 步骤1 - 拆除螺丝

> **注意：**
> 
> 这个过程涉及到很多螺丝，请将它们区分开来，并把它们放在不同的区域，以免弄混。

如图所示，断开电源连接后，取下后盖上的10颗螺丝和4颗螺丝。这是两种类型的螺丝，所以要把它们分开。

|  |  |
| --- | --- |
|  |  |

#### 步骤2 - 拆除后盖

拆下后盖，先将后盖从左侧（面向后盖）皮带张紧口的位置松开，再松开右侧（面向后盖）皮带张紧口的位置，以免卡住。

|  |  |
| --- | --- |
|  |  |

#### 步骤3 - 移除废料滑梯

拧下2颗螺丝，并拆下废料滑梯。

|  |  |
| --- | --- |
|  |  |

#### 步骤4 - 移除电源保护盖

拆下6颗螺丝，将电源模块保护盖移到一边，露出热床电源线接头。

![](https://wiki.bambulab.com/x1/maintenance/replace-ac-board/318px-6_screw.png)

### 检查

#### 步骤 5：检查连接器

拆除打印机背板和护线盖，检查热床电源线和 MC 板-AC 板连接线的连接状态，确认连接正常，无松脱或歪斜。

|  |  |
| --- | --- |
|  |  |

#### 步骤 6：检测热床电源线

移开两个保护胶套，用万用表测试阻值；

- 如果阻值在 40~60 ohms，则热床正常；
- 如果阻值不在 40~60 ohms，需要更换热床，请参考[更换热床](https://wiki.bambulab.com/zh/p1/maintenance/heat-bed)。

![](https://wiki.bambulab.com/p1/troubleshooting/heat-bed-not-heat-up/measure_the_resistance.jpg)

> 注意：测试完或维修完成后，请务必将两个保护胶套装回原位，避免短路。
>  ![](https://wiki.bambulab.com/p1/troubleshooting/heat-bed-not-heat-up/power_scokets.jpg)

#### 步骤 7：检查 AC 电源板

如果上述步骤确认热床本身无异常，那么基本上确认是 AC 电源板故障，需要更换 AC 电源板，请参考[更换 AC 电源板](https://wiki.bambulab.com/zh/p1/maintenance/ac-board)。

当然，如果能直接观察到 AC 电源板上有元器件损坏，也可以判断是 AC 电源板损坏。

![](https://wiki.bambulab.com/p1/troubleshooting/heat-bed-not-heat-up/ac_board.jpg)

### 组装

#### 步骤1 - 安装电源模块保护盖

安装电源模块保护盖，并锁紧6颗螺丝。

![](https://wiki.bambulab.com/x1/maintenance/replace-ac-board/318px-6_screw.png)

#### 步骤2 - 安装废料滑梯

安装废料滑梯，注意两边的卡扣，锁紧2颗螺丝。

|  |  |
| --- | --- |
|  |  |

#### 步骤3 - 安装后盖

安装后盖时，应首先穿过PTFE管支架和装好右侧的皮带张紧口位置。

|  |  |
| --- | --- |
|  |  |

## 针对 H2 系列打印机

**用户可视情调整各排故措施的顺序。**

### 拆解

#### 步骤1. 拆打印机后盖板，移除AC板理线盖，裸露AC板

参考Wiki[更换 H2系列 AC 板/AC 板理线盖](https://wiki.bambulab.com/zh/h2/maintenance/replace-ac-board-for) 。
 ![image3.png](https://wiki.bambulab.com/h2/troubleshooting/hmscode/0300-0100-0001-0008/image3.png)

### 检查

#### 步骤2. 检查AC板端电源连接

拔下电源线，确认PIN针无异常后，重新连接。暂时连接电源启动打印机，设置床温确认问题是否解决。如果没有解决，断开电源线连接后，继续下一步。

![image-4.png](https://wiki.bambulab.com/h2/troubleshooting/hmscode/0300-0100-0001-0008/image-4.png)

#### 步骤3. 检查热床电阻

如果家中有万用表，请将下图中接线拔下后，测量接线间电阻值。

![image-4.png](https://wiki.bambulab.com/h2/troubleshooting/hmscode/0300-0100-0001-0008/image-4.png)

正常情况下阻值如下表所示。

|  | 蓝色线和红色线间电阻 | 蓝色线和棕色线间电阻 |
| --- | --- | --- |
| 220V高压版本 | 28~35 Ω | 180~220 Ω |
| 110V低压版本 | 9~11 Ω | 45~55 Ω |

如果测量阻值无示数或过大，则很可能是热床端的电源连接开路或热床内部元件烧坏了。请参考Wiki[更换 H2S 热床组件](https://wiki.bambulab.com/zh/h2s/maintenance/replace-heatbed-unit) 或 [更换 H2D 热床组件](https://wiki.bambulab.com/zh/h2/maintenance/replace-heatbed-unit) 更换热床。

#### 步骤4. 检查AC电源板外观

目视检查AC板外观，包括摇晃检查电源输入线是否有松动（如有，请重新连接固定）。板上的元件器有无明显的烧坏痕迹（如有，请参考[更换 H2系列 AC 板/AC 板理线盖](https://wiki.bambulab.com/zh/h2/maintenance/replace-ac-board-for) 进行AC电源板的更换）。确认无异常，则进行下一步确认。

![image-6.png](https://wiki.bambulab.com/h2/troubleshooting/hmscode/0300-0100-0001-0008/image-6.png)

#### 步骤5. 检查热床测温电阻安装

检查MC板上热床测温电阻连接器（下图中24号连接器）是否插到位，可重新拔插。

![image-7.png](https://wiki.bambulab.com/h2/troubleshooting/hmscode/0300-0100-0001-0008/image-7.png)

若以上措施未能解决问题，请联系客服。

### 组装

#### 步骤6. 安装AC板理线盖和打印机背板

请参考Wiki[更换 H2系列 AC 板/AC 板理线盖](https://wiki.bambulab.com/zh/h2/maintenance/replace-ac-board-for) 将AC板与打印机背板依次装回。

## 错误信息

HMS_0300-0100-0001-0008: 热床加热过程中出现异常， 加热模块可能故障。

“热床加热过程中出现异常， 加热模块可能故障。”

0300-0100-0001-0008



## 媒体资源

- img: https://wiki.bambulab.com/h2/troubleshooting/hmscode/0300-0100-0001-0008/%E8%A1%A81eng.png
- img: https://wiki.bambulab.com/x1/troubleshooting/heatbed-not-heat-up/not_0.jpg
- img: https://wiki.bambulab.com/x1/maintenance/replace-ac-board/350px-10_screws.png
- img: https://wiki.bambulab.com/x1/maintenance/replace-ac-board/350px-4_screws.png
- img: https://wiki.bambulab.com/x1/maintenance/replace-ac-board/336px-left_side_belt_tension_port.png
- img: https://wiki.bambulab.com/x1/maintenance/replace-ac-board/350px-the_right_side_belt_tension_port.png
- img: https://wiki.bambulab.com/x1/maintenance/replace-ac-board/350px-remove_the_excess_chute1.png
- img: https://wiki.bambulab.com/x1/maintenance/replace-ac-board/350px-remove_the_excess_chute2.png
- img: https://wiki.bambulab.com/x1/maintenance/replace-ac-board/318px-6_screw.png
- img: https://wiki.bambulab.com/p1/troubleshooting/heat-bed-not-heat-up/power_scokets.jpg
- img: https://wiki.bambulab.com/p1/troubleshooting/heat-bed-not-heat-up/mc_to_ac_cable.jpg
- img: https://wiki.bambulab.com/p1/troubleshooting/heat-bed-not-heat-up/measure_the_resistance.jpg
- img: https://wiki.bambulab.com/p1/troubleshooting/heat-bed-not-heat-up/ac_board.jpg
- img: https://wiki.bambulab.com/x1/maintenance/replace-ac-board/350px-install_the_excess_chute1.png
- img: https://wiki.bambulab.com/x1/maintenance/replace-ac-board/350px-install_the_rear_cover.png
- img: https://wiki.bambulab.com/h2/troubleshooting/hmscode/0300-0100-0001-0008/image3.png
- img: https://wiki.bambulab.com/h2/troubleshooting/hmscode/0300-0100-0001-0008/image-4.png
- img: https://wiki.bambulab.com/h2/troubleshooting/hmscode/0300-0100-0001-0008/image-6.png
- img: https://wiki.bambulab.com/h2/troubleshooting/hmscode/0300-0100-0001-0008/image-7.png

