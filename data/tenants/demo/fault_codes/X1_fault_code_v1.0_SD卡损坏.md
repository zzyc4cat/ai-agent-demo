---
source: https://wiki.bambulab.com/zh/X1/troubleshooting/SD-card-damage
fetched_at: 2026-10-26
title: 开机后屏幕无法正常启动
media_count: 4
---

> 来源：https://wiki.bambulab.com/zh/X1/troubleshooting/SD-card-damage｜抓取日期：2026-10-26｜仅供本地检索演示，版权归原作者

开机后屏幕无法正常启动
本文介绍了 X1 系列打印机开机后屏幕无响应的解决方案。

---


## 适用机型

X1 系列

## 问题现象

开机后，屏幕一直停留在起始页，无法切换。

![起始页.jpg](https://wiki.bambulab.com/x1/troubleshooting/sd-card-damage/%E8%B5%B7%E5%A7%8B%E9%A1%B5.jpg)

## 原因

SD 卡损坏。

## 排查指引

### 关闭打印机

![关机.jpg](https://wiki.bambulab.com/x1/troubleshooting/sd-card-damage/%E5%85%B3%E6%9C%BA.jpg)

### 拔出 SD 卡

![退出sd.jpg](https://wiki.bambulab.com/x1/troubleshooting/sd-card-damage/%E9%80%80%E5%87%BAsd.jpg)

### 重新开机

重新开机，查看屏幕是否正常。如果正常，则说明 SD 卡损坏，需要更换 SD 卡。

## SD 卡的规格要求

如果使用打印机对 SD 卡进行格式化，Bambu Lab 打印机可支持高达 2TB 容量的 S D卡，支持格式为 FAT32 格式。

推荐使用 Class 10 或 U1（最低写入速度 10M/S）等级以上的 SD 卡。

> SD 卡格式化步骤如下：
>  ![格式化.jpg](https://wiki.bambulab.com/x1/troubleshooting/sd-card-damage/%E6%A0%BC%E5%BC%8F%E5%8C%96.jpg)

## SD 卡是如何进行工作的

Bambu Lab 打印机最多只会使用 SD 卡容量的 85%。如果已使用容量超过 85%，视频录制功能将无法使用。如果剩余容量超过 15%，您可以在打印时启用视频录制功能，直到 SD 卡容量达到 85%。此后，如果需要录制新视频，现有的视频将被清除，以释放空间。

请注意，**打印机目前仅支持 FAT32 格式的 SD 卡**。在 Windows 操作系统下，如果 SD 卡容量超过 32GB，默认格式为 exFAT。但对于 Linux 和 macOS，没有此限制。如果您使用 64GB 至 2TB 的 SD 卡，可通过 Linux 或 Mac OS 操作系统的电脑或者直接使用打印机将其格式化为 FAT32。



## 媒体资源

- img: https://wiki.bambulab.com/x1/troubleshooting/sd-card-damage/%E8%B5%B7%E5%A7%8B%E9%A1%B5.jpg
- img: https://wiki.bambulab.com/x1/troubleshooting/sd-card-damage/%E5%85%B3%E6%9C%BA.jpg
- img: https://wiki.bambulab.com/x1/troubleshooting/sd-card-damage/%E9%80%80%E5%87%BAsd.jpg
- img: https://wiki.bambulab.com/x1/troubleshooting/sd-card-damage/%E6%A0%BC%E5%BC%8F%E5%8C%96.jpg

