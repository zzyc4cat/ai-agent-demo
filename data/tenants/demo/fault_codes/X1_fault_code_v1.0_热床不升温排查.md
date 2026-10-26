---
source: https://wiki.bambulab.com/zh/x1/troubleshooting/heatbed-not-heat-up
fetched_at: 2026-10-26
title: X1 系列热床不升温问题排查
media_count: 28
---

> 来源：https://wiki.bambulab.com/zh/x1/troubleshooting/heatbed-not-heat-up｜抓取日期：2026-10-26｜仅供本地检索演示，版权归原作者

X1 系列热床不升温问题排查
本指南介绍两种热床不升温情形及其解决方案。

---


## 问题现象

打印机在准备打印和打印过程中，出现热床无法加热或者床温为零，手动设置床温也无响应。

## 原因及解决方案

导致热床温度异常主要的几个原因及解决方案如下：

1. 连接线接口处接触不良，包括热床电源线、热床通信线和热床 NTC 线，需要用户协助进行排查和解决；
2. MC 板到热床的连接线材暗断， 要更换热床通信线，需要联系售后安排处理。
3. 热床内部元器件烧坏，要更换热床，需要联系售后安排处理；
4. AC 板故障，电压输出有问题，需要更换 AC 板。

## 安全和操作提示

1. 热床是直接使用市电加热的，有高压危险，需要确保在断电的情况下进行故障排查。

2. 在打印机开启的状态下，在屏幕上的控制界面，将热床置于较中间高度的位置，方便后面的操作。

## 所需的工具

- H1.5 和 H2.0 内六角扳手
- 镊子
- 电吹风

## 情形一：热床温度显示为 0

这种情形一般是热床的温度信息缺失导致的。

![](https://wiki.bambulab.com/x1/troubleshooting/heatbed-not-heat-up/t0.jpg)

### 排查方案

1. 检查热床与 MC 板的连接线即热床通信线的连接状态

2. 检查 NTC 的连接状态

注意：这两条线的连接器处都有打白色硅胶固定的，如果没有看到明显的倾斜或退 PIN 的情况，只需要重新按压确认即可； 实在需要断开连接时，可以使用电吹风对硅胶进行加热，降低硬度后再移除硅胶或断开连接。

### 操作步骤（拆解检查）

#### 步骤 1 - 拆除螺丝

注意：这个过程涉及到很多螺丝，请将它们区分开来，并把它们放在不同的区域，以免弄混。

如图所示，断开电源连接后，取下后盖上的 10 颗螺丝和 4 颗螺丝。这是两种类型的螺丝，所以要把它们分开。

|  |  |
| --- | --- |
|  |  |

#### 步骤 2 - 拆除后盖

拆下后盖，先将后盖从左侧（面向后盖）皮带张紧口的位置松开，再松开右侧（面向后盖）皮带张紧口的位置，以免卡住。

|  |  |
| --- | --- |
|  |  |

#### 步骤 3 - 移除废料滑梯

拧下 2 颗螺丝，并拆下废料滑梯。

|  |  |
| --- | --- |
|  |  |

#### 步骤 4 - 检查连接器

检查 MC 板端的连接线状态，确认连接没有浮起和退 PIN。检查确认后，可重新连接电源，开机确认热床温度是否不再显示为 0； 如果故障未排除，则需要再检查热床端的连接状态。

![](https://wiki.bambulab.com/x1/troubleshooting/heatbed-not-heat-up/check_the_connector_on_mc_board.jpg)

#### 步骤 5 - 拆下热床预紧螺母

拧下 3 个预紧螺母，将加热床从金属支架上解锁。 请注意，每个螺母顶部还有一个橡胶环。

|  |  |
| --- | --- |
|  |  |

#### 步骤 6 - 打开热床

小心打开加热床，因为里面有电缆连接，取下已松脱出来的预紧弹簧。

![](https://wiki.bambulab.com/x1/troubleshooting/heatbed-not-heat-up/open.jpg)

#### 步骤 7 - 检查连接状态

这里可以同时检查热床到 MC 板的连接线和 NTC 线的连接，其中 2PIN 的是 NTC 连接线，需确认连接器有无松动，连接线有无松出。 检查确认OK或重新连接后，可再次连接电源，开机确认热床温度是否不再显示为0； 如果故障仍未排除，则需要联系售后进行确认。

![](https://wiki.bambulab.com/x1/troubleshooting/heatbed-not-heat-up/ntc_and_mc-heatbed.jpg)

### 组装步骤

#### 步骤 1 - 安装电源模块保护盖

安装电源模块保护盖，并锁紧 6 颗螺丝。

![](https://wiki.bambulab.com/x1/maintenance/replace-ac-board/318px-6_screw.png)

#### 步骤 2 - 安装废料滑梯

安装废料滑梯，注意两边的卡扣，锁紧 2 颗螺丝。

|  |  |
| --- | --- |
|  |  |

#### 步骤 3 - 安装后盖

安装后盖时，应首先穿过 PTFE 管支架和装好右侧的皮带张紧口位置。

|  |  |
| --- | --- |
|  |  |

#### 步骤 4 - 锁紧螺丝

用螺丝将后盖重新固定。注意使用的不同类型的螺丝(如下图所示的 10 颗螺丝和 4 颗螺丝)。

|  |  |
| --- | --- |
|  |  |

## 情形二：热床温度不为 0

这种情况一般是热床的供电异常，导致热床无法加热。

![](https://wiki.bambulab.com/x1/troubleshooting/heatbed-not-heat-up/not_0.jpg)

### 排查方案

1. 检查热床电源线的连接状态

2. 检查 AC 板输出（高压危险，需要有电工基础）

### 操作步骤（拆解检查）

#### 步骤 1 - 拆除螺丝

注意：这个过程涉及到很多螺丝，请将它们区分开来，并把它们放在不同的区域，以免弄混。

如图所示，断开电源连接后，取下后盖上的 10 颗螺丝和 4 颗螺丝。这是两种类型的螺丝，所以要把它们分开。

|  |  |
| --- | --- |
|  |  |

#### 步骤 2 - 拆除后盖

拆下后盖，先将后盖从左侧（面向后盖）皮带张紧口的位置松开，再松开右侧（面向后盖）皮带张紧口的位置，以免卡住。

|  |  |
| --- | --- |
|  |  |

#### 步骤 3 - 移除废料滑梯

拧下 2 颗螺丝，并拆下废料滑梯。

|  |  |
| --- | --- |
|  |  |

#### 步骤 4 - 移除电源保护盖

拆下 6 颗螺丝，将电源模块保护盖移到一边，露出热床电源线接头。

|  |  |
| --- | --- |
|  |  |

#### 步骤 5 - 检查 AC 板端电源连接

拔下电源线，确认 PIN 针无异常后，重新连接。暂时连接电源启动打印机，设置床温确认问题是否解决。如果没有解决，断开电源线连接后，继续下一步。

|  |  |
| --- | --- |
|  |  |

提醒： 如果家中有万用表，也可以测试一下两个pin的电阻值，正常情况下阻值约为50~60欧，如果阻值无示数，则很可能是热床端的电源连接开路或热床内部元件烧坏了。

![](https://wiki.bambulab.com/x1/troubleshooting/heatbed-not-heat-up/check_the_r.jpg)

#### 步骤 6 - 检查热床底下的电源线连接

警告：务必确认操作前，已断开电源连接。

因为该连接器一般是打了白色硅胶的，可能无法直接看清楚是否连接正常。只需要用镊子头多次尝试将连接接头往接口处推动即可。按压后，连接电源启动打印机，设置床温确认问题是否解决。如果问题没有解决，继续下一步检查 AC 板输出。

|  |  |
| --- | --- |
|  |  |

#### 步骤 7 - 检查 AC 电源板外观

目视检查 AC 板外观，包括摇晃检查电源输入线是否有松动（如有，重新连接固定），板上的元件器有无明显的烧坏痕迹（如有，请参考 [更换 AC 电源板](https://wiki.bambulab.com/zh/x1/maintenance/replace-ac-board)进行 AC 电源板的更换）。确认无异常，则进行下一步确认。

![](https://wiki.bambulab.com/x1/troubleshooting/heatbed-not-heat-up/check_the_input_cables.jpg)

#### 步骤 8 - 检查 AC 板电压输出

> 警告：这个操作，检测的是市电电压，不建议无相关知识的人员操作。

在打印开启的状态下，用万用表的交流电压测试档，检查输出电压，这个电压应该与当地的使用电压相同。如果输出电压有异常，说明 AC 板有问题，请参考 [更换AC电源板](https://wiki.bambulab.com/zh/x1/maintenance/replace-ac-board)进行 AC 电源板的更换。

|  |  |
| --- | --- |
|  |  |

以上操作如果无法排除故障，则需要联系售后进行确认。

### 组装步骤

#### 步骤 1 - 安装预紧弹簧

握住热床的上部，将预紧弹簧一个接一个地安装到加热床螺钉上。

![](https://wiki.bambulab.com/x1/maintenance/heatbed-force-sensor/install_the_springs.jpg)

#### 步骤 2 - 安装热床

现在您可以合上热床并将它与支架固定在一起。 从加热床顶部轻轻按压，并确认所有三个螺钉的个根部都可以穿过传感器支架上的孔。

![](https://wiki.bambulab.com/x1/maintenance/heatbed-force-sensor/screw.jpg)

#### 步骤 3 - 锁定预紧螺母

将橡胶圈放在 3 个预紧螺母上，然后将它们均匀拧入，一次拧一点。不要锁定它们。继续均匀地拧入螺母，直到螺柱与螺母底部齐平（见下图）。

|  |  |
| --- | --- |
|  |  |



## 媒体资源

- img: https://wiki.bambulab.com/x1/troubleshooting/heatbed-not-heat-up/t0.jpg
- img: https://wiki.bambulab.com/x1/maintenance/replace-ac-board/350px-10_screws.png
- img: https://wiki.bambulab.com/x1/maintenance/replace-ac-board/350px-4_screws.png
- img: https://wiki.bambulab.com/x1/maintenance/replace-ac-board/336px-left_side_belt_tension_port.png
- img: https://wiki.bambulab.com/x1/maintenance/replace-ac-board/350px-the_right_side_belt_tension_port.png
- img: https://wiki.bambulab.com/x1/maintenance/replace-ac-board/350px-remove_the_excess_chute1.png
- img: https://wiki.bambulab.com/x1/maintenance/replace-ac-board/350px-remove_the_excess_chute2.png
- img: https://wiki.bambulab.com/x1/troubleshooting/heatbed-not-heat-up/check_the_connector_on_mc_board.jpg
- img: https://wiki.bambulab.com/x1/troubleshooting/heatbed-not-heat-up/nut.jpg
- img: https://wiki.bambulab.com/x1/maintenance/heatbed-force-sensor/rubber_on_the_nuts.jpg
- img: https://wiki.bambulab.com/x1/troubleshooting/heatbed-not-heat-up/open.jpg
- img: https://wiki.bambulab.com/x1/troubleshooting/heatbed-not-heat-up/ntc_and_mc-heatbed.jpg
- img: https://wiki.bambulab.com/x1/maintenance/replace-ac-board/318px-6_screw.png
- img: https://wiki.bambulab.com/x1/maintenance/replace-ac-board/350px-install_the_excess_chute1.png
- img: https://wiki.bambulab.com/x1/maintenance/replace-ac-board/350px-install_the_rear_cover.png
- img: https://wiki.bambulab.com/x1/troubleshooting/heatbed-not-heat-up/not_0.jpg
- img: https://wiki.bambulab.com/x1/maintenance/replace-ac-board/350px-remove_the_power_board_cover.png
- img: https://wiki.bambulab.com/x1/troubleshooting/heatbed-not-heat-up/check_the_pins.jpg
- img: https://wiki.bambulab.com/x1/maintenance/replace-ac-board/354px-disconnect_heatbed_power_cable.png
- img: https://wiki.bambulab.com/x1/troubleshooting/heatbed-not-heat-up/check_the_r.jpg
- img: https://wiki.bambulab.com/x1/troubleshooting/heatbed-not-heat-up/connector_under_the_bed.jpg
- img: https://wiki.bambulab.com/x1/troubleshooting/heatbed-not-heat-up/push_the_connector.jpg
- img: https://wiki.bambulab.com/x1/troubleshooting/heatbed-not-heat-up/check_the_input_cables.jpg
- img: https://wiki.bambulab.com/x1/troubleshooting/heatbed-not-heat-up/av.jpg
- img: https://wiki.bambulab.com/x1/troubleshooting/heatbed-not-heat-up/check_the_v.jpg
- img: https://wiki.bambulab.com/x1/maintenance/heatbed-force-sensor/install_the_springs.jpg
- img: https://wiki.bambulab.com/x1/maintenance/heatbed-force-sensor/screw.jpg
- img: https://wiki.bambulab.com/x1/maintenance/heatbed-force-sensor/check_the_nut_position.jpg

