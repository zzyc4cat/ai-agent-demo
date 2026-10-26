---
source: https://wiki.bambulab.com/zh/x1/troubleshooting/ams_buffer_signal_lost
fetched_at: 2026-10-26
title: AMS一直进料退料循环
media_count: 6
---

> 来源：https://wiki.bambulab.com/zh/x1/troubleshooting/ams_buffer_signal_lost｜抓取日期：2026-10-26｜仅供本地检索演示，版权归原作者

AMS一直进料退料循环

---


## 问题现象:

当AMS进料时，AMS处于进料-退料循环，始终无法将料线送入工具头。

## 问题原因

主要原因有以下几点：

1. 线缆连接不良：连接AMS缓冲器与AMS之间的6pin线连接不良；或AMS电源板与主板之间的线连接不良;
2. 缓冲区的滑块或者弹簧卡住了
3. 缓冲器或AMS主板损坏;

## 排查步骤

### 1. 重新连接6Pin线并检查Pin脚

重新连接从缓冲器到AMS的6pin电缆，确保插紧。然后再次尝试进料，看看它是否可以成功地送入工具头。、

如果仍然有问题，拔掉线缆，检查Bambu Bus 6Pin线缆的引脚是否开路，如下图。

![](https://wiki.bambulab.com/ams_buffer_signal_lost/%E6%A3%80%E6%9F%A56pin%E7%BA%BFpin%E8%84%9A.png)

### 2. 检查缓冲器的弹簧和滑块

请检查缓冲器的弹簧是否卡住，滑块是否能左右顺利地移动。

![](https://wiki.bambulab.com/x1/manual/connect-ams/check_buffer_spring.png)

### 3. AMS内部连接检查

检查AMS内部的总线线缆（Bus）是否松动或者脱落。

![](https://wiki.bambulab.com/ams_is_not_detected/bus_inside_ams.png)

- 建议将总线的线缆的两端重新插好，然后试着重新进料，看看是否可以恢复，这样我们就可以把故障缩小到总线上。
- **如果你有万用表，**请先对这条电缆的所有引脚进行连续性检查。。

#### 4. 测量电压

如果连通性正常，请尝试将料线退回AMS，检查AMS缓冲器滑块是否回到最左侧，如下图所示:

![](https://wiki.bambulab.com/ams_buffer_signal_lost/buffer.png)

然后测量6Pin线缆（从AMS端拔出）针脚之间的电压。

![](https://wiki.bambulab.com/ams_buffer_signal_lost/ams_buffer.drawio.svg)

![](https://wiki.bambulab.com/ams_buffer_signal_lost/%E6%B5%8B%E7%BC%93%E5%86%B2%E5%8C%BA%E7%94%B5%E5%8E%8B.png)

正常的电压应如下表所示。**注意要提前退料，使缓冲区的滑块回到最左侧，否则测的电压值会不一样。**

| pin-pin | Voltage |
| --- | --- |
| GND-Buffer_A | ≈0.5-1.0V |
| GND-Buffer_B | ≈2.8-2.3V |

这两个电压值加起来约为3.0~3.3V

请按上述步骤进行排查，记录测试结果并联系售后服务团队以获得进一步帮助。



## 媒体资源

- img: https://wiki.bambulab.com/ams_buffer_signal_lost/%E6%A3%80%E6%9F%A56pin%E7%BA%BFpin%E8%84%9A.png
- img: https://wiki.bambulab.com/x1/manual/connect-ams/check_buffer_spring.png
- img: https://wiki.bambulab.com/ams_is_not_detected/bus_inside_ams.png
- img: https://wiki.bambulab.com/ams_buffer_signal_lost/buffer.png
- img: https://wiki.bambulab.com/ams_buffer_signal_lost/ams_buffer.drawio.svg
- img: https://wiki.bambulab.com/ams_buffer_signal_lost/%E6%B5%8B%E7%BC%93%E5%86%B2%E5%8C%BA%E7%94%B5%E5%8E%8B.png

