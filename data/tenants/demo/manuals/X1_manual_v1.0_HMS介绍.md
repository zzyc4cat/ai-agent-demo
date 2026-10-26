---
source: https://wiki.bambulab.com/zh/x1/troubleshooting/intro-hms
fetched_at: 2026-10-26
title: HMS介绍
media_count: 4
---

> 来源：https://wiki.bambulab.com/zh/x1/troubleshooting/intro-hms｜抓取日期：2026-10-26｜仅供本地检索演示，版权归原作者

HMS介绍

---


## 什么是 HMS

健康管理系统 (Health Management System) 负责收集和监控整个系统状态，包括:

1. 硬件连接和工作状态，例如：热端风扇转速过低；
2. 机械状态，例如皮带张紧度;
3. 打印过程中的问题，例如首层检测失败或炒面缺陷。

一旦发生异常事件， HMS会通知用户问题所在。然后，用户可以采取适当的操作。

## HMS 编码系统

![](https://wiki.bambulab.com/hms_code_definition-%E4%B8%AD%E6%96%87.jpg)

**1. 部件编号**

|  |  |  |
| --- | --- | --- |
| 部件编号 | 部件名称缩写 | 部件名称 |
| 03 | MC | Motion Controller（运动控制） |
| 05 | AP | Main Board（主板） |
| 07 | AMS | Automated Material System（自动进料系统） |
| 08 | TH | Tool Head（工具头） |
| 0C | XCAM | Bambu Micro Lidar（激光雷达） |
| 10 | Studio | Bambu Studio |
| 11 | APP | Bambu Handy |
| 12 | AMS Lite | Automated Material System Lite（自动进料系统） |
| 18 | AMS HT | Automated Material System Heater（自动进料系统-烘干 ） |

**2. 部件序号**

打印机中或打印机连接设备中特定模块的序号。序号通常为0，当同一模块的数量大于1时，序号可不为0。例如，当一台打印机连接两台AMS设备时，AMS设备的序号可为0，1。

**3. 零件编号**

部件下属零件的编号。例如，MC模块下，零件编号01代表热床加热器，02代表挤出头加热器。

**4. 零件序号**

零件的序号，默认为0，当该部件下相同零件数大于1时，序号可不为0。

**5. 告警等级**

| 等级 | 类型 | 弹窗颜色 | 打印状态影响 | 安全风险 | 举例 |
| --- | --- | --- | --- | --- | --- |
| 0000 | 无效告警 | / | / | / | / |
| 0001 | 错误 | 红色 | 打印停止，告警消除后才能开启打印 | 高 | 热端温度过高导致打印机损坏 |
| 0002 | 警告 | 黄色 | 打印暂停，告警消除后才能继续打印 | 中低 | 异物检测未生效，需要校准摄像头 |
| 0003 | 提醒 | 蓝色 | 无影响，仅提示用户注意 | 无 | 开门检测，关门后提示消失 |

**6. 错误码编号**

按部件、零件划分后，HMS算法的序号。

## HMS是如何工作的

HMS是一个分布式系统，包含许多状态检测器和一个中央管理单元。下图是一个简单的示意图来展示它是如何工作的。

![](https://wiki.bambulab.com/x1/troubleshooting/intro-hms/300px-hms_diagram.jpg)

HMS 示意图

### 错误代码

对于每个异常状态，HMS都会为其发送一个唯一的错误代码。例如：03000100010001表示加热床温度异常，可能是由于短路引起。然后可以使用这个错误代码在Bambu Lab Wiki中搜索解决方案。

### 通知

如果HMS检测到系统中有错误，它将在屏幕上弹出一个错误消息和错误代码。根据严重性的级别，每个消息的通知方法是不同的。对于严重错误，它将在机器的显示器上弹出一个消息窗口并请求用户确认。对于警告状态，HMS将只在显示屏的右侧显示一条通知消息。HMS也将同时发送一条通知到移动端APP上。

### 局限性

HMS同样存在一些局限性，例如：

1. 由于缺乏一些评估方法，HMS不能涵盖所有的错误和警告。
2. 有些错误不能直接识别，例如丢步。
3. 一些错误的根本原因是非常复杂的，HMS无法识别它们的真正原因。例如，打印阻塞可能是由于打印设置或操作不当造成的。HMS可能只检测到发生了错误，但不知道真正的原因。

## 如何使用HMS

用户可以利用HMS的通知来了解整个系统的状态，包括一些机械和硬件错误，或者打印失败的原因。这有一个wiki页面给出了每个错误代码的详细描述和操作方法，可以在[这里](https://wiki.bambulab.com/zh/hms/home)找到。

在屏幕报告错误时，HMS还会给出一个二维码，这个二维码会指向wiki页面。因此，当看到HMS消息时，用户应该仔细阅读相关的wiki页面，并按照诊断步骤确定真正的问题是什么。可以使用Bambu handy扫码，也可以使用其他支持扫码功能的APP。

![screencn.png](https://wiki.bambulab.com/x1/troubleshooting/intro-hms/screencn.png)

扫码后会跳转到一个网页，进入到对应的错误代码链接。在弹出的页面就可以看到有关错误代码的详细信息，还有针对此错误的故障排查指南。 您可以尝试按照其中的步骤解决问题。

![webcn.png](https://wiki.bambulab.com/x1/troubleshooting/intro-hms/webcn.png)

如果问题最终没有解决，请联系 Bambu 售后服务团队。



## 媒体资源

- img: https://wiki.bambulab.com/hms_code_definition-%E4%B8%AD%E6%96%87.jpg
- img: https://wiki.bambulab.com/x1/troubleshooting/intro-hms/300px-hms_diagram.jpg
- img: https://wiki.bambulab.com/x1/troubleshooting/intro-hms/screencn.png
- img: https://wiki.bambulab.com/x1/troubleshooting/intro-hms/webcn.png

