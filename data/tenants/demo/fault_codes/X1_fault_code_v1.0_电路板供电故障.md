---
source: https://wiki.bambulab.com/zh/x1/troubleshooting/circuit-board-power-failure
fetched_at: 2026-10-26
title: 打印机电路故障排查 - X1 系列
media_count: 21
---

> 来源：https://wiki.bambulab.com/zh/x1/troubleshooting/circuit-board-power-failure｜抓取日期：2026-10-26｜仅供本地检索演示，版权归原作者

打印机电路故障排查 - X1 系列
本指南介绍 X1 系列打印机电路故障的表现、原因及排障操作。

---


## 何时需要使用该指南

在连接电源线并打开电源后，虽然电源指示灯亮起，但打印机的显示屏没有被点亮。与此同时，一个或多个电路板指示灯发生故障。

> 本指南中的部分视频在手机端的浏览器上可能无法正常加载，建议您改用电脑端浏览器观看。

|  |  |
| --- | --- |
|  |  |

### 正常状态：TH 板指示灯常亮红灯

### 正常状态：MC 板每 5 秒闪烁一次红灯

### 正常状态：AP 板有 2个指示灯,一个常亮红灯,一个 1 秒闪烁一次红灯

### 打印机电路故障和显示屏黑屏、闪屏的区别

如果显示屏不亮，但 MC 和 TH 指示灯正常，则故障仅属于显示屏， AP 模块或 MC-AP 线缆，而不是整机的整体电路问题。在这种情况下，您可以跳转到下方的链接进行故障排查。

- [显示屏黑屏、闪屏故障排查](https://wiki.bambulab.com/zh/x1/troubleshooting/black-flicker-screen)

## 所需工具

- H1.5 内六角扳手
- H2.0 内六角扳手
- 镊子

## 安全提示

> **重要提醒 ！** 在对打印机及其电子设备（包括工具头线缆）进行任何维护工作之前，**请关闭打印机电源并断开电源连接**，以避免发生电路短路从而引起额外的电子设备损坏和安全隐患。 在您对打印机进行维护或故障排查时，请先确认热端和热床的温度，避免在高温状态下操作，如果必须在高温状态下操作，请佩戴好隔热手套，以确保安全有效地执行维护工作。 如果您对本指南有任何疑问，请[点击提交服务工单](https://bambulab.cn/zh/sign-in?to=%2Fmy%2Fsupport%2Ftickets)，我们将及时回复并为您提供所需的帮助。

## 可能的故障原因

### 1. Micro SD 卡故障

Micro SD 卡短路导致 AP 故障指示灯不亮，屏幕黑屏。

### 2. 铁壳 24V 电源模块输出异常：

前面提到的电路板的输入电压为 24V，由铁壳电源模块提供。如果铁壳 24V 电源模块输出异常，将导致后续电路板的的输入电压异常，从而导致所有的指示灯无法点亮。

![](https://wiki.bambulab.com/x1/troubleshooting/circuit-board-power-failure/power-unit-on.png)

- [更换电源模块](https://wiki.bambulab.com/zh/x1/maintenance/replace-power-module)

### 3. 如果铁壳 24V 电源模块工作正常，但由于诸如 TH 板、MC 板、AP 板等某个电路板，或电路板上的风扇、加热器、电机等部件发生 24V 短路，也会导致打印机整机电路中出现 24V 短路。

打印机内部的电路板 24V 电源是串联连接的。如果主电路或分支电路中有任何一个发生短路，可能会导致整个 24V 系统发生短路。

![x1_电路关系.png](https://wiki.bambulab.com/x1_%E7%94%B5%E8%B7%AF%E5%85%B3%E7%B3%BB.png)

## 排查建议：

排查建议背后的原理是，如果在断开某个特定连接器后，剩余电路的指示灯恢复正常，则表明连接到该接口的那个模块就是导致异常的原因。在这种情况下，需要进一步排查或更换该故障模块。

> **请注意，在每次插拔动作之前，您必须先关闭打印机电源。在插拔完成后，再开启打印机电源并观察电路状态。**

![](https://wiki.bambulab.com/x1/troubleshooting/circuit-board-power-failure/x1-%E7%94%B5%E8%B7%AF%E5%BC%82%E5%B8%B8%E6%8E%92%E6%9F%A5-v.jpg)

### 1. 排查 Micro SD 卡问题。

启动打印机后，若显示屏黑屏无显示，首先可排查 Micro SD 卡问题。

> **注意事项：在进行以下操作前，请务必先关闭打印机电源**

1. 关闭打印机电源，并小心地从打印机中拔出 Micro SD 卡。

2. 重启打印机，观察显示屏是否能正常亮起。若显示屏在拔出 MicroSD 卡后能正常显示，那么请在关机状态下将 MicroSD 卡重新插入打印机，并再次开机以验证是否因 MicroSD 卡故障导致之前的黑屏问题。

![](https://wiki.bambulab.com/x1/troubleshooting/circuit-board-power-failure/x1-sd.jpg)

### 2. 排查铁壳 24V 电源模块

#### 步骤 1 - 关机，断开电源。拆下金属后盖板

请根据  [更换后面板 | Bambu Lab Wiki](https://wiki.bambulab.com/zh/x1/maintenance/replace-rear-panel)  拆除后盖板。

![](https://wiki.bambulab.com/x1/maintenance/mc_ap/rear_panel_removed.jpg)

#### 步骤 2 - 拆除废料槽(可选步骤)

建议拆除废料槽，这样可以创造更多的操作空间。

拧出位于废料槽两侧的螺丝。完成后，取出废料槽。**有些打印机有三颗螺丝固定废料槽，而有些只有两颗螺丝，请根据您的具体情况操作。**

另外，有些版本的打印机，热床电缆是固定在废料槽底部的，取下废料槽时请小心操作，不要扯断线缆。

**2 颗螺丝的情况:**

|  |  |
| --- | --- |
|  |  |

**3 颗螺丝的情况:**

|  |  |  |
| --- | --- | --- |
|  |  |  |

#### 步骤 3 - 连接电源，打开电源开关，观察铁壳 24V 电源模块的绿色指示灯是否是常亮状态（不亮或常闪均为异常）。

[更换电源模块](https://wiki.bambulab.com/zh/x1/maintenance/replace-power-module)

![](https://wiki.bambulab.com/x1/troubleshooting/circuit-board-power-failure/power-unit-on.png)

如果绿色指示灯是常亮的，这意味着铁壳 24V 电源模块正常工作，您可以跳过步骤 4，直接从第二部分的步骤 5 开始开始检查第二部分。

#### 步骤 4 - 如果绿色指示灯不亮或者是闪烁的，请再次关闭打印机。然后小心地使用镊子拔掉 MC 板上的 24V 输入连接器。重新启动打印机，再次检查铁壳 24V 电源模块指示灯的状态。

在拔 MC 板上的 24V 输入连接器后，也就意味着断开了其他电路对铁壳 24V 电源模块的影响，如果此时，铁壳电源指示灯仍然不亮或者闪烁，这表明铁壳电源模块本身存在故障，需要更换。

相反，如果在拔掉连接器并打开电源开关后，铁壳电源模块的指示灯会变成常亮，这表明铁壳电源模块本身没有故障。请跟着后面的步骤继续排查故障的原因。

|  |  |
| --- | --- |
|  |  |

### 3. 排查铁壳电源之外的异常电子元件（如 TH 板、MC 板、AP 板等某个电路板，或电路板上的风扇、加热器、电机等部件），通过依次插拔，排除试错的方法找出故障部件

如果铁壳电源模块确认工作正常，问题必定是其中一块电路板(大概率是 TH / MC / AP 板)，或者这些电路板上的某个部件(小概率是风扇、加热器、电机)存在 24V 短路，导致整个系统短路，因此我们需要继续排查。

#### 步骤 5 - 在关闭打印机电源后，重新接回步骤 4 提到的 MC 板上 24V 电源连接器。然后断开 MC 板上的 AP-MC 电缆(通信和供电,#9和#10),如图所示。再开机检查 MC 指示灯的状态。

- [更换MC板](https://wiki.bambulab.com/zh/x1/maintenance/replace-mc-board)

![](https://wiki.bambulab.com/x1/maintenance/replace-mc-board/marks_on_connectors_2.png)

| 序号 | 连接对象 | 序号 | 连接对象 | 序号 | 连接对象 |
| --- | --- | --- | --- | --- | --- |
| 1 | Z 轴电机 | 5 | 辅助部件冷却风扇 | 9 | AP 主板 (供电) |
| 2 | 右边的电机 (从后盖往前看) | 6 | MC板冷却风扇 | 10 | AP 主板 (通信) |
| 3 | 左边的电机 (从后盖往前看) | 7 | MC -AC 板连接线 | 11 | 热床（通信） |
| 4 | 机箱控温风扇 | 8 | AMS 接口板 |  |  |

断开 MC 和 AP 模块之间的电源和信号线可以隔离 AP 和 TH 模块对 MC 板的影响。这可以帮助我们确定 MC 模块本身是否正常工作。

如果在 MC 板这端断开 MC-AP 信号线和电源线后，MC 板上的指示灯仍然异常，则表示 MC 模块需要更换。

> 小提示
> 
> 假如我们已经将问题缩小到 MC 模块，根本原因可能是 MC 板本身或 MC 板上的部件，比如 24V 电机或风扇。但是从概率上说,问题出在 MC 板本身的可能性会更大。为了简化排查步骤，将在本文末尾包含对 MC 板及其组件问题的隔离方法（步骤8），而不在这一步中继续展开了。

如果在 MC 板这端断开 MC-AP 信号线和电源线后，MC 板上的指示灯恢复正常，则表示 MC 模块工作正常，问题可能出在下游电路，如 MC-AP 线缆，AP 板或 TH 板,或者 AP/TH 板上的部件，导致短路。那你需要从步骤 6 接着往下看。

#### 步骤 6 - 在关闭打印机电源后，重新插回 MC 板端的 MC-AP 线缆，然后拔下 AP 板上的 USB-C 口，判断 AP 模块是否异常。

![](https://wiki.bambulab.com/x1/maintenance/replace-ap-board/connectors_on_the_ap_board.jpg)

|  |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- |
| 序号 | 连接对象 | 序号 | 连接对象 | 序号 | 连接对象 |
| 1 | 机箱摄像头 | 4 | 按键板 | 7 | USB-C |
| 2 | 机箱LED | 5 | MC 板 (电源) |  |  |
| 3 | WIFI 天线 | 6 | MC 板(通信) |  |  |

- [更换AP主板](https://wiki.bambulab.com/zh/x1/maintenance/replace-ap-board)

假如通过步骤 5 的排查，我们已经排除 MC 模块故障的可能。那接下来我们需要进一步排查 AP 模块和 TH 模块故障的可能。

断开 USB-C(#7) 可以隔离 TH 对 AP 的影响，这可以帮助我们判断 AP 模块本身是否正常。

假如在 AP 板上拔掉 USB-C(#7) 后，AP 板上的指示灯仍然异常，则问题可能出在 AP 模块，即 AP 板，MC-AP 线缆，或者 AP 上的组件，导致短路，你需要根据步骤 6 继续排查。

假如在 AP 板上拔掉 USB-C(#7) 后，AP 板上的指示灯恢复正常，则表明 AP 模块工作正常，问题出在 TH 模块，即 TH板，USB-C 线缆，或者 TH 板上的组件，如热端加热片，散热风扇或电机，导致短路。那你需要根据步骤 7 继续排查。

如已经将问题定位到 AP 模块了，那需要先将 AP 板上的机箱摄像头，LED，wifi 天线和按键板 (#1、#2、#3、#4) 拔掉，观察 AP 板灯语是否恢复正常。

如果 AP 灯语仍然异常，那 AP 板或者 MC-AP 线缆需要被更换。

如果 AP 灯语恢复正常，则在断电的情况下，小心逐一插回 AP 板上的这些连接器 (#1、#2、#3、#4)，如果插回某一部件导致 AP 灯语异常，则该部件需要被更换。

#### 步骤 7 - 关闭打印机电源后，重新插回 AP 板端的 USB-C 线缆，然后依次拔下 TH板组件上的其他接口，以判断是 TH 板组件或者 USB-C 异常，还是 TH 板上的部件，如热端加热片，散热风扇或电机异常。

![](https://wiki.bambulab.com/x1/maintenance/replace-usb-cable/connect_to_ap_board.jpg)

- [更换工具头电路板（旧版）](https://wiki.bambulab.com/zh/x1/maintenance/replace-the-th-board-assembly)
- [更换工具头电路板（新版）](https://wiki.bambulab.com/zh/x1/maintenance/toolhead_boards_v9)

如果在拔掉 插头 #2、#3、#4、#5、#8、#9、和#10（需保留USB-C口， #1 和 #7 这 3 个插头） ，TH 板上的指示灯仍然异常，则表明 TH 板组件和 USB-C 线缆需要更换。

再次说明，当 USB-C 电缆的任一端断开时，TH 板上的指示灯一定不会点亮，因为 TH 模块需要通过 USB-C 连接供电。

![](https://wiki.bambulab.com/x1/troubleshooting/circuit-board-power-failure/th-logic.png)

如果在拔掉 插头 #2、#3、#4、#5、#8、#9、和#10（需保留 USB-C口， #1 和 #7 这 3 个插头），TH 板上的指示灯恢复正常，则表明 TH 组件和 USB-C 线缆工作正常。

这意味着问题可能出在 #2、#3、#4、#5、#8、#9、#10 号插头的部件中的一个或几个。在这种情况下，您需要在断电的情况下逐个将这些连接器 (#2、#3、#4、#5、#6、#8、#9、#10) 重新插回，以找出导致短路的具体部件。如果插回哪一个，TH 灯语出现异常，则该备件需要被更换。

#### 步骤 8 - 如前所述，如果问题已被定位在 MC 模块，更换 MC 板最有可能解决问题。但是，如果您想确保 100%，可以再继续逐一检查 MC 板上的 24V 部件，如电机，风扇，和 AMS 接口板的插头。

如果在拔掉 MC 板上的所有部件 (包括 #1、#2、#3、#4、#5、#6、#7、#8、#9、#10、#11)之后，MC 板上的指示灯仍然没有点亮，那么我们可以相当确定 MC 板本身存在故障。

![](https://wiki.bambulab.com/x1/maintenance/replace-mc-board/marks_on_connectors_2.png)

| 序号 | 连接对象 | 序号 | 连接对象 | 序号 | 连接对象 |
| --- | --- | --- | --- | --- | --- |
| 1 | Z 轴电机 | 5 | 辅助部件冷却风扇 | 9 | AP 主板 (供电) |
| 2 | 右边的电机 (从后盖往前看) | 6 | MC板冷却风扇 | 10 | AP 主板 (通信) |
| 3 | 左边的电机 (从后盖往前看) | 7 | MC -AC 板连接线 | 11 | 热床（通信） |
| 4 | 机箱控温风扇 | 8 | AMS 接口板 |  |  |

[更换MC板](https://wiki.bambulab.com/zh/x1/maintenance/replace-mc-board)

另一方面，如果在拔掉 MC 板上的所有部件 (包括 #1、#2、#3、#4、#5、#6、#7、#8、#9、#10、#11) 之后，MC 板上的指示灯恢复正常，这意味着可能是 MC 板上的某个部件导致了短路。

在这种情况下，你需要在断电的情况下，小心逐一插回 MC 板上的这些连接器(包括 #1、#2、#3、#4、#5、#6、#7、#8、#9、#10、#11)，以确定导致短路的具体组件。如果插回哪一个，MC 灯语出现异常，则该备件需要被更换。

在这一步中，您需要特别关注 MC 板上的电机、风扇（辅助风扇，腔温调节风扇和 MC 板风扇）和 AMS 接口板。这些设备由 24V 供电，更容易导致电路短路。



## 媒体资源

- video: https://public-cdn.bblmw.com/wiki/video/X1-TH.mp4
- video: https://public-cdn.bblmw.com/wiki/video/X1-MC.mp4
- video: https://public-cdn.bblmw.com/wiki/video/X1-AP.mp4
- img: https://wiki.bambulab.com/x1/maintenance/replace-fuse/395px-power_on.png
- img: https://wiki.bambulab.com/x1/troubleshooting/black-screen/black_screen.jpg
- img: https://wiki.bambulab.com/x1/troubleshooting/circuit-board-power-failure/power-unit-on.png
- img: https://wiki.bambulab.com/x1_%E7%94%B5%E8%B7%AF%E5%85%B3%E7%B3%BB.png
- img: https://wiki.bambulab.com/x1/troubleshooting/circuit-board-power-failure/x1-%E7%94%B5%E8%B7%AF%E5%BC%82%E5%B8%B8%E6%8E%92%E6%9F%A5-v.jpg
- img: https://wiki.bambulab.com/x1/troubleshooting/circuit-board-power-failure/x1-sd.jpg
- img: https://wiki.bambulab.com/x1/maintenance/mc_ap/rear_panel_removed.jpg
- img: https://wiki.bambulab.com/x1/maintenance/replace-mc-board-fan/350px-remove_the_excess_chute1.png
- img: https://wiki.bambulab.com/x1/maintenance/replace-mc-board-fan/350px-remove_the_excess_chute2.png
- img: https://wiki.bambulab.com/x1/maintenance/replace-mc-board/rear_panel_screws_1.jpg
- img: https://wiki.bambulab.com/x1/maintenance/replace-mc-board/excess_chute_screws_2.jpg
- img: https://wiki.bambulab.com/x1/maintenance/replace-mc-board/3_screws.png
- img: https://wiki.bambulab.com/x1/troubleshooting/circuit-board-power-failure/24v-conn1.png
- img: https://wiki.bambulab.com/x1/troubleshooting/circuit-board-power-failure/24v-conn2.png
- img: https://wiki.bambulab.com/x1/maintenance/replace-mc-board/marks_on_connectors_2.png
- img: https://wiki.bambulab.com/x1/maintenance/replace-ap-board/connectors_on_the_ap_board.jpg
- img: https://wiki.bambulab.com/x1/maintenance/replace-usb-cable/connect_to_ap_board.jpg
- img: https://wiki.bambulab.com/x1/troubleshooting/circuit-board-power-failure/th-logic.png

