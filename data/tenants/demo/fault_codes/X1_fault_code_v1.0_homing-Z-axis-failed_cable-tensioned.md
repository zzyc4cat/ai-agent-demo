---
source: https://wiki.bambulab.com/zh/x1/troubleshooting/homing-Z-axis-failed_cable-tensioned
fetched_at: 2026-10-26
title: Z轴回中失败错误—热床线缆被拉紧
media_count: 13
---

> 来源：https://wiki.bambulab.com/zh/x1/troubleshooting/homing-Z-axis-failed_cable-tensioned｜抓取日期：2026-10-26｜仅供本地检索演示，版权归原作者

Z轴回中失败错误—热床线缆被拉紧

---


## 问题现象：

1. Z轴回中失败

![](https://wiki.bambulab.com/x1/troubleshooting/homing-z-failed-1/err_code.jpg)

2. 连接到热床的线缆处于张紧状态。

## 造成的原因：

热床的移动的时候将线缆推向MC电路板，造成线缆太短无法和热床一起完全上升。

## 解决方案：

**临时解决方案：**

调高热床并关闭打印机电源。然后从Z轴丝杆间隙将线缆稍微向热床斜向上拉一点（如下图箭头方向），以使线缆的长度足以完成Z轴回中(见下图)。

![](https://wiki.bambulab.com/x1/troubleshooting/homing-z-failed-1/quick_solution.png)

**永久性解决方案：**

固定线缆以防止过度移动。

### 步骤 1 - 升高热床

将工具头移动到废料滑梯的边缘(以防发生碰撞)，并将热床抬高到顶部。

![](https://wiki.bambulab.com/x1/troubleshooting/homing-z-failed-1/move_th_and_hb.png)

### 步骤 2 - 移除螺栓

断开电源线，然后先后从后盖上卸下10个螺丝和4个螺丝，如图所示。一共有两种类型的螺丝，所以要注意区分，并记住两种螺丝的位置。

|  |  |
| --- | --- |

### 步骤 3 - 移除后盖

拆下后盖，先解锁左侧皮带张紧口，再解锁右侧皮带张紧口，以免被卡住。

|  |  |
| --- | --- |

### 步骤 4 - 热床线缆

现在可以看到热床的线缆，有一个卡口用于固定线缆。

|  |  |
| --- | --- |

### 步骤 5 - 使用线缆扎带

给线缆绑上泡棉胶带(不要扎得太紧，以防导致线缆内断)，防止它们向MC电路板方向移动太多。尝试移动线缆来确保其被扎带固定住了。

![](https://wiki.bambulab.com/x1/troubleshooting/homing-z-failed-1/snipaste_2022-11-10_11-33-20.jpg)

### 步骤 6 - 安装后盖

将后盖穿过料管支架，先安装右侧皮带张力调节端口，然后安装后盖。

|  |  |
| --- | --- |

### 步骤 7 - 锁紧螺栓

拧回螺栓。 注意一共有两种不同类型的螺丝，安装位置如下图。

|  |  |
| --- | --- |

## 媒体资源

- img: https://wiki.bambulab.com/x1/troubleshooting/homing-z-failed-1/err_code.jpg
- img: https://wiki.bambulab.com/x1/troubleshooting/homing-z-failed-1/quick_solution.png
- img: https://wiki.bambulab.com/x1/troubleshooting/homing-z-failed-1/move_th_and_hb.png
- img: https://wiki.bambulab.com/x1/troubleshooting/homing-z-failed-1/10_screw_1.png
- img: https://wiki.bambulab.com/x1/troubleshooting/homing-z-failed-1/4_screws_1.png
- img: https://wiki.bambulab.com/x1/troubleshooting/homing-z-failed-1/back_cover_1.png
- img: https://wiki.bambulab.com/x1/troubleshooting/homing-z-failed-1/back_cover_2.png
- img: https://wiki.bambulab.com/x1/troubleshooting/homing-z-failed-1/over_view.png
- img: https://wiki.bambulab.com/x1/troubleshooting/homing-z-failed-1/buckle.png
- img: https://wiki.bambulab.com/x1/troubleshooting/homing-z-failed-1/snipaste_2022-11-10_11-33-20.jpg
- img: https://wiki.bambulab.com/x1/troubleshooting/homing-z-failed-1/back_cover_3.png
- img: https://wiki.bambulab.com/x1/troubleshooting/homing-z-failed-1/10_screw_2.png
- img: https://wiki.bambulab.com/x1/troubleshooting/homing-z-failed-1/4_screws_2.png

