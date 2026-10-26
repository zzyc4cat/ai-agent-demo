---
source: https://wiki.bambulab.com/zh/x1/troubleshooting/AMS-first-stage-feeder-fault
fetched_at: 2026-10-26
title: AMS 上下料异常故障排查
media_count: 25
---

> 来源：https://wiki.bambulab.com/zh/x1/troubleshooting/AMS-first-stage-feeder-fault｜抓取日期：2026-10-26｜仅供本地检索演示，版权归原作者

AMS 上下料异常故障排查
本文将介绍上下料常见故障以及处理方法

---


## 故障现象

1. 插入 10 cm 左右长度的耗材后，AMS 始终检测不到耗材，LED 不亮或白色闪烁；

2. 在未插入耗材的情况下，AMS 的指示灯依然为白色常亮，持续检测到存在耗材；

3. 插入耗材后，AMS 的指示灯变为白色常亮，但是电机始终无反应，齿轮无法转动以拉入耗材；

4. 插入耗材后，AMS 的指示灯变为白色常亮，电机能够带动齿轮转动，但依然无法拉入耗材。

以上异常情况您也可通过指示灯状态来判断（[AMS指示灯状态解析](https://wiki.bambulab.com/zh/x1/troubleshooting/ams-led-status)）。

![](https://wiki.bambulab.com/x1/troubleshooting/ams-feeder-fault/%E6%B2%A1%E6%96%99%E6%A3%80%E6%B5%8B%E4%B8%BA%E6%9C%89%E6%96%99.jpg)

## 处理方法

如果入料口的传感器出现误检测（**有料检测不到**或**没料检测为有料**），这通常是入料口中有残留的碎屑或磁铁磨损导致的，可以仅处理入料口部分。

如果入料口的传感器正常，但插入耗材后设备无法自动拉入，可能是上下料的电机工作异常或内部存在耗材碎屑，请检查并清理上下料组件内部。

## 拆除工作

### 步骤 1：拆卸上下料组件

先参考 [更换上下料组件指南](https://wiki.bambulab.com/zh/x1/maintenance/replace-first-stage-feeder) 拆下上下料组件。

![image1.png](https://wiki.bambulab.com/x1/troubleshooting/ams-feeder-fault/image1.png)

### 步骤 2：分离上盖和底座

拧松图中标记的 4 颗螺丝，

![image2.png](https://wiki.bambulab.com/x1/troubleshooting/ams-feeder-fault/image2.png)
 ![image3.png](https://wiki.bambulab.com/x1/troubleshooting/ams-feeder-fault/image3.png)
 ![image4.png](https://wiki.bambulab.com/x1/troubleshooting/ams-feeder-fault/image4.png)

小心分离上盖和底座，

断开入料口组件主板上的线缆。
 ![image5.png](https://wiki.bambulab.com/x1/troubleshooting/ams-feeder-fault/image5.png)

断开入料口组件主板上的线缆。

> 线缆连接器上可能存在白胶，需刮除白胶后拔下连接器。

![image6.png](https://wiki.bambulab.com/x1/troubleshooting/ams-feeder-fault/image6.png)

### 步骤 3：拆下入料口组件

使用 H2.0 螺丝刀顶住入料口组件，并将入料口组件架空一定高度，逐渐向下施加力，尝试顶出销轴。

![image10.png](https://wiki.bambulab.com/x1/troubleshooting/ams-feeder-fault/image10.png)
 ![image11.png](https://wiki.bambulab.com/x1/troubleshooting/ams-feeder-fault/image11.png)

取出销轴，移除入料口组件。

![image12.png](https://wiki.bambulab.com/x1/troubleshooting/ams-feeder-fault/image12.png)

### 步骤 4：拆卸入料口电路板

拧下图中标记的 2 个螺丝，取下电路板，并小心吸出内部的弹簧和磁铁。

![image13.png](https://wiki.bambulab.com/x1/troubleshooting/ams-feeder-fault/image13.png)
 ![image14.png](https://wiki.bambulab.com/x1/troubleshooting/ams-feeder-fault/image14.png)

> 弹簧和磁铁尺寸较小，请勿遗失。

## 处理工作

### 步骤 1：清理入料口

向入料口组件中插入一截耗材，顶出堵塞的耗材碎屑或断料。

![image15.png](https://wiki.bambulab.com/x1/troubleshooting/ams-feeder-fault/image15.png)

### 步骤 2：清理上下料

使用无纺布或纸巾清理上盖的滚花轮，底座的齿轮。

![image8.png](https://wiki.bambulab.com/x1/troubleshooting/ams-feeder-fault/image8.png)
 ![image17.png](https://wiki.bambulab.com/x1/troubleshooting/ams-feeder-fault/image17.png)

### 步骤 3：重装电机连接线

对于电机无法工作的情况，需重新插拔电机的连接线。如果后续电机仍然无法正常工作，则需要更换整个上下料组件。

![image26.png](https://wiki.bambulab.com/x1/troubleshooting/ams-feeder-fault/image26.png)

### 步骤 4：检查磁铁是否磨损

如果磁铁出现磨损，则需要更换新的入料口组件。

![磨损zh.png](https://wiki.bambulab.com/ams-2-pro/maintenance/replace-the-feed-funnel-assy/%E7%A3%A8%E6%8D%9Fzh.png)

## 安装工作

### 步骤 1：安装磁铁和电路板

将磁贴和弹簧塞入孔洞中。

![image16.png](https://wiki.bambulab.com/x1/troubleshooting/ams-feeder-fault/image16.png)

放上电路板并拧紧固定螺丝

![image13.png](https://wiki.bambulab.com/x1/troubleshooting/ams-feeder-fault/image13.png)

### 步骤 2：安装入料口组件

重新安装销轴，固定入料口组件

![image18.png](https://wiki.bambulab.com/x1/troubleshooting/ams-feeder-fault/image18.png)

### 步骤 3：安装上盖和底座

将底座上的齿轮调整到下图角度。

![image20.png](https://wiki.bambulab.com/x1/troubleshooting/ams-feeder-fault/image20.png)

缓慢装回上盖，确保安装后齿轮位置不变。

![image25.png](https://wiki.bambulab.com/x1/troubleshooting/ams-feeder-fault/image25.png)

调整弹簧位置。

![image21.png](https://wiki.bambulab.com/x1/troubleshooting/ams-feeder-fault/image21.png)
 ![image22.png](https://wiki.bambulab.com/x1/troubleshooting/ams-feeder-fault/image22.png)

拧紧 4 颗固定螺丝。

![image24.png](https://wiki.bambulab.com/x1/troubleshooting/ams-feeder-fault/image24.png)
 ![image23.png](https://wiki.bambulab.com/x1/troubleshooting/ams-feeder-fault/image23.png)
 ![image4.png](https://wiki.bambulab.com/x1/troubleshooting/ams-feeder-fault/image4.png)

### 步骤 4：安装上下料组件

参考 [更换上下料组件指南](https://wiki.bambulab.com/zh/x1/maintenance/replace-first-stage-feeder) 将上下料组件安装到 AMS 中框。

## 功能验证

插入耗材后，AMS 能够自动拉入耗材；AMS 能够完成进退料工作。



## 媒体资源

- img: https://wiki.bambulab.com/x1/troubleshooting/ams-feeder-fault/%E6%B2%A1%E6%96%99%E6%A3%80%E6%B5%8B%E4%B8%BA%E6%9C%89%E6%96%99.jpg
- img: https://wiki.bambulab.com/x1/troubleshooting/ams-feeder-fault/image1.png
- img: https://wiki.bambulab.com/x1/troubleshooting/ams-feeder-fault/image2.png
- img: https://wiki.bambulab.com/x1/troubleshooting/ams-feeder-fault/image3.png
- img: https://wiki.bambulab.com/x1/troubleshooting/ams-feeder-fault/image4.png
- img: https://wiki.bambulab.com/x1/troubleshooting/ams-feeder-fault/image5.png
- img: https://wiki.bambulab.com/x1/troubleshooting/ams-feeder-fault/image6.png
- img: https://wiki.bambulab.com/x1/troubleshooting/ams-feeder-fault/image10.png
- img: https://wiki.bambulab.com/x1/troubleshooting/ams-feeder-fault/image11.png
- img: https://wiki.bambulab.com/x1/troubleshooting/ams-feeder-fault/image12.png
- img: https://wiki.bambulab.com/x1/troubleshooting/ams-feeder-fault/image13.png
- img: https://wiki.bambulab.com/x1/troubleshooting/ams-feeder-fault/image14.png
- img: https://wiki.bambulab.com/x1/troubleshooting/ams-feeder-fault/image15.png
- img: https://wiki.bambulab.com/x1/troubleshooting/ams-feeder-fault/image8.png
- img: https://wiki.bambulab.com/x1/troubleshooting/ams-feeder-fault/image17.png
- img: https://wiki.bambulab.com/x1/troubleshooting/ams-feeder-fault/image26.png
- img: https://wiki.bambulab.com/ams-2-pro/maintenance/replace-the-feed-funnel-assy/%E7%A3%A8%E6%8D%9Fzh.png
- img: https://wiki.bambulab.com/x1/troubleshooting/ams-feeder-fault/image16.png
- img: https://wiki.bambulab.com/x1/troubleshooting/ams-feeder-fault/image18.png
- img: https://wiki.bambulab.com/x1/troubleshooting/ams-feeder-fault/image20.png
- img: https://wiki.bambulab.com/x1/troubleshooting/ams-feeder-fault/image25.png
- img: https://wiki.bambulab.com/x1/troubleshooting/ams-feeder-fault/image21.png
- img: https://wiki.bambulab.com/x1/troubleshooting/ams-feeder-fault/image22.png
- img: https://wiki.bambulab.com/x1/troubleshooting/ams-feeder-fault/image24.png
- img: https://wiki.bambulab.com/x1/troubleshooting/ams-feeder-fault/image23.png

