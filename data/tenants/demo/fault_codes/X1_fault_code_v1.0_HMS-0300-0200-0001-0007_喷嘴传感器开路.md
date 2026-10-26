---
source: https://wiki.bambulab.com/zh/x1/troubleshooting/hmscode/0300_0200_0001_0007
fetched_at: 2026-10-26
title: HMS_0300-0200-0001-0007: 喷嘴温控异常，温度传感器可能开路。
media_count: 18
---

> 来源：https://wiki.bambulab.com/zh/x1/troubleshooting/hmscode/0300_0200_0001_0007｜抓取日期：2026-10-26｜仅供本地检索演示，版权归原作者

HMS_0300-0200-0001-0007: 喷嘴温控异常，温度传感器可能开路。
0300-0200-0001-0007

---


## 为何会出现此错误

喷头温度控制主要包括一个加热器和一个NTC传感器。当NTC传感器开路时，TH板无法获得正确的喷头温度，会导致加热器持续发热，导致打印失败。

|  |  |  |
| --- | --- | --- |

以下是出现此 HMS 错误代码的可能原因：

1. 工具头线与连接器接触不良

2. NTC传感器坏了

3. 传感器线断了

4. 未安装热端硅胶套，风扇冷却热端温度。

## 安全警告

> 喷嘴温度很高，请避免触摸喷嘴。 **请务必确保在打印机断电并断开电源连接的情况下，执行热端、NTC传感器、加热器连接线的插拔。** **请在上电前，务必检查各连接线插头与插槽，确保没有错位。** ![](https://wiki.bambulab.com/x1/troubleshooting/hmscode/toolhead/hotend_connector.png)

## 故障排除指南

### 检查热端硅胶套

检查硅胶套是否遗失、掉落或大面积破损，如果外观良好，重新安装并不会轻易掉落后恢复打印。

可参考[更换硅胶套](https://wiki.bambulab.com/zh/x1/maintenance/replacing-the-silicone-sock-for-hotend)

![a1系列硅胶套.jpg](https://wiki.bambulab.com/x1/maintenance/replacing-the-silicone-sock-for-hotend/a1%E7%B3%BB%E5%88%97%E7%A1%85%E8%83%B6%E5%A5%97.jpg)

### X1 排查测量

#### 插拔 NTC 线

重新插拔 NTC 线，查看错误提示是否消失。

#### 拆解热端

请参考此[WIKI](https://wiki.bambulab.com/zh/x1/maintenance/replace-hotend)拆解热端，并检查NTC传感器或电线是否损坏。

#### 用万用表测量

如果您有万用表可以尝试根据下面的步骤测量一下热端组件的电阻以判断是否为热端故障。

常温下陶瓷加热片的电阻一般是**12Ω**，热敏电阻NTC的阻值为**50-100 KΩ**:

|  |  |
| --- | --- |
|  |  |
|  |  |

#### 重新插拔 10pin 连接器

如果问题仍然存在，**请重新插拔 V8 TH 板的 10Pin 连接器（有时需要重新插拔几次）；并检查 10 针插头是否有烧坏的迹象。操作前您需要用镊子先清理连接器上的硅胶**。

如果您的 X1 系列打印机有 V9 TH 板，请重新插拔此 FPC 的两端。

| V8 TH板 | V9 TH 板 |
| --- | --- |

> 请参考以下 wiki 获得更多相关信息：
>  [更换工具头挤出板组件 | Bambu Lab Wiki](https://wiki.bambulab.com/zh/x1/maintenance/replace-the-th-board-assembly)
>  [更换工具头电路板（新版） | Bambu Lab Wiki](https://wiki.bambulab.com/zh/x1/maintenance/toolhead_boards_v9)

### P1 排查测量

#### 插拔 NTC 线

重新插拔 NTC 线，查看错误提示是否消失。

#### 拆解热端

请参考此[WIKI](https://wiki.bambulab.com/zh/x1/maintenance/replace-hotend)拆解热端，并检查NTC传感器或电线是否损坏。

#### 用万用表测量

如果您有万用表可以尝试根据下面的步骤测量一下热端组件的电阻以判断是否为热端故障。

常温下陶瓷加热片的电阻一般是 **10Ω**（测量下图中红色箭头指向的两个 pin 脚），热敏电阻 NTC 的阻值为**100 KΩ**（测量下图中橙色箭头指向的两个 pin 脚）:

|  |  |
| --- | --- |
|  |  |

#### 重新插拔 FPC

如果问题仍然存在，**请重新插拔 FPC 的两端（有时需要重新插拔几次）。**

![](https://wiki.bambulab.com/p1/troubleshooting/cutter-stuck/fpc_disconnected.jpg)

> 请参考以下 wiki 获得更多相关信息：
>  [更换工具头电路板 | Bambu Lab Wiki](https://wiki.bambulab.com/zh/p1/maintenance/pcb-boards-on-toolhead)

### A1 排查测量

#### 插拔 NTC 线

重新插拔 NTC 线，查看错误提示是否消失。

#### 拆解热端

请参考此[WIKI](https://wiki.bambulab.com/zh/a1-mini/maintenance/hotend-heating-assembly-replacement)拆解热端，并检查 NTC 传感器或电线是否损坏。

#### 用万用表测量

如果您有万用表可以尝试根据下面的步骤测量一下热端组件的电阻以判断是否为热端故障。

通常 A1 系列打印机报错为“喷嘴温度故障”，测量加热组件的电阻需要先拆开工具头后盖，加热组件的插头为 TH 板上的 1 号插头。

|  |  |
| --- | --- |
|  |  |

常温下陶瓷加热片的电阻一般是**7Ω**（测量下图中红色箭头指向的两个pin脚），热敏电阻 NTC 的阻值为**100 KΩ**（测量下图中橙色箭头指向的两个 pin 脚，NTC 的电阻受温度波动范围大）:

|  |  |
| --- | --- |
|  |  |

### 热敏电阻特性曲线

该热敏电阻为负温度系数热敏电阻（NTC）常温 25℃ 时电阻值为 100K，如果当前处于冬季电阻值会随着气温下降而升高，反之处于夏季随着气温的升高电阻值也会出现下降的情况。

在实际测量中，由于测量仪器的精度限制、环境温度的瞬时波动、热敏电阻的热响应时间以及测量电路的寄生参数影响等因素，可能导致测量值与理论曲线存在微小偏差，这些偏差属于正常现象，不会影响热敏电阻的正常使用和温度检测功能。

![ntc特性曲线zh.png](https://wiki.bambulab.com/x1/troubleshooting/hmscode/ntc%E7%89%B9%E6%80%A7%E6%9B%B2%E7%BA%BFzh.png)

#### 联系售后

如果消息仍然出现，请联系售后团队。

## 错误信息

HMS_0300-0200-0001-0007: 喷嘴温控异常，温度传感器可能开路。

“喷嘴温控异常，温度传感器可能开路。”

0300-0200-0001-0007



## 媒体资源

- img: https://wiki.bambulab.com/x1/troubleshooting/hmscode/toolhead/x1c_th_connector_board.png
- img: https://wiki.bambulab.com/p1/maintenance/toolhead-enclosure/insert_the_tube.jpg
- img: https://wiki.bambulab.com/n1/maintenance/hotend-heating-assembly-replacement/replacement-step2-3-en.jpg
- img: https://wiki.bambulab.com/x1/troubleshooting/hmscode/toolhead/hotend_connector.png
- img: https://wiki.bambulab.com/x1/troubleshooting/hmscode/toolhead/heater/measure_x1_2.jpg
- img: https://wiki.bambulab.com/x1/troubleshooting/hmscode/toolhead/heater/measure_x1_1.jpg
- img: https://wiki.bambulab.com/x1/troubleshooting/hmscode/toolhead/heater/heater_res_cn.png
- img: https://wiki.bambulab.com/x1/troubleshooting/hmscode/toolhead/heater/thermistor_res_cn.png
- img: https://wiki.bambulab.com/x1/troubleshooting/hotend_heater_over_temperature/10pin_connector.png
- img: https://wiki.bambulab.com/x1/troubleshooting/hmscode/toolhead/heater-short-circuit/fpc_v9.jpeg
- img: https://wiki.bambulab.com/x1/troubleshooting/hmscode/toolhead/heater/resistance_value_p1_cn.png
- img: https://wiki.bambulab.com/x1/troubleshooting/hmscode/toolhead/heater/measure_p1.jpg
- img: https://wiki.bambulab.com/p1/troubleshooting/cutter-stuck/fpc_disconnected.jpg
- img: https://wiki.bambulab.com/n1/a1-mini-print-head/%E6%8B%86%E8%A3%85/%E7%A7%BB%E9%99%A4%E5%B7%A5%E5%85%B7%E5%A4%B4%E5%90%8E%E7%9B%96.png
- img: https://wiki.bambulab.com/n1/a1-mini-print-head/connectors_on_th_2.jpg
- img: https://wiki.bambulab.com/x1/troubleshooting/hmscode/toolhead/heater/resistance_value_a1_cn.png
- img: https://wiki.bambulab.com/x1/troubleshooting/hmscode/toolhead/heater/measure_a1.jpg
- img: https://wiki.bambulab.com/x1/troubleshooting/hmscode/ntc%E7%89%B9%E6%80%A7%E6%9B%B2%E7%BA%BFzh.png

