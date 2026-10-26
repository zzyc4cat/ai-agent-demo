---
source: https://wiki.bambulab.com/zh/x1/troubleshooting/z-timing-pulley
fetched_at: 2026-10-26
title: Z轴丝杆松动、Z滑块错位处理方案
media_count: 19
---

> 来源：https://wiki.bambulab.com/zh/x1/troubleshooting/z-timing-pulley｜抓取日期：2026-10-26｜仅供本地检索演示，版权归原作者

Z轴丝杆松动、Z滑块错位处理方案
如何重新固定松脱的Z轴同步带轮，和重新调整Z轴滑块的位置。

---


# 问题现象:

1. 丝杆在Z方向活动过大；

2. 3个Z轴滑块的高度出现偏差，并可能导致热床回零失败。

![](https://wiki.bambulab.com/x1/troubleshooting/loosen-belt-wheel/position_ng.png)

## 原因及解决方案

- Z轴同步带轮松动，需要重新锁紧同步带轮；
- Z轴运动过程中受外力或异物干涉，造成Z皮带打滑，从而导致3个Z滑块出现不同步的情况，这时需要重做Z轴滑块的一致性调整。

## 所需工具和材料

1. H1.5 和H2.0内六角扳手；
2. 刮刀或切口钳；
3. 锤子。

# 安全提示

> **重要提醒 ！** 在对打印机及其电子设备（包括工具头线缆）进行任何维护工作之前，请关闭打印机电源并断开电源连接，以避免发生电路短路从而引起额外的电子设备损坏和安全隐患。 在您对打印机进行维护或故障排查时，请先确认热端和热床的温度，避免在高温状态下操作，如果必须在高温状态下操作，请佩戴好隔热手套，以确保安全有效地执行维护工作。 如果您对本指南有任何疑问，请[点击这里提交工单](https://bambulab.cn/zh/sign-in?to=%2Fmy%2Fsupport%2Ftickets)，我们将及时回复并为您提供所需的帮助。

# 操作指南(一) 丝杆松动修复

## 步骤1 - 移除玻璃上盖和显示屏

断开电源线连接，移除玻璃上盖和LCD显示屏。

![](https://wiki.bambulab.com/x1/maintenance/replace-z-belt/remove_the_cover_plate.jpg)

## 步骤2 - 倒放打印机

倒放打印机，露出底部同步带轮。

![](https://wiki.bambulab.com/x1/maintenance/replace-z-belt/bottom_side_up.jpg)

## 步骤3 - 解锁同步带轮

| 找到松动的同步带轮，用刀片或钳子去除同步带上的AB胶 | 拧松2颗同步带轮固定螺丝 |
| --- | --- |

如果同步带轮卡住不动，可以使用锤子敲击丝杆底部，使丝杆与同步带轮有松动感。

![](https://wiki.bambulab.com/x1/troubleshooting/loosen-belt-wheel/knock_the_screw_rod.png)

## 步骤4 - 复位同步带轮

| 用手抓住丝杆并将其往打印机底座方向推，另一只手握住同步带轮沿反方向用力，将同步带轮复位。 | 正常的情况，丝杆应该在同步带轮外露出一小截，沿Z方向拉同步带轮，确认没有松动。 |
| --- | --- |

## 步骤5 - 锁定同步带轮

锁紧两颗同步带轮固定螺丝，如有条件，可重新在原来的位置打上AB胶进行加固。

![](https://wiki.bambulab.com/x1/troubleshooting/loosen-belt-wheel/2_screws.png)

## 步骤6 - 张紧Z轴皮带

| 拧松Z张紧器螺丝 | 用手拉动皮带往返动作3~5次，重新锁紧张紧器螺丝 |
| --- | --- |

## 步骤7 - 正放打印机，装好屏幕

正放打印机，连接屏幕并盖上玻璃上盖。

# 操作指南(二) Z轴滑块位置调整

## 步骤1 - 移除玻璃上盖和显示屏

断开电源线连接，移除玻璃上盖和LCD显示屏。

![](https://wiki.bambulab.com/x1/maintenance/replace-z-belt/remove_the_cover_plate.jpg)

## 步骤2 - 清洁打印机底座

| 清除印机底座上的异物 | 特别是光杆处的残留物 |
| --- | --- |

## 步骤3 - 锁定3个Z滑块

侧放打印机，拉动Z轴皮带，将热床下降到底部，然后用3颗滑块固定螺丝将3个滑块进行锁定，这里，因为3个滑块位置已有差异，所以会存在某个滑块没有完全贴合底座的情况。

![](https://wiki.bambulab.com/x1/maintenance/replace-z-motor/lock_sliders.jpg)

## 步骤4 - 解除Z皮带的张紧状态

释放Z张紧弹簧，拧松张紧器螺丝，使Z轴皮带处于松动的状态。

![](https://wiki.bambulab.com/x1/troubleshooting/loosen-belt-wheel/release_the_spring.png)

## 步骤5 - 调整Z滑块

用手压住皮带的一端，逐个转动同步带轮，确认将对应位置的Z滑块调至与底座贴合，并锁紧对应位置的滑块固定螺丝。

![](https://wiki.bambulab.com/x1/troubleshooting/loosen-belt-wheel/rotate_the_pulley.png)

## 步骤6 - 卡弹簧，解除Z滑块锁定

| 将弹簧的卡回原位 | 正放打印机，然后移除锁定Z轴滑块的3颗螺丝 |
| --- | --- |

## 步骤7 - 张紧皮带，拧紧螺丝

| 倒放打印机，用手拉动皮带往返动作3~5次 | 重新锁紧张紧器螺丝 |
| --- | --- |

## 步骤8 - 正放打印机，装好屏幕

正放打印机，连接屏幕并盖上玻璃上盖。

# 功能确认

用手逐个检查同步带轮，确认无明显松动现象。

# 设备校准

- 连接电源，启动打印机
- 如下图所示，进入 LCD 屏幕上的设置菜单，运行设备校准流程。

![](https://wiki.bambulab.com/x1/troubleshooting/loosen-belt-wheel/start_calibration.png)

如果有异常了，请排查组装是否有问题，排除后，再次运行设备校准。如果问题仍然存在，请联系Bambu Lab服务团队寻求进一步的帮助。

评论

## 媒体资源

- video: https://wiki.bambulab.com/x1/troubleshooting/loosen-belt-wheel/loose_lead_screw.mp4
- img: https://wiki.bambulab.com/x1/troubleshooting/loosen-belt-wheel/position_ng.png
- img: https://wiki.bambulab.com/x1/maintenance/replace-z-belt/remove_the_cover_plate.jpg
- img: https://wiki.bambulab.com/x1/maintenance/replace-z-belt/bottom_side_up.jpg
- img: https://wiki.bambulab.com/x1/troubleshooting/loosen-belt-wheel/remove_the_glue.png
- img: https://wiki.bambulab.com/x1/troubleshooting/loosen-belt-wheel/2_screws.png
- img: https://wiki.bambulab.com/x1/troubleshooting/loosen-belt-wheel/knock_the_screw_rod.png
- img: https://wiki.bambulab.com/x1/troubleshooting/loosen-belt-wheel/refit_the_belt_pulley_1.png
- img: https://wiki.bambulab.com/x1/troubleshooting/loosen-belt-wheel/refit_the_belt_pulley_2.png
- img: https://wiki.bambulab.com/x1/troubleshooting/loosen-belt-wheel/lock_the_tension_screw.png
- img: https://wiki.bambulab.com/x1/troubleshooting/loosen-belt-wheel/move_the_belt.png
- img: https://wiki.bambulab.com/x1/maintenance/replace-z-motor/clean_the_bottom1.jpg
- img: https://wiki.bambulab.com/x1/maintenance/replace-z-motor/clean_the_bottom2.jpg
- img: https://wiki.bambulab.com/x1/maintenance/replace-z-motor/lock_sliders.jpg
- img: https://wiki.bambulab.com/x1/troubleshooting/loosen-belt-wheel/release_the_spring.png
- img: https://wiki.bambulab.com/x1/troubleshooting/loosen-belt-wheel/rotate_the_pulley.png
- img: https://wiki.bambulab.com/x1/troubleshooting/loosen-belt-wheel/reset_the_spring.png
- img: https://wiki.bambulab.com/x1/maintenance/replace-z-motor/unlock_the_sliders.jpg
- img: https://wiki.bambulab.com/x1/troubleshooting/loosen-belt-wheel/start_calibration.png

