---
source: https://wiki.bambulab.com/zh/x1/troubleshooting/chamber-led-issue-and-ap-reboot
fetched_at: 2026-10-26
title: 机箱补光灯异常&打印机重启
media_count: 5
---

> 来源：https://wiki.bambulab.com/zh/x1/troubleshooting/chamber-led-issue-and-ap-reboot｜抓取日期：2026-10-26｜仅供本地检索演示，版权归原作者

机箱补光灯异常&打印机重启
关于X1系列LED补光灯工作异常的排查指引

---


## 问题现象:

1. 补光灯暗淡且无法关闭；

2. 补光灯亮度正常但无法关闭;

3. 补光灯只有部分灯珠正常开启，控制正常；

4. AP重启，显示屏重现开机画面;

5. 开机后AP不启动，黑屏，MC板指示灯正常。

## 原因及解决方案

1. 改装导致AP板LED驱动烧坏，更换AP主板和补光灯电缆（或整个补光灯组件）；

2. 补光灯线缆破损短路，更换更换补光灯电缆（或整个补光灯组件）；

3. 补光灯部分灯珠烧坏，更换补光灯；

4. AP 板5V供电IC烧坏，更换AP主板和补光灯电缆（或整个补光灯组件）。

## 安全和操作提示

在进行拆装作业时，需要确认打印机是断电状态。

## 所需的工具

- H2.0 内六角扳手
- 万用表
- 镊子

## 排查指引

### 一、补光灯暗淡且无法关闭

LED补光灯电路最高支持5V 0.3A补光灯，短路或过流会导致AP板损坏。可以用万用表测量补光灯连接器处的电压确定是否AP板已经烧毁。

**排查方法：**打印机处于开启的状态下，用万用表测量LED连接器黑色线缆的pin针与打印机外壳间的电压，如果电压大于1V且LED暗淡则确定AP板LED驱动电路烧毁。这种情况下，线缆短路风险很大，建议将AP主板和补光灯线缆一起换掉。

![](https://wiki.bambulab.com/x1/troubleshooting/chamer-led/led_power_test.png)

如果用户没有万用表，也优先考虑更换AP主板和补光灯线缆。

### 二：补光灯常亮且亮度正常

补光灯线缆在装配过程比较容易磨破，如果黑色线磨破和外壳短路，会造成补光灯无法关闭。一般情况摇晃下补光灯线缆，补光灯的功能会恢复。

**排查方法：**关机状态下，用万用表测量补光灯连接器黑色线缆与打印机外壳的导通性，如果是导通的，说明有短路的情况，需要更换补光灯线缆。

![](https://wiki.bambulab.com/x1/troubleshooting/chamer-led/short_circuit_check.jpg)

### 三：补光灯灯珠不全亮

LED补光灯只有部分灯珠是亮起的，且亮度正常。说明是不亮的灯珠烧坏了，可以更换LED补光灯。

### 四：AP重启，显示屏重现开机画面

启动打印机或打印机在工作状态时，AP掉电重启，表现为在屏幕上可以重复看到开机的画面，一般是补光灯红色线缆与外壳短路。

**排查方法：**断开补光灯连接j线缆后进行打印，如果打印机恢复正常就说明需要更换补光灯线缆。也可能增加在关机状态下，检查，用万用表测试补光灯红色线缆与打印机外壳的导电性。

### 五：开机后LED不亮，显示屏黑屏，AP不启动

AP主板上的电源指示灯（常亮）正常，但工作状态指示灯没有亮起。

![](https://wiki.bambulab.com/x1/troubleshooting/black-screen/ap_board_failed.jpg)

**排查方法：**可以查看5V 供电IC是否烧毁，一般烧毁后会有一个印，如果是5V IC烧毁的话需要更换AP板和补光灯。

如果5V 供电IC没有烧毁，则只需更换AP主板。

|  |  |
| --- | --- |

## 部件更换、排查链接

- [更换机箱LED灯条](https://wiki.bambulab.com/zh/x1/maintenance/replace-the-chamber-led)
- [更换AP主板](https://wiki.bambulab.com/zh/x1/maintenance/replace-ap-board)
- [显示屏黑屏、闪屏故障排查](https://wiki.bambulab.com/zh/x1/troubleshooting/black-flicker-screen)



## 媒体资源

- img: https://wiki.bambulab.com/x1/troubleshooting/chamer-led/led_power_test.png
- img: https://wiki.bambulab.com/x1/troubleshooting/chamer-led/short_circuit_check.jpg
- img: https://wiki.bambulab.com/x1/troubleshooting/black-screen/ap_board_failed.jpg
- img: https://wiki.bambulab.com/x1/troubleshooting/chamer-led/5v_ic.png
- img: https://wiki.bambulab.com/x1/troubleshooting/chamer-led/5v_burnt_out.jpg

