---
source: https://wiki.bambulab.com/zh/x1/troubleshooting/ams-power-failure
fetched_at: 2026-10-26
title: AMS 无法上电
media_count: 7
---

> 来源：https://wiki.bambulab.com/zh/x1/troubleshooting/ams-power-failure｜抓取日期：2026-10-26｜仅供本地检索演示，版权归原作者

AMS 无法上电
本文介绍了 AMS 无法上电的故障排除

---


## 问题现象

当我们给打印机连接 AMS 后，发现 AMS 的插槽没有 LED 灯闪烁，插入料线后 AMS 也没有反应。

![](https://wiki.bambulab.com/x1/troubleshooting/ams-power-failure/301px-led_flinkle_when_power_on.png)

## 操作指导

这个问题通常是由线缆连接异常引起的，所以请按照以下步骤缩小故障范围。

### 1. Pin 脚检查

首先可以尝试重新插拔 4&6Pin 线缆，检查 Bambu Bus 4Pin&6Pin 线缆（连接打印机—缓冲器— AMS 的两条线缆）的 Pin 脚是否存在变形或开路，如下图。

![](https://wiki.bambulab.com/ams_power_on_failure/pin_open.png)

### 2. 检查线缆连接

- 建议稍微摇晃或弯曲 4Pin 和 6Pin 的插头和线缆，或者稍微拔出插头（不要完全拔出），看看 AMS 是否能在短时间内被打印机检测到，这样我们就可以把故障范围缩小到插头/电缆。

### 3. 测量电压

- 如果您有万用表，请检查 4Pin 和 6Pin 电缆的针脚连通性和电压是否正常（24V）。

![](https://wiki.bambulab.com/ams_power_on_failure/ams_cable_pin_define.drawio.svg)

从缓冲器上断开 4Pin 线缆，开启打印机，测试 4Pin 线缆的电压。

![](https://wiki.bambulab.com/ams_power_on_failure/%E6%B5%8B4pin%E7%BA%BF%E7%94%B5%E5%8E%8B.png)

然后将 4Pin 线缆连接回打印机，将 6Pin 线缆与 AMS 断开。测试 6pin 电缆的电压。

![](https://wiki.bambulab.com/ams_power_on_failure/%E6%B5%8B6pin%E7%BA%BF%E7%94%B5%E5%8E%8B.png)

- 如果 AMS 外部的引脚和电压都是正常的，但故障仍然存在，检查 AMS 内部的电源线缆（Power）是否松动或者脱落以及内部电压是否正常（24V）。
- 检查 AMS 主板针脚是否有存在进水腐蚀的情况。

![](https://wiki.bambulab.com/ams_power_on_failure/power_cable_inside_ams.png)

- 如果 AMS 主板的 24V 也是正常的，**请拔掉主板上的其他的线只保留电源线和通信线(485)，测 U2 芯片上的 GND/3.3V 和 GND/6.6V**是否正常（绿框中），并同时观察一下屏幕上 AMS 是不是被识别到了。如果此时 AMS 能被打印机检测到，把 AMS 主板上的其他模块的线依次接上，看看接回哪条线的时候 AMS 就无法上电了，这样就能确认是哪个部件故障导致整个 AMS 无法工作的。

![](https://wiki.bambulab.com/x1/troubleshooting/ams-power-failure/ams%E4%B8%8A%E7%94%B5.jpg)

- 请按上述步骤进行测量和排查，根据测试结果联系售后服务团队以获得进一步帮助。



## 媒体资源

- img: https://wiki.bambulab.com/x1/troubleshooting/ams-power-failure/301px-led_flinkle_when_power_on.png
- img: https://wiki.bambulab.com/ams_power_on_failure/pin_open.png
- img: https://wiki.bambulab.com/ams_power_on_failure/ams_cable_pin_define.drawio.svg
- img: https://wiki.bambulab.com/ams_power_on_failure/%E6%B5%8B4pin%E7%BA%BF%E7%94%B5%E5%8E%8B.png
- img: https://wiki.bambulab.com/ams_power_on_failure/%E6%B5%8B6pin%E7%BA%BF%E7%94%B5%E5%8E%8B.png
- img: https://wiki.bambulab.com/ams_power_on_failure/power_cable_inside_ams.png
- img: https://wiki.bambulab.com/x1/troubleshooting/ams-power-failure/ams%E4%B8%8A%E7%94%B5.jpg

