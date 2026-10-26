---
source: https://wiki.bambulab.com/zh/x1/troubleshooting/filament-not-extruding
fetched_at: 2026-10-26
title: 耗材挤出失败时的故障排除步骤
media_count: 4
---

> 来源：https://wiki.bambulab.com/zh/x1/troubleshooting/filament-not-extruding｜抓取日期：2026-10-26｜仅供本地检索演示，版权归原作者

耗材挤出失败时的故障排除步骤
本指南介绍耗材停止挤出时，建议采用的故障排除流程。

---

大多数情况下，问题出在工具头周围。但在极少数情况下，AMS、耗材路径或 PTFE 管等外部因素也可能导致此问题。

### 何时使用本指南？

本指南适用于挤出机出现咔哒声或无法挤出耗材。

对于 X1 和 P1 系列打印机，导致此问题的常见因素包括：

- 喷嘴堵塞，需要疏通
- 喷嘴温度过低
- 挤出机堵塞
- 挤出机上的进料霍尔板损坏/堵塞
- 挤出电机故障
- 挤出主板故障/挤出主板的 USB-C 数据线接触不良

### 工具和材料

- H2.0 六角扳手

### 安全警告

> **重要提醒！** **在进行任何维护工作之前，务必关闭打印机的电源**，包括对打印机的电子元件和工具头电线进行维护。在打印机通电时进行此类操作可能会导致短路，从而损坏电子设备和造成安全隐患。 在维护或故障排除过程中，您可能需要拆卸热端等部件，从而暴露电线和电子元件。如果它们在打印机仍处于通电状态时相互接触或与其他金属、电子元件接触，就可能发生短路。**这将损坏打印机的电子元件和造成其他问题。** 因此，**在进行任何维护前，务必关闭打印机并断开电源**，以防止短路或损坏打印机的电子原件，从而确保维护工作安全有效地进行。 如果您对本指南有任何疑问，请[点击这里提交工单](https://bambulab.com/zh/my/support/tickets?from=5)，我们将及时回复并提供帮助。

## 潜在堵塞位置

下图显示了几个潜在堵塞位置。

![](https://wiki.bambulab.com/x1/troubleshooting/filament-not-extruding/potential_clog_locations_for_x1c.jpeg)

### 1. 进料霍尔板

进料霍尔板内部可能存在耗材灰尘/碎屑，从而将磁铁 "锁 "在原位，导致无法将耗材送入挤出机。

要解决此问题，请先按照[此指南](https://wiki.bambulab.com/zh/x1/troubleshooting/hmscode/0700_2000_0002_0004)清洁进料霍尔板，然后再进行其他步骤。

### 2. 挤出齿轮

挤出机内部可能存在耗材碎片，导致挤出齿轮被卡住。对于没有[定期维护](https://wiki.bambulab.com/zh/x1/maintenance/basic-maintenance)的打印机，这种情况比较常见。

另一种可能性是挤出机内的耗材因热蠕变而变软，从而堵塞挤出机。[此指南](https://wiki.bambulab.com/zh/x1/troubleshooting/extruder-clog)详细解释了此问题，建议您阅读以获得进一步了解。

解决挤出齿轮相关问题的最佳方法是拆下挤出机，彻底清洁，并按照[挤出机维护指南](https://wiki.bambulab.com/zh/P1/maintenance/extruder-cleaning-guide)为挤出齿轮涂抹润滑油。

从打印机上拆下挤出机后，您应该可以轻松地旋转黄色齿轮，没有其他阻力。

### 3. 切刀

如果长时间未更换切刀，切刀可能无法干净利落地切断耗材。当这种情况出现时，耗材可能会在回抽过程中被卡住。

缺乏定期维护也会导致碎屑和灰尘进入切刀的通道，使切刀难以移动。如果切刀卡在不太理想的位置，可能会堵塞耗材通道，导致挤出机丢步。

最简单的解决方法是在对[挤出机进行维护](https://wiki.bambulab.com/zh/P1/maintenance/extruder-cleaning-guide)，同时[更换切刀](https://wiki.bambulab.com/zh/x1/maintenance/replace-cutter)。

### 4. 热蠕变导致耗材卡在冷端

如果在封闭式打印机（X1 系列和 P1S）中打印玻璃化转变温度较低的耗材（PLA、PETG、TPU），腔温会升高，导致耗材卡在热端的冷端。

在这种情况下，我们建议[按照 wiki 文章疏通热端](https://wiki.bambulab.com/zh/x1/troubleshooting/nozzle-clog)。在特殊情况下，您可能无法疏通热端，此时您需要安装新的热端。

我们还建议您阅读[这篇 wiki 文章](https://wiki.bambulab.com/zh/filament-acc/filament/heat-creep)，了解更多有关热蠕变的信息，以及如何避免热蠕变。

### 5. 喷嘴堵塞

在打印含有各种类型颗粒的耗材时，这个问题很常见。CF 耗材会导致细小的碳纤维颗粒附着在喷嘴上，在某些情况下可能会引起堵塞。

出现这种问题时，挤出机可能会发出咔嗒声，耗材也会停止挤出。

在这种情况下，我们建议[按照 wiki 文章疏通热端](https://wiki.bambulab.com/zh/x1/troubleshooting/nozzle-clog)。在特殊情况下，您可能无法疏通热端，此时您需要安装新的热端。

此外，我们建议打印含有不同颗粒的耗材时使用 0.6 毫米的喷嘴，以避免堵塞。

## 电机相关问题

挤出电机发生故障的几率很低。出现故障时，电机没有足够的动力转动挤出齿轮，导致丢步。

测试挤出电机的最佳方式如下：

### 1. 从工具头拆下挤出机

首先是从工具头上拆下挤出机。

### 2. 用打印机屏幕上的挤出按钮转动挤出齿轮

轻按几下上料按钮即可转动挤出齿轮。

![](https://wiki.bambulab.com/x1/%E6%8C%A4%E5%87%BA.png)

### 3. 尝试停止挤出电机

此步骤的目的是在挤出齿轮**旋转时抓住它并使其停止**。

> 电机齿轮边缘较为锋利，操作时请佩戴防割手套防护。

![](https://wiki.bambulab.com/x1/troubleshooting/filament-not-extruding/grab_the_extruder_motor_gear.jpeg)

如果挤出电机正常工作，您应该无法轻易使其停止旋转。

但是，如果挤出电机在旋转时可以轻易被停止，代表[挤出电机可能有故障，需要更换](https://wiki.bambulab.com/zh/x1/maintenance/replace-the-extrude-motor)。

在更换挤出机前，建议仔细检查挤出主板上的挤出电机电缆的连接情况，并重新连接。

此外，我们还建议重新连接挤出主板上的 USB 数据线（[此指南中的步骤 4](https://wiki.bambulab.com/zh/x1/maintenance/toolhead_boards_v9)）。

![](https://wiki.bambulab.com/x1/maintenance/th-boards-v9/disconnect_the_usb_cable.jpg)

如果问题仍然存在，则此问题可能与挤出电机、工具头板/USB-C 数据线有关。请联系我们的客户支持团队为您提供帮助。

请务必提供打印机的日志文件，以及您所做测试的相关信息。

## 操作后的校准步骤

建议您在更换挤出机后进行一次热床调平，以确保打印机顺畅运行。

此外，强烈建议在进行打印之前[清洗纹理PEI打印板](https://wiki.bambulab.com/zh/general/textured-PEI-plate-not-working-as-expected)，因为在更换挤出机的过程中，构建板可能会受到污染。



## 媒体资源

- img: https://wiki.bambulab.com/x1/troubleshooting/filament-not-extruding/potential_clog_locations_for_x1c.jpeg
- img: https://wiki.bambulab.com/x1/%E6%8C%A4%E5%87%BA.png
- img: https://wiki.bambulab.com/x1/troubleshooting/filament-not-extruding/grab_the_extruder_motor_gear.jpeg
- img: https://wiki.bambulab.com/x1/maintenance/th-boards-v9/disconnect_the_usb_cable.jpg

