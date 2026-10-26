---
source: https://wiki.bambulab.com/zh/x1/troubleshooting/enable-the-video-recording-function
fetched_at: 2026-10-26
title: 开启录像功能和导出录像视频
media_count: 15
---

> 来源：https://wiki.bambulab.com/zh/x1/troubleshooting/enable-the-video-recording-function｜抓取日期：2026-10-26｜仅供本地检索演示，版权归原作者

开启录像功能和导出录像视频
本文介绍了如何在不同系列打印机中开启录像功能和导出录像视频

---

开启录像功能可以记录打印机的状态。在打印过程中遇到异常或失败时，您可以通过查看 SD 卡中的视频进行分析；也可以将视频发送给我们，我们的售后团队会帮助您分析并寻找解决方案。

因此，为了帮助我们的售后团队更有效地解决您的问题，建议您启用录像功能。

## 开启录像功能

### X1 系列

1. 在屏幕侧边插入SD卡。
 ![](https://wiki.bambulab.com/x1/troubleshooting/enable-video-record/%E6%8F%92%E5%85%A5sd%E5%8D%A1.jpg)
2. 点击屏幕左侧菜单栏中的**设置**图标，点击顶部**通用**，选择**录像**。
 ![录像-x1.jpg](https://wiki.bambulab.com/x1/troubleshooting/enable-video-record/%E5%BD%95%E5%83%8F-x1.jpg)
3. 可打开录像功能并设置录像的清晰度。
 ![录像.jpg](https://wiki.bambulab.com/x1/troubleshooting/enable-video-record/%E5%BD%95%E5%83%8F.jpg)

### P1 系列

打开 Bambu Studio，进入**设备**页面，点击**相机设置**图标，可打开监控录像。

![p1-录像_中.png](https://wiki.bambulab.com/x1/troubleshooting/enable-video-record/p1-%E5%BD%95%E5%83%8F_%E4%B8%AD.png)

### A1 系列

点击**设置 > 相机选项**，打开**视频**功能。

|  |  |  |
| --- | --- | --- |

### H2 系列 / P2S / X2D

H2D、H2S 及 P2S 机型均配置外部 USB 接口，用于连接 U 盘。插入 U 盘后，设备支持录像文件存储功能。

![h2d插入u盘.png](https://wiki.bambulab.com/x1/troubleshooting/enable-video-record/h2d%E6%8F%92%E5%85%A5u%E7%9B%98.png)

#### 录像功能操作流程

1. 将 U 盘插入设备屏幕侧上盖组件的 USB 接口；

> **注意：** 若未插入 U 盘或外部存储设备未被识别，设备将弹出提示："没有外部存储，无法继续。请检查外部存储是否已插入，如果仍然无法读取，可以尝试格式化。"，无法进行后续步骤

1. 插入 U 盘后，依次点击设备界面 “**设置**” > “**录像**" > "**1080p**"，即可启用录像功能；

|  |  |
| --- | --- |

> **注意：** 功能开启后，设备将在打印任务启动时自动开始录制打印腔内视频（含打印暂停期间），并将视频文件存储至 SD 卡或已连接的 U 盘；打印任务结束后，录像将自动停止。

## SD 卡的规格和存储机制

- SD 卡的文件格式需为 FAT32，最大容量为 2TB。建议使用 Class 10 或 U1（最低写入速度 10MB/s）等级以上的 SD 卡。
- 打印机最多使用 85% 的 SD 卡内存存储视频。当 SD 卡内存占用达到 85% 以上时，将无法再存储新视频，但打印功能不会受到影响。如果 SD 卡剩余内存超过 15%，可以继续存储打印视频，直到占用达到 85%。一旦达到该占用率，新视频将覆盖旧视频。

## U 盘的规格要求和使用建议

| U 盘文件格式 | 执行格式化的操作系统 | 最大U盘容量 | 最大单个文件 |
| --- | --- | --- | --- |
| FAT32 | linux 或 MAC系统 | 2TB | 4GB |
|  | Windows 系统 | 32G | 4GB |
| exFAT | 任何系统 | 128PB | 16EB |

- 如果需要取下 U 盘，推荐使用 U 盘安全弹出功能，避免热拔插。直接拔出 U 盘可能会导致录像和延时摄影文件受损，无法打开。

![](https://wiki.bambulab.com/h2/manual/usb-pecifications-and-usage-recommendations/image-7.png)

- 推荐在打印机的 USB 接口上直接插入 U 盘，而不是读卡器+ SD 卡的模式。如果需要使用读卡器+ SD 卡，插拔时请直接插拔读卡器。

请参阅[H2D U 盘规格要求和使用建议](https://wiki.bambulab.com/zh/h2/manual/usb-pecifications-and-usage-recommendations)了解更多信息。

## 导出 SD 卡/U 盘中的录像视频

将 SD 卡/U 盘插入电脑，存储的录像文件都在 **ipcam** 文件夹里。

|  |  |
| --- | --- |
| X1 系列 | P1/A1 系列 |

**H2D**
 ![h2dfolder.png](https://wiki.bambulab.com/x1/troubleshooting/enable-video-record/h2dfolder.png)

录像视频分为多个文件，文件名包含相应的日期和时间。您可以根据文件名查找特定时间段的视频，以查看该时段内机器的打印情况。此外，也可以将这些视频发送给我们的售后团队进行分析。

![](https://wiki.bambulab.com/x1/troubleshooting/enable-video-record/%E5%BD%95%E5%83%8F%E8%A7%86%E9%A2%91%E6%96%87%E4%BB%B6.jpg)



## 媒体资源

- img: https://wiki.bambulab.com/x1/troubleshooting/enable-video-record/%E6%8F%92%E5%85%A5sd%E5%8D%A1.jpg
- img: https://wiki.bambulab.com/x1/troubleshooting/enable-video-record/%E5%BD%95%E5%83%8F-x1.jpg
- img: https://wiki.bambulab.com/x1/troubleshooting/enable-video-record/%E5%BD%95%E5%83%8F.jpg
- img: https://wiki.bambulab.com/x1/troubleshooting/enable-video-record/p1-%E5%BD%95%E5%83%8F_%E4%B8%AD.png
- img: https://wiki.bambulab.com/x1/troubleshooting/upload-log/%E8%AE%BE%E7%BD%AE--.png
- img: https://wiki.bambulab.com/x1/troubleshooting/enable-video-record/a1-%E7%9B%B8%E6%9C%BA.png
- img: https://wiki.bambulab.com/a1-screen-operation/a1-%E7%9B%B8%E6%9C%BA%E9%80%89%E9%A1%B9.jpg
- img: https://wiki.bambulab.com/x1/troubleshooting/enable-video-record/h2d%E6%8F%92%E5%85%A5u%E7%9B%98.png
- img: https://wiki.bambulab.com/x1/troubleshooting/sd-card-damage/%E5%BD%95%E5%88%B6.png
- img: https://wiki.bambulab.com/x1/troubleshooting/sd-card-damage/1080.png
- img: https://wiki.bambulab.com/h2/manual/usb-pecifications-and-usage-recommendations/image-7.png
- img: https://wiki.bambulab.com/x1/troubleshooting/enable-video-record/20241009-153408.jpg
- img: https://wiki.bambulab.com/x1/troubleshooting/enable-video-record/p1-a1.jpg
- img: https://wiki.bambulab.com/x1/troubleshooting/enable-video-record/h2dfolder.png
- img: https://wiki.bambulab.com/x1/troubleshooting/enable-video-record/%E5%BD%95%E5%83%8F%E8%A7%86%E9%A2%91%E6%96%87%E4%BB%B6.jpg

