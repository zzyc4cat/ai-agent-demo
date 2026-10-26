---
source: https://wiki.bambulab.com/zh/x1/troubleshooting/cutter-stuck
fetched_at: 2026-10-26
title: 打印机提示切刀卡住
media_count: 11
---

> 来源：https://wiki.bambulab.com/zh/x1/troubleshooting/cutter-stuck｜抓取日期：2026-10-26｜仅供本地检索演示，版权归原作者

打印机提示切刀卡住

---


## 问题现象

打印过程中，屏幕上出现切刀卡住的提示，如下图所示：

![](https://wiki.bambulab.com/x1/troubleshooting/cutter-stuck/%E5%88%87%E5%88%80%E5%8D%A1%E4%BD%8F%E6%8A%A5%E9%94%99.png)

## 为什么会出现这个提示

当机器退料或者用AMS打印换料的时候，需要用切刀切断料线并把料线抽回。切料时，工具头将会移动到打印机的前方让顶杆块按压刀柄，刀柄会推动刀片切断挤出机下方的料线。在切料完成后，刀柄会自动回弹。切刀刀柄如下图所示：

![](https://wiki.bambulab.com/x1/troubleshooting/cutter-stuck/%E5%88%87%E5%88%80%E5%88%80%E6%9F%84.png)

切刀的刀柄处有磁铁，而挤出机对应的位置有个霍尔传感器，打印机就是通过霍尔传感器感应切刀位置来判断它是否成功复位.**当检测到切刀刀柄持续两分钟都没有复位，屏幕上就会弹出对应的提示。**

![](https://wiki.bambulab.com/x1/troubleshooting/cutter-stuck/%E5%88%80%E6%9F%84%E7%A3%81%E9%93%81.jpg)

![](https://wiki.bambulab.com/x1/troubleshooting/cutter-stuck/%E9%9C%8D%E5%B0%94%E4%BC%A0%E6%84%9F%E5%99%A8%E4%BD%8D%E7%BD%AE.png)

切刀卡住时，刀柄将会卡在工具头内没有回弹，如下图：

![](https://wiki.bambulab.com/x1/troubleshooting/cutter-stuck/%E5%88%87%E5%88%80%E5%8D%A1%E4%BD%8F.png)

## 解决办法

1. 当屏幕出现切刀卡住的提示的时候，首先检查刀柄是否真的卡在了工具头内，如果发现刀柄在原位并没有卡住，那么有几种可能：

- 刀柄在卡住一段时间后又自动复位了，这跟打印的材料有关。打印support或slik材料的时候偶尔会出现这个情况，这时候直接点击“重试”即可。如果不再出现提示，那么就可以继续打印。
- 霍尔传感器误检测了。首先检查霍尔传感器上是否有异物，可以清洁一下磁铁和霍尔传感器的位置后重试。如果霍尔传感器故障或者是线缆断了（如下图）也会导致误报，如下图所示。

![](https://wiki.bambulab.com/x1/troubleshooting/cutter-stuck/%E9%9C%8D%E5%B0%94%E4%BC%A0%E6%84%9F%E5%99%A8%E7%BA%BF%E6%96%AD%E4%BA%86.png)

- 切刀卡住误报也可能由接触不良或连接器损坏引起。请尝试重新插拔下图中的10pin连接器（有时需要重复插拔几次），然后再次尝试打印以查看错误是否仍然存在。如仍有问题，请联系售后团队。

![](https://wiki.bambulab.com/x1/troubleshooting/hmscode/toolhead/front-cover-fall-off/10pin%E7%AB%AF%E5%AD%90.png)

![](https://wiki.bambulab.com/x1/troubleshooting/hmscode/toolhead/front-cover-fall-off/%E6%8F%92%E6%8B%9410pin%E7%AB%AF%E5%AD%90.jpg)

2. 当出现切刀卡住提示时，检查发现切刀确实卡住了并没有自动复位，则有以下几种可能：

- 热端堵头了，当热端堵住的时候，挤出机和热端之间一段的料线压力过大，会导致刀片被夹住无法顺利回弹。这种情况需要拆除热端并清理，清理热端的具体步骤可以参考这篇wiki：[https://wiki.bambulab.com/zh/x1/troubleshooting/nozzle-clog](https://wiki.bambulab.com/zh/x1/troubleshooting/nozzle-clog)
- 如果热端没有堵头，但是切刀仍会在切料的时候频繁卡住，可以先退出挤出机中的料线，尝试一下在没有料线的情况下，手动按压切刀刀柄看它是否会被卡住。

![](https://wiki.bambulab.com/x1/troubleshooting/cutter-stuck/%E6%89%8B%E5%8A%A8%E6%8C%89%E5%8E%8B%E5%88%80%E6%9F%84.png)

- 如果切刀仍会卡住，则说明切刀两侧和挤出机的内壁摩擦力过大导致无法顺利回弹。这有可能是生产中的误差导致的，您可以尝试取出切刀，用小刀或其他工具将切刀的左右两侧削磨掉一小部分，装回去再按压几下，看摩擦力是否减小。如何取出切刀你可以参考这篇文章：[https://wiki.bambulab.com/zh/x1/maintenance/replace-cutter](https://wiki.bambulab.com/zh/x1/maintenance/replace-cutter)

![](https://wiki.bambulab.com/x1/troubleshooting/cutter-stuck/%E6%89%93%E7%A3%A8%E5%88%87%E5%88%80%E4%B8%A4%E4%BE%A7.png)

- 有时候工具头冷却风扇的线缆也会卡住切刀刀柄导致其无法弹回。要注意检查并收纳好线缆，不要让它干涉刀柄回弹。

![](https://wiki.bambulab.com/x1/troubleshooting/cutter-stuck/%E7%BA%BF%E7%BC%86%E5%8D%A1%E4%BD%8F%E5%88%80%E6%9F%84.jpg)



## 媒体资源

- img: https://wiki.bambulab.com/x1/troubleshooting/cutter-stuck/%E5%88%87%E5%88%80%E5%8D%A1%E4%BD%8F%E6%8A%A5%E9%94%99.png
- img: https://wiki.bambulab.com/x1/troubleshooting/cutter-stuck/%E5%88%87%E5%88%80%E5%88%80%E6%9F%84.png
- img: https://wiki.bambulab.com/x1/troubleshooting/cutter-stuck/%E5%88%80%E6%9F%84%E7%A3%81%E9%93%81.jpg
- img: https://wiki.bambulab.com/x1/troubleshooting/cutter-stuck/%E9%9C%8D%E5%B0%94%E4%BC%A0%E6%84%9F%E5%99%A8%E4%BD%8D%E7%BD%AE.png
- img: https://wiki.bambulab.com/x1/troubleshooting/cutter-stuck/%E5%88%87%E5%88%80%E5%8D%A1%E4%BD%8F.png
- img: https://wiki.bambulab.com/x1/troubleshooting/cutter-stuck/%E9%9C%8D%E5%B0%94%E4%BC%A0%E6%84%9F%E5%99%A8%E7%BA%BF%E6%96%AD%E4%BA%86.png
- img: https://wiki.bambulab.com/x1/troubleshooting/hmscode/toolhead/front-cover-fall-off/10pin%E7%AB%AF%E5%AD%90.png
- img: https://wiki.bambulab.com/x1/troubleshooting/hmscode/toolhead/front-cover-fall-off/%E6%8F%92%E6%8B%9410pin%E7%AB%AF%E5%AD%90.jpg
- img: https://wiki.bambulab.com/x1/troubleshooting/cutter-stuck/%E6%89%8B%E5%8A%A8%E6%8C%89%E5%8E%8B%E5%88%80%E6%9F%84.png
- img: https://wiki.bambulab.com/x1/troubleshooting/cutter-stuck/%E6%89%93%E7%A3%A8%E5%88%87%E5%88%80%E4%B8%A4%E4%BE%A7.png
- img: https://wiki.bambulab.com/x1/troubleshooting/cutter-stuck/%E7%BA%BF%E7%BC%86%E5%8D%A1%E4%BD%8F%E5%88%80%E6%9F%84.jpg

