---
source: https://wiki.bambulab.com/zh/x1/troubleshooting/AMS_is_not_detected_by_the_printer
fetched_at: 2026-10-26
title: 打印机无法检测到AMS
media_count: 19
---

> 来源：https://wiki.bambulab.com/zh/x1/troubleshooting/AMS_is_not_detected_by_the_printer｜抓取日期：2026-10-26｜仅供本地检索演示，版权归原作者

打印机无法检测到AMS

---


## 问题现象

当我们给 X1 系列打印机连接上 AMS 后，AMS 的四个插槽 LED 灯都是红灯闪烁（如果 AMS 固件版本太老的话可能还是显示白灯）。将料线插入 AMS 后，AMS 会进行预上料（向内吸入然后拉回），但在打印机无法检测到 AMS，屏幕上没有显示 AMS 标签。

![](https://wiki.bambulab.com/ams_is_not_detected/ams_tab.png)

## 操作指导

**首先请先将打印机关机，** 然后按照以下步骤缩小故障范围。

### 1. Pin 脚检查

首先可以尝试重新插拔 4&6Pin线缆，检查 Bambu Bus 4Pin & 6Pin 电缆（连接打印机—缓冲器— AMS 的两条线缆）的 Pin 脚是否存在变形或开路，如下图。

![](https://wiki.bambulab.com/ams_power_on_failure/pin_open.png)

### 2. 检查线缆连接

- 检查 AMS 内部的总线线缆（Bus）是否松动或者脱落，尝试重新插拔 BUS 线缆两端并再次上电看是否可以恢复正常。
- 检查 AMS 主板针脚是否有存在进水腐蚀的情况。

![](https://wiki.bambulab.com/ams_is_not_detected/bus_inside_ams.png)

- 同时建议稍微摇晃或弯曲 4Pin 和 6Pin 的插头和电缆，或者稍微拔出插头（不要完全拔出），看看 AMS 是否能在短时间内被打印机检测到，这样我们就可以把故障范围缩小到插头/电缆。

### 3. 电阻测量

如果你有万用表，确保 4Pin 和 6Pin 电缆正常地连接在机器上，然后用万用表测量 AMS、打印机以及 4Pin 和 6Pin 线电阻 **（打印机处于关机状态）。**

![](https://wiki.bambulab.com/ams_power_on_failure/ams_cable_pin_define.drawio.svg)

**X1C、P1P 和 P1S 正常的电阻值如下（只连接一台 AMS）**：

|  |  |  |  |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| pin-pin | AMS | 打印机接口 | 4pin线连接缓冲器 | 4pin线连接打印机 | 6pin线连接缓冲器 | 6pin线连接AMS | 4pin线连接AMS Hub | 6pin线连接AMS Hub |
| GND-sigA | 4~5kΩ | 4~5kΩ | 4~5kΩ | 4~5kΩ | 4~5kΩ | 4~5kΩ | 2~2.5kΩ | 2~2.5kΩ |
| GND-sigB | 4~5kΩ | 4~5kΩ | 4~5kΩ | 4~5kΩ | 4~6kΩ | 4~6kΩ | 2~2.5kΩ | 2~2.5kΩ |
| sigA-sigB | 8~10kΩ | 8~10kΩ | 8~10kΩ | 8~10kΩ | 8~10kΩ | 8~10kΩ | 4~5kΩ | 4~5kΩ |

**X1E 正常的电阻值如下（只连接一台 AMS）：**

|  |  |  |  |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| pin-pin | AMS接口 | 打印机接口 | 4pin线连接缓冲器 | 4pin线连打印机 | 6pin线连接缓冲器 | 6pin线连接AMS | 4pin线连接AMS Hub | 6pin线连接AMS Hub |
| GND-sigA | 4~5kΩ | 2~2.5kΩ | 4~5kΩ | 2~2.5kΩ | 2~2.5kΩ | 4~5kΩ | 2~2.5kΩ | 2~2.5kΩ |
| GNS-sigB | 4~5kΩ | 2~2.5kΩ | 4~5kΩ | 2~2.5kΩ | 2~2.5kΩ | 4~5kΩ | 2~2.5kΩ | 2~2.5kΩ |
| sigA-sigB | 8~10kΩ | 4~5kΩ | 8~10kΩ | 4~5kΩ | 4~5kΩ | 8~10kΩ | 4~5kΩ | 4~5kΩ |

#### 测量打印机 4Pin 接口和 4Pin 线两端的电阻

1. 4Pin 接口：

从打印机上断开 4Pin 线缆，测量打印机 4Pin 接口和 4Pin 线端子的电阻。

|  |  |
| --- | --- |
|  |  |

**打印机 4Pin 接口正常的测量结果如下：**

|  |  |  |
| --- | --- | --- |
| Pin-Pin | X1C/P1P/P1S | X1E |
| GND-sigA | 4~5kΩ | 2~2.5kΩ |
| GND-sigB | 4~5kΩ | 2~2.5kΩ |
| sigA-sigB | 8~10kΩ | 4~5kΩ |

2.  4Pin 线连接缓冲器：

测量打印机 4Pin 线连接缓冲器时另一端的电阻。

|  |  |
| --- | --- |
|  |  |

**4pin 线连接缓冲器正常的测量结果如下：**

|  |  |  |
| --- | --- | --- |
| Pin-Pin | X1C/P1P/P1S | X1E |
| GND-sigA | 4~5kΩ | 4~5kΩ |
| GND-sigB | 4~5kΩ | 4~5kΩ |
| sigA-sigB | 8~10kΩ | 8~10kΩ |

3. 4pin 线连接打印机：

把 4Pin 线接回打印机，从缓冲器上拔掉 4Pin 线，继续测量另一端 4Pin 针脚之间的电阻 **（把缓冲器从打印机上取下可以更容易拔出线缆）**。

![](https://wiki.bambulab.com/ams_is_not_detected/%E7%BC%93%E5%86%B2%E5%99%A8%E7%AB%AF4pin%E7%BA%BF%E7%AB%AF%E5%AD%90.png)

**4pin 线连接打印机正常的测量结果如下：**

|  |  |  |
| --- | --- | --- |
| Pin-Pin | X1C/P1P/P1S | X1E |
| GND-sigA | 4~5kΩ | 2~2.5kΩ |
| GND-sigB | 4~5kΩ | 2~2.5kΩ |
| sigA-sigB | 8~10kΩ | 4~5kΩ |

#### 测量 AMS 6Pin 接口和 6Pin 线两端的电阻

1. 6Pin 接口：

把 4Pin 线缆接回缓冲器，从 AMS 上拔掉 6Pin 线缆，测量 AMS 6Pin 接口的电阻（两个接口都一样）和 6Pin 线缆的电阻。

|  |  |
| --- | --- |
|  |  |

**AMS 6pin 接口正常的测量结果如下：**

|  |  |  |
| --- | --- | --- |
| Pin-Pin | X1C/P1P/P1S | X1E |
| GND-sigA | 4~5kΩ | 4~5kΩ |
| GND-sigB | 4~6kΩ | 4~5kΩ |
| sigA-sigB | 8~10kΩ | 8~10kΩ |

2. 6Pin 线连接缓冲器：

测量打印机 6Pin 线连接缓冲器时另一端的电阻。

|  |  |
| --- | --- |
|  |  |

**6pin 线连接缓冲器正常的测量结果如下：**

|  |  |  |
| --- | --- | --- |
| Pin-Pin | X1C/P1P/P1S | X1E |
| GND-sigA | 4~5kΩ | 2~2.5kΩ |
| GND-sigB | 4~6kΩ | 2~2.5kΩ |
| sigA-sigB | 8~10kΩ | 4~5kΩ |

3. 6pin 线连 AMS：

把 6Pin 线缆从缓冲器上拔出，测量 6Pin 线缆另一端的电阻**（把缓冲器从打印机上取下可以更容易拔出线缆）**。

![](https://wiki.bambulab.com/ams_is_not_detected/%E7%BC%93%E5%86%B2%E5%99%A8%E7%AB%AF6pin%E7%BA%BF%E7%AB%AF%E5%AD%90.png)

**6pin 线连 AMS 正常的测量结果如下：**

|  |  |  |
| --- | --- | --- |
| Pin-Pin | X1C/P1P/P1S | X1E |
| GND-sigA | 4~5kΩ | 4~5kΩ |
| GND-sigB | 4~6kΩ | 4~5kΩ |
| sigA-sigB | 8~10kΩ | 8~10kΩ |

#### 测量 AMS 主板和 MC 板的电阻

若在以上的步骤中测出异常的电阻值，则可以判断 AMS/打印机/4&6pin 线/缓冲器中是哪里出的故障导致 AMS 无法识别。

**AMS主板电阻的测量**

根据以上的测量结果，如果 AMS 的 6pin 接口的电阻异常，可以拆开 AMS（可以参考[这篇wiki](https://wiki.bambulab.com/zh/x1/maintenance/replace-ams-main-board)），进一步测量连接主板的总线(Bus)和电源(power)线缆接口的电阻，看是否是 AMS 主板故障：

![](https://wiki.bambulab.com/ams_is_not_detected/%E6%B5%8Bams%E4%B8%BB%E6%9D%BF%E7%94%B5%E9%98%BB.jpg)

**总线 (Bus) 和电源线 (Power) 正常的测量结果如下：**

|  |  |  |
| --- | --- | --- |
| Pin-Pin | X1C/P1P/P1S | X1E |
| GND-sigA | 4~5kΩ | 4~5kΩ |
| GND-sigB | 4~6kΩ | 4~5kΩ |
| sigA-sigB | 8~10kΩ | 8~10kΩ |

- 如果测量连接主板的总线(Bus)和电源(power)线缆接口的电阻正常，则可能是 AMS 电源板异常，需要更换电源板；
- 如果测量连接主板的总线(Bus)和电源(power)线缆接口的电阻异常，则可能是 AMS 主板异常。

**MC 板电阻测量**

如果测量的打印机 4pin 接口的电阻异常，则有可能是 AMS 接口板或者是 MC 板的故障。可以拆开打印机后盖，拔掉 AMS 接口板上的 6pin 线（可以参考[这篇wiki](https://wiki.bambulab.com/zh/x1/maintenance/replace-ams-interface-board)），测量连接 MC 板的6pin 线电阻看是否是 MC 板故障：

![](https://wiki.bambulab.com/ams_is_not_detected/%E6%B5%8B%E9%87%8Fmc6pin%E7%BA%BF.jpeg)

**连接 MC 板的 6pin 线正常的测量结果如下：**

|  |  |  |
| --- | --- | --- |
| Pin-Pin | X1C/P1P/P1S | X1E |
| GND-sigA | 4~5kΩ | 4~5kΩ |
| GND-sigB | 4~5kΩ | 4~5kΩ |
| sigA-sigB | 8~10kΩ | 8~10kΩ |

- 如果测量连接 MC 板的 6pin 线电阻正常，则可能是 AMS 接口板异常，需要更换 AMS 接口板；
- 如果测量连接 MC 板的 6pin 线电阻异常，则可能是 MC 板异常，需要更换 MC 板；

对于 X1E，如果以上测量的电阻均正常，请参考下图移除风道（左图），然后测量加热模块控制板上网线及 AMS 接口板接口的电阻（右图）：

|  |  |
| --- | --- |
|  |  |

加热模块控制板上网线及 AMS 接口板接口正常的测量结果如下：

|  |  |
| --- | --- |
| Pin-Pin | X1E |
| GND-sigA | 4~5kΩ |
| GND-sigB | 4~5kΩ |
| sigA-sigB | 8~10kΩ |

如果测得的电阻异常，则需要更换加热模块控制板。

#### 备注

以上一共有 8 组电阻值数据，如下图所示。测得哪个部分的电阻值是异常的，说明这个部件是有故障的。请按照下图记录这几组测量的电阻值数据，并联系售后团队获取进一步的帮助。

![](https://wiki.bambulab.com/ams_is_not_detected/8%E7%BB%84%E7%94%B5%E9%98%BB%E5%80%BC%E6%95%B0%E6%8D%AE.png)

**记录测量电阻的表格可以参考如下：**

|  |  |  |  |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| pin-pin | AMS | 打印机接口 | 4pin线连接缓冲器/AMS hub | 4pin线连接打印机 | 6pin线连接缓冲器//AMS hub | 6pin线连接AMS | MC板 | AMS主板 |
| GND-sigA |  |  |  |  |  |  |  |  |
| GND-sigB |  |  |  |  |  |  |  |  |
| sigA-sigB |  |  |  |  |  |  |  |  |

## 媒体资源

- img: https://wiki.bambulab.com/ams_is_not_detected/ams_tab.png
- img: https://wiki.bambulab.com/ams_power_on_failure/pin_open.png
- img: https://wiki.bambulab.com/ams_is_not_detected/bus_inside_ams.png
- img: https://wiki.bambulab.com/ams_power_on_failure/ams_cable_pin_define.drawio.svg
- img: https://wiki.bambulab.com/ams_is_not_detected/%E6%B5%8B%E6%89%93%E5%8D%B0%E6%9C%BA4pin%E7%AB%AF%E5%8F%A3%E7%94%B5%E9%98%BB.png
- img: https://wiki.bambulab.com/ams_is_not_detected/4pin_%E6%8E%A5%E5%8F%A3-.webp
- img: https://wiki.bambulab.com/ams_is_not_detected/4pin%E7%BA%BF%E7%AB%AF%E5%AD%90.png
- img: https://wiki.bambulab.com/ams_is_not_detected/4pin_%E8%BF%9E%E6%8E%A5%E7%BC%93%E5%86%B2%E5%99%A8.webp
- img: https://wiki.bambulab.com/ams_is_not_detected/%E7%BC%93%E5%86%B2%E5%99%A8%E7%AB%AF4pin%E7%BA%BF%E7%AB%AF%E5%AD%90.png
- img: https://wiki.bambulab.com/ams_is_not_detected/%E6%B5%8Bams6pin%E6%8E%A5%E5%8F%A3%E7%94%B5%E9%98%BB.png
- img: https://wiki.bambulab.com/ams_is_not_detected/6pin_%E5%8F%A3.webp
- img: https://wiki.bambulab.com/ams_is_not_detected/6pin%E7%BA%BF%E7%AB%AF%E5%AD%90.png
- img: https://wiki.bambulab.com/ams_is_not_detected/6pin_%E8%BF%9E%E6%8E%A5%E7%BC%93%E5%86%B2%E5%99%A8.webp
- img: https://wiki.bambulab.com/ams_is_not_detected/%E7%BC%93%E5%86%B2%E5%99%A8%E7%AB%AF6pin%E7%BA%BF%E7%AB%AF%E5%AD%90.png
- img: https://wiki.bambulab.com/ams_is_not_detected/%E6%B5%8Bams%E4%B8%BB%E6%9D%BF%E7%94%B5%E9%98%BB.jpg
- img: https://wiki.bambulab.com/ams_is_not_detected/%E6%B5%8B%E9%87%8Fmc6pin%E7%BA%BF.jpeg
- img: https://wiki.bambulab.com/ams_is_not_detected/%E7%A7%BB%E9%99%A4%E9%A3%8E%E9%81%93.jpg
- img: https://wiki.bambulab.com/ams_is_not_detected/%E5%8A%A0%E7%83%AD%E6%A8%A1%E5%9D%97%E7%94%B5%E9%98%BB%E6%B5%8B%E9%87%8F.png
- img: https://wiki.bambulab.com/ams_is_not_detected/8%E7%BB%84%E7%94%B5%E9%98%BB%E5%80%BC%E6%95%B0%E6%8D%AE.png

