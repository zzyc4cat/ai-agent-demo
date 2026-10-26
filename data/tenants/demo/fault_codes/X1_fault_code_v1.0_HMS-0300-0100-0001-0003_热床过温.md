---
source: https://wiki.bambulab.com/zh/x1/troubleshooting/hmscode/0300_0100_0001_0003
fetched_at: 2026-10-26
title: HMS_0300-0100-0001-0003: 热床温控异常，加热器过温。
media_count: 3
---

> 来源：https://wiki.bambulab.com/zh/x1/troubleshooting/hmscode/0300_0100_0001_0003｜抓取日期：2026-10-26｜仅供本地检索演示，版权归原作者

HMS_0300-0100-0001-0003: 热床温控异常，加热器过温。
0300-0100-0001-0003

---


## 故障现象

该告警表明热床实际温度高于设定温度。

![heatbed_over_temp_example](https://wiki.bambulab.com/x1/maintenance/heatbed_over_temp/heatbed_over_temp_example.png)

热床温控异常，加热器过温示例

打印机热床温度控制系统如下图所示，主要包含：MC板、AC板、电源、热床（含热床温度传感器）。MC板下达热床温控指令，控制AC板给热床供电加热。同时，热床上的温度传感器将热床实际温度反馈给MC板，实现热床温控的闭环。

A1mini打印机因为主板整合了MC板、AC板的功能，因此温控链路有所区别，主要包含：主板、电源、热床（含热床温度传感器）。

![heatbed_over_temp](https://wiki.bambulab.com/x1/maintenance/heatbed_over_temp/tempover.png)

热床温控系统示意图

热床实际温度超过设定温度的常见原因是：

- 热床加热供电链路异常（AC板/主板故障），导致给热床持续供电加热
- 热床温度传感器故障，识别的热床温度错误

## 故障排除

### 故障隔离流程

下图展示故障隔离的主要流程。

![heatbed_temp_control_troubleshooting_cn](https://wiki.bambulab.com/h2c/heatbed_temp_control_troubleshooting_cn.png)

热床超温故障隔离流程

### 排故措施

1. 热床加热供电链路异常

- [针对X/P1打印机，更换AC板](https://wiki.bambulab.com/zh/p1/maintenance/ac-board)
- [针对 H 系列打印机，更换AC](https://wiki.bambulab.com/zh/h2/maintenance/replace-ac-board-for)
- [针对 P2S 打印机，更换 AC](https://wiki.bambulab.com/zh/p2s/maintenance/replace-mc-and-ac-boards)
- [针对 A1 打印机，更换 AC 板](https://wiki.bambulab.com/zh/a1/maintenance/bottom-base)
- [针对A1mini打印机，更换主板](https://wiki.bambulab.com/zh/a1-mini/maintenance/mc-board-replacement-guide)

1. 热床测温链路异常

- [针对X/P打印机，更换V3热床](https://wiki.bambulab.com/zh/x1/maintenance/Replacing-the-heat-bed-v3)/[更换V2热床](https://wiki.bambulab.com/zh/x1/maintenance/Replacing-the-heat-bed)
- [针对H系列打印机，更换热床](https://wiki.bambulab.com/zh/h2/maintenance/replace-heatbed-unit)
- [针对 P2S 打印机，更换热床](https://wiki.bambulab.com/zh/p2s/maintenance/replace-heatbed)
- [针对A1打印机，更换热床](https://wiki.bambulab.com/zh/a1/maintenance/heatbed)
- [针对A1mini打印机，更换热床](https://wiki.bambulab.com/zh/a1-mini/maintenance/heatbed-replacement-guide)



## 媒体资源

- img: https://wiki.bambulab.com/x1/maintenance/heatbed_over_temp/heatbed_over_temp_example.png
- img: https://wiki.bambulab.com/x1/maintenance/heatbed_over_temp/tempover.png
- img: https://wiki.bambulab.com/h2c/heatbed_temp_control_troubleshooting_cn.png

