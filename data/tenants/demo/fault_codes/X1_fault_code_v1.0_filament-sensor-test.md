---
source: https://wiki.bambulab.com/zh/x1/troubleshooting/filament-sensor-test
fetched_at: 2026-10-26
title: 霍尔开关故障排查指南
media_count: 100
---

> 来源：https://wiki.bambulab.com/zh/x1/troubleshooting/filament-sensor-test｜抓取日期：2026-10-26｜仅供本地检索演示，版权归原作者

霍尔开关故障排查指南
本文介绍了如何对霍尔开关进行检测

---

页面内容
何时使用？
所需工具
安全提示
结束语
标签
霍尔板
最后编辑
Jessie
Last Tuesday at 4:02 PM

## 何时使用？

- 打印机提示“耗材送往挤出机失败”，但工具头上方料管中有耗材。
- 使用 AMS 或 AMS Lite 打印时，打印机提示“请将外挂料盘的耗材拉出”，但料管中没有耗材。
- 打印机提示"请把耗材插入进料口，直到推不动为止”，但耗材已经进入挤出机。

## 所需工具

- 一段耗材
- （可选）H1.5 & H2.0 内六角扳手
- （可选）平头镊子

## 安全提示

> **重要提醒 ！** 在对打印机及其电子设备（包括工具头线缆）进行任何维护工作之前，请关闭打印机电源并断开电源连接，以避免发生电路短路从而引起额外的电子设备损坏和安全隐患。
> 
> 在您对打印机进行维护或故障排查时，请先确认热端和热床的温度，避免在高温状态下操作，如果必须在高温状态下操作，请佩戴好隔热手套，以确保安全有效地执行维护工作。

**本篇指南涵盖多个机型，请点击对应标签跳转至特定机型对应章节**

- A2L
- H2 系列
- P2S
- X2D （主挤出机）
- X2D （辅助挤出机）
- X1/P1 系列
- A1 系列

#### 检测指引

按压黑色压块后，拔下五通组件上的料管。
 ![](https://wiki.bambulab.com/x1/troubleshooting/filament-sensor-test/a2l_(3).jpg)

向五通组件内部插入一截耗材。
 ![](https://wiki.bambulab.com/x1/troubleshooting/filament-sensor-test/a2l_(4).jpg)

观察打印机屏幕上挤出机位置是否亮起小绿点。

|  |  |
| --- | --- |
|  |  |

- 若小绿点随着插入耗材而亮起，则传感器工作正常；
- 若小绿点无法亮起或一直亮起，则进一步排查故障情况。

#### 拆装指引

拧下五通底座的固定螺丝。
 ![](https://wiki.bambulab.com/x1/troubleshooting/filament-sensor-test/a2l_(7).jpg)

小心取出五通底座。
 ![](https://wiki.bambulab.com/x1/troubleshooting/filament-sensor-test/a2l_(8).jpg)

拧松霍尔板的固定螺丝后，翻开霍尔板。

|  |  |
| --- | --- |
|  |  |

#### 排障指引

使用气吹或者吹风机清理磁铁部位。
 ![](https://wiki.bambulab.com/x1/troubleshooting/filament-sensor-test/a2l_(1).jpg)

插入一截耗材，确保磁铁能够正常移动。
 ![](https://wiki.bambulab.com/x1/troubleshooting/filament-sensor-test/a2l_(1).webp)

使用干净的纸巾擦拭电路板两面，避免灰尘影响传感器判断，再重新装回五通底座。

完成后重新开机验证屏幕上小绿点状态，若故障依旧，请参考[该Wiki](https://wiki.bambulab.com/zh/a2l/maintenance/replace-th-board)重新连接 TH 板端的排线插头（5号）。若后续故障依旧，则需要更换新的霍尔开关板，请参考[该Wiki](https://wiki.bambulab.com/zh/a2l/maintenance/replace-filament-sensor-unit)。

![](https://wiki.bambulab.com/x1/troubleshooting/filament-sensor-test/a2l_(2).jpg)

| 序号 | 连接对象 | 序号 | 连接对象 |
| --- | --- | --- | --- |
| 1 | 涡流线圈 | 4 | 热端加热组件 |
| 2 | 热端风扇 | 5 | 进料霍尔板 |
| 3 | 部件风扇 | 6 | A3508挤出电机 |

#### 检测指引

移除工具头增强散热风扇或前盖。向上拔起风扇连接器以断开连接，用右手托住风扇底部并向上推，用左手捏住风扇顶部并向外抬起以将其移除。

![remove_front_fan.gif](https://wiki.bambulab.com/h2/troubleshooting/filament-sensor/remove_front_fan.gif)

按压气动连接器并拔出料管，针对左侧或右侧挤出机。具体取决于您正在排查哪个挤出机的进料问题。

![remove_ptfe_tubes.gif](https://wiki.bambulab.com/h2/troubleshooting/filament-sensor/remove_ptfe_tubes.gif)

在屏幕上选择左侧或右侧挤出机，然后手动将一段耗材插入挤出机。检查屏幕上的耗材页面：

- 如果屏幕显示耗材存在（绿灯亮起），则传感器功能正常。
- 如果屏幕无法亮起小绿灯，则可能表明传感器故障导致误检测。请继续进行进一步的故障排除。

![filament_sensor_check.gif](https://wiki.bambulab.com/h2/troubleshooting/filament-sensor/filament_sensor_check.gif)

![h2halltest.png](https://wiki.bambulab.com/x1/troubleshooting/filament-sensor-test/h2halltest.png)

#### 拆卸与组装指南

参考 [更换 H2D & H2C 挤出机从动轮组件](https://wiki.bambulab.com/zh/h2/maintenance/replace-dual-extruder-idlers-and-filament-sensor) 小心移除从动轮侧面的耗材传感器，以便您可以自由接触到摆动臂。

移除传感器的固定螺丝并小心取下耗材传感器。

![filament_sensor_h2_series.png](https://wiki.bambulab.com/h2/troubleshooting/filament-sensor/filament_sensor_h2_series.png)

#### 故障排除步骤

插入一小段耗材，观察摆动臂是否移动顺畅，并确认移除耗材后摆动臂是否自动复位。

- 如果摆动臂异常、卡在耗材上或有阻力地回弹，请检查摆动臂枢轴处是否有异物并彻底清洁。
- 如果摆动臂工作正常，则耗材传感器故障。请参考 [更换 H2D & H2C 挤出机从动轮组件](https://wiki.bambulab.com/zh/h2/maintenance/replace-dual-extruder-idlers-and-filament-sensor) 进行更换。

![waswbix1foamiqx8w2wcx8wdncc.webp](https://wiki.bambulab.com/h2/troubleshooting/hmscode/07fe_2000_0002_0002/waswbix1foamiqx8w2wcx8wdncc.webp)

#### 检测指引

打开工具头磁吸前壳，按压连接器锁扣拔出连接插头，取下工具头前盖。

|  |  |
| --- | --- |
|  |  |

用镊子按压料管支架气动接头黑色部分，移除铁氟龙料管。

![remove_tube.jpg](https://wiki.bambulab.com/x1/troubleshooting/filament-sensor-test/remove_tube.jpg)

点击屏幕上的**控制** > **喷嘴和挤出机**。

|  |  |
| --- | --- |
|  |  |

将一段料管手动插入挤出机后拔出，观察挤出机处图像变化。

> 霍尔开关正常工作时，插入耗材，屏幕显示挤出机内部有耗材图像；拔出耗材，耗材图像消失。

|  |  |
| --- | --- |
|  |  |

如果插入和拔出耗材时屏幕图像都正常，则霍尔传感器正常。若不正常，请参考以下方法进行排障。

#### 拆卸指引

请参考[更换工具头外壳](https://wiki.bambulab.com/zh/p2s/maintenance/replace-toolhead-housing)，将工具头中框和后盖（下图 2、3 部分）移除。

![toolhead_housing_001.png](https://public-cdn.bblmw.com/wiki/new/p2s/maintenance/extruder_unit/toolhead_housing_001.png)

用镊子辅助，拨开霍尔开关板连接器前盖，移除连接线。

![remove_extruder_filament_sensor_cable.webp](https://wiki.bambulab.com/x1/troubleshooting/filament-sensor-test/remove_extruder_filament_sensor_cable.webp)

用 H1.5 内六角扳手松开霍尔开关板组件两颗螺丝。

![remove_2_screws.jpg](https://wiki.bambulab.com/x1/troubleshooting/filament-sensor-test/remove_2_screws.jpg)

轻轻晃动霍尔开关板组件，向上移除。

![remove_extruder_filament_sensor.webp](https://wiki.bambulab.com/x1/troubleshooting/filament-sensor-test/remove_extruder_filament_sensor.webp)

#### 排障指引

清理霍尔开关组件内部残留耗材（若有）。将一段耗材从气动接口处插入，观察摇臂工作情况。

摇臂功能正常时，插入耗材摇臂被顶起；拔出耗材摇臂自动落下。

![inspect_the_arm.webp](https://wiki.bambulab.com/x1/troubleshooting/filament-sensor-test/inspect_the_arm.webp)

> 如果摇臂卡住，将摇臂左右移动，即可归位。

#### 组装指引

将霍尔开关板组件放回，用 H1.5 内六角扳手重新安装霍尔开关板组件两颗螺丝。

![remove_2_screws.jpg](https://wiki.bambulab.com/x1/troubleshooting/filament-sensor-test/remove_2_screws.jpg)

按下图所示放回霍尔开关板组件连接线，并盖上连接器盖板。

|  |  |
| --- | --- |
|  |  |

请参考[更换工具头外壳](https://wiki.bambulab.com/zh/p2s/maintenance/replace-toolhead-housing)，安装工具头中框和后盖（下图 2、3 部分）。

![toolhead_housing_001.png](https://public-cdn.bblmw.com/wiki/new/p2s/maintenance/extruder_unit/toolhead_housing_001.png)

安装铁氟龙料管

![install_tube.jpg](https://wiki.bambulab.com/x1/troubleshooting/filament-sensor-test/install_tube.jpg)

重新安装工具头前盖排线，然后安装工具头前盖。

> 安装排线时，请注意连接器锁扣朝上。

![install_the_toolhead_front_cover_cable.png](https://wiki.bambulab.com/x1/troubleshooting/filament-sensor-test/install_the_toolhead_front_cover_cable.png)

#### 检测指引

打开工具头前盖，按压连接器锁扣并拔掉插头，取下工具头前盖组件。

![](https://public-cdn.bblmw.com/wiki/new/x2d/filament-sensor-test/016.jpg)

按住气动接头拔出料管，手动将一段耗材插入挤出机内部。

|  |  |
| --- | --- |

检查屏幕的耗材页面：

- 如果屏幕显示有料，则为传感器正常；
- 如果屏幕显示无料，则可能是传感器异常导致误报，请执行后续排查步骤。

![](https://public-cdn.bblmw.com/wiki/new/x2d/filament-sensor-test/010.png)

#### 拆装指引

参考[更换左霍尔检测板](https://wiki.bambulab.com/zh/x2d/maintenance/replace-extruder-filament-sensor-left)，小心取出左霍尔组件，切勿用力拉扯；取出后移除侧面两颗固定螺丝。

|  |  |
| --- | --- |

#### 排障指引

插入一小段耗材，观察摇臂动作是否顺畅，并确认取出耗材后摇臂能否自动复位。

- 如果摇臂异常，卡住耗材或回弹卡涩，需检查摇臂转轴是否存在异物，并将其清理干净。
- 如果摇臂正常，则霍尔传感器故障，请参考[更换左霍尔检测板](https://wiki.bambulab.com/zh/x2d/maintenance/replace-extruder-filament-sensor-left)进行更换。

![](https://public-cdn.bblmw.com/wiki/new/x2d/filament-sensor-test/018.webp)

#### 检测指引

按住黑色气动接头，拔出料管。

![](https://public-cdn.bblmw.com/wiki/new/x2d/filament-sensor-test/004.jpg)

插入耗材，同时观察打印机屏幕的耗材显示状态：

- 如果屏幕显示有料，则传感器正常；
- 如果屏幕显示无料，则可能是传感器异常导致误报，请执行后续排查步骤。

|  |  |
| --- | --- |

#### 拆装指引

拆下辅助挤出机，详细步骤请参考 [更换 X2D 辅助挤出机配件](https://wiki.bambulab.com/zh/x2d/maintenance/replace-auxiliary-extruder)。

|  |  |
| --- | --- |

#### 排障指引

移除顶盖7颗固定螺丝，从入料口插入一段耗材，观察摇臂动作。

- 如果摇臂异常，卡住耗材或回弹卡涩，需检查摇臂转轴是否存在异物，并将其清理干净。
- 如果摇臂正常，则霍尔传感器故障，需更换辅助挤出机。

|  |  |
| --- | --- |

#### 工具头霍尔排查

##### 检测指引

打开工具头前盖，拔掉连接插头并取下前盖组件； 使用扳手逆时针拧松气动接头，取下右侧进料管。

|  |  |
| --- | --- |

插入耗材，同时观察打印机屏幕的耗材显示状态：

- 如果屏幕显示有料，则传感器正常；
- 如果屏幕显示无料，则可能是传感器异常导致误报，请执行后续排查步骤。

|  |  |
| --- | --- |

##### 拆装指引

参考[更换 X2D 工具头外壳](https://wiki.bambulab.com/zh/x2d/maintenance/replace-toolhead-housing)，小心移除工具头前盖和中框；手动拨动切料拨杆组件，使辅助热端下降。

|  |  |
| --- | --- |

移除右切料组件的固定螺丝，将拨杆向外旋转。

|  |  |
| --- | --- |

##### 排障指引

插入一小段耗材，观察摇臂动作是否顺畅，并确认取出耗材后摇臂能否自动复位。

- 如果摇臂异常，卡住耗材或回弹卡涩，需检查摇臂转轴是否存在异物，并将其清理干净。
- 如果摇臂正常，则霍尔传感器故障，请参考[更换 X2D 挤出机配件](https://wiki.bambulab.com/zh/x2d/maintenance/replace-extruder-components)，更换右霍尔检测板。

|  |  |
| --- | --- |

#### 检测指引

打开工具头前壳组件，按压料管支架，移除料管。

|  |  |
| --- | --- |
|  |  |

使用一段耗材尝试手动送料。

![手动送料x1.jpg](https://wiki.bambulab.com/x1/troubleshooting/filament-sensor-test/%E6%89%8B%E5%8A%A8%E9%80%81%E6%96%99x1.jpg)

点击屏幕上的**控制**图标，观察小绿点处。

![控制.jpg](https://wiki.bambulab.com/x1/troubleshooting/filament-sensor-test/%E6%8E%A7%E5%88%B6.jpg)

P1 系列则需要在**电脑或手机**端观察箭头指向位置中间的绿点。

![](https://wiki.bambulab.com/p1/pixpin_2025-05-27_12-04-43.png)

插入耗材后，观察挤出机图标是否出现小绿点；然后取出耗材，观察挤出机图标是否出现小白点。

![gif.webp](https://wiki.bambulab.com/x1/troubleshooting/filament-sensor-test/gif.webp)

如果绿色、白色显示都正常，则霍尔传感器正常。若不正常，请参考以下方法进行排障。

#### 拆卸指引

断开热端加热器、热端风扇和 NTC 电阻连接线，露出霍尔开关板连接线接口。用电吹风加热硅胶，然后断开连接线。

|  |  |
| --- | --- |
|  |  |

> **注意**：P1 系列和 X1E 接口示意图如下：1. 霍尔开关板；2.热端风扇；3.热端加热器   ![](https://wiki.bambulab.com/x1/troubleshooting/filament-sensor-test/p1--.jpg)
> 
> P1 ![](https://wiki.bambulab.com/x1/troubleshooting/filament-sensor-test/x1e-.jpg)
> 
> X1E

用 H1.5 内六角扳手拧松切刀柄螺丝，使刀柄下垂。

|  |  |
| --- | --- |
|  |  |

用 H1.5 内六角扳手移除 2 颗螺丝，将内六角扳手伸入气动接口将组件撬松，然后取下霍尔开关板组件。

|  |  |  |
| --- | --- | --- |
|  |  |  |

#### 排障指引

检查霍尔内部是否有残留的耗材卡住

![检查x1-.jpg](https://wiki.bambulab.com/x1/troubleshooting/filament-sensor-test/%E6%A3%80%E6%9F%A5x1-.jpg)

用 H1.5 内六角扳手移除霍尔板上的 2 颗螺丝。

![移除螺丝-.jpg](https://wiki.bambulab.com/x1/troubleshooting/filament-sensor-test/%E7%A7%BB%E9%99%A4%E8%9E%BA%E4%B8%9D-.jpg)

插入一段耗材，观察摇臂是否正常运作，取出耗材后是否会自动归位。

|  |  |
| --- | --- |
|  |  |

如果摇臂卡住，将摇臂左右移动，即可归位。

#### 组装指引

用 H1.5 内六角扳手安装霍尔板上的 2 颗螺丝。

![安装螺丝.jpg](https://wiki.bambulab.com/x1/troubleshooting/filament-sensor-test/%E5%AE%89%E8%A3%85%E8%9E%BA%E4%B8%9D.jpg)

按压霍尔开关板组件上的气动接头，将开关板组件安装到位，然后锁入 2 颗螺丝进行固定。

|  |  |
| --- | --- |
|  |  |

连接霍尔开关板电缆，建议对这个连接器使用硅胶进行加固。然后依次连接热端 NTC 电缆、热端风扇和热端加热器，并对齐连接器。

|  |  |
| --- | --- |
|  |  |

> **注意**：P1 系列和 X1E 接口示意图如下：1. 霍尔开关板；2.热端风扇；3.热端加热器   ![](https://wiki.bambulab.com/x1/troubleshooting/filament-sensor-test/p1--.jpg)
> 
> P1 ![](https://wiki.bambulab.com/x1/troubleshooting/filament-sensor-test/x1e-.jpg)
> 
> X1E

将料管接入气动接头，然后用手扶起切片刀柄，将切刀滑入刀槽内，拧紧切刀柄螺丝，然后盖上前盖。

|  |  |
| --- | --- |
|  |  |

#### 检测指引

从五通组件上拆下一根料管。

![拆下一根料管.jpg](https://wiki.bambulab.com/x1/troubleshooting/filament-sensor-test/%E6%8B%86%E4%B8%8B%E4%B8%80%E6%A0%B9%E6%96%99%E7%AE%A1.jpg)

使用一段耗材尝试手动送料。

![捅一段料.jpg](https://wiki.bambulab.com/x1/troubleshooting/filament-sensor-test/%E6%8D%85%E4%B8%80%E6%AE%B5%E6%96%99.jpg)

点击打印机屏幕上的**耗材**，观察小绿点处。

|  |  |
| --- | --- |
|  |  |

插入耗材后，观察挤出机图标是否出现小绿点；然后取出耗材，观察挤出机图标是否出现小白点。

![观察小绿点.webp](https://wiki.bambulab.com/x1/troubleshooting/filament-sensor-test/%E8%A7%82%E5%AF%9F%E5%B0%8F%E7%BB%BF%E7%82%B9.webp)

如果绿色、白色显示都正常，则霍尔传感器正常。若不正常，请参考以下方法进行排障。

#### 拆卸指引

用扳手轻微撬起五通的盖子，将五通组件取下。

> **注意**：进料霍尔板底座处涂布有阻尼脂，可能会有些粘手，请在操作时小心。

|  |  |
| --- | --- |
|  |  |

用 H2.0 内六角扳手移除五通组件底座顶部的 2 颗螺丝。

![移除螺丝-五通.jpg](https://wiki.bambulab.com/x1/troubleshooting/filament-sensor-test/%E7%A7%BB%E9%99%A4%E8%9E%BA%E4%B8%9D-%E4%BA%94%E9%80%9A.jpg)

取出五通组件底座。

> 注意：请勿用力取出，避免损坏排线。

|  |  |
| --- | --- |
|  |  |

#### 排障指引

检查霍尔内部是否有残留的耗材卡住

![出料的地方是否有磨损和缺口.jpg](https://wiki.bambulab.com/a1/maintenance/filament-hub-cleaning/%E5%87%BA%E6%96%99%E7%9A%84%E5%9C%B0%E6%96%B9%E6%98%AF%E5%90%A6%E6%9C%89%E7%A3%A8%E6%8D%9F%E5%92%8C%E7%BC%BA%E5%8F%A3.jpg)

用 H1.5 内六角扳手移除霍尔板上的 2 颗螺丝。

![五通螺丝.jpg](https://wiki.bambulab.com/x1/troubleshooting/filament-sensor-test/%E4%BA%94%E9%80%9A%E8%9E%BA%E4%B8%9D.jpg)

插入一段耗材，观察摇臂是否正常运作，取出耗材后是否会自动归位。

|  |  |
| --- | --- |
|  |  |

如果摇臂卡住，将摇臂左右移动，即可归位。

![磁铁归位.jpg](https://wiki.bambulab.com/x1/troubleshooting/filament-sensor-test/%E7%A3%81%E9%93%81%E5%BD%92%E4%BD%8D.jpg)

#### 组装指引

用 H1.5 内六角扳手安装霍尔板上的 2 颗螺丝。

![五通螺丝.jpg](https://wiki.bambulab.com/x1/troubleshooting/filament-sensor-test/%E4%BA%94%E9%80%9A%E8%9E%BA%E4%B8%9D.jpg)

将五通组件底座放回，用 H2.0 内六角扳手安装底座顶部的两颗螺丝。

![拧紧螺丝.jpg](https://wiki.bambulab.com/x1/troubleshooting/filament-sensor-test/%E6%8B%A7%E7%B4%A7%E8%9E%BA%E4%B8%9D.jpg)

将五通组件安装到底座上，对齐安装卡扣，下压五通主体，锁定五通组件。

|  |  |
| --- | --- |
|  |  |



## 媒体资源

- img: https://wiki.bambulab.com/x1/troubleshooting/filament-sensor-test/a2l_(3).jpg
- img: https://wiki.bambulab.com/x1/troubleshooting/filament-sensor-test/a2l_(4).jpg
- img: https://wiki.bambulab.com/x1/troubleshooting/filament-sensor-test/a2l_(5).jpg
- img: https://wiki.bambulab.com/x1/troubleshooting/filament-sensor-test/a2l_(6).jpg
- img: https://wiki.bambulab.com/x1/troubleshooting/filament-sensor-test/a2l_(7).jpg
- img: https://wiki.bambulab.com/x1/troubleshooting/filament-sensor-test/a2l_(8).jpg
- img: https://wiki.bambulab.com/x1/troubleshooting/filament-sensor-test/a2l_(9).jpg
- img: https://wiki.bambulab.com/x1/troubleshooting/filament-sensor-test/a2l_(10).jpg
- img: https://wiki.bambulab.com/x1/troubleshooting/filament-sensor-test/a2l_(1).jpg
- img: https://wiki.bambulab.com/x1/troubleshooting/filament-sensor-test/a2l_(1).webp
- img: https://wiki.bambulab.com/x1/troubleshooting/filament-sensor-test/a2l_(2).jpg
- img: https://wiki.bambulab.com/h2/troubleshooting/filament-sensor/remove_front_fan.gif
- img: https://wiki.bambulab.com/h2/troubleshooting/filament-sensor/remove_ptfe_tubes.gif
- img: https://wiki.bambulab.com/h2/troubleshooting/filament-sensor/filament_sensor_check.gif
- img: https://wiki.bambulab.com/x1/troubleshooting/filament-sensor-test/h2halltest.png
- img: https://wiki.bambulab.com/h2/troubleshooting/filament-sensor/filament_sensor_h2_series.png
- img: https://wiki.bambulab.com/h2/troubleshooting/hmscode/07fe_2000_0002_0002/waswbix1foamiqx8w2wcx8wdncc.webp
- img: https://wiki.bambulab.com/x1/troubleshooting/filament-sensor-test/remove_the_toolhead_front_cover.jpg
- img: https://wiki.bambulab.com/x1/troubleshooting/filament-sensor-test/remove_the_toolhead_front_cover_cable.webp
- img: https://wiki.bambulab.com/x1/troubleshooting/filament-sensor-test/remove_tube.jpg
- img: https://wiki.bambulab.com/x1/troubleshooting/filament-sensor-test/p2s_screen_2.jpg
- img: https://wiki.bambulab.com/x1/troubleshooting/filament-sensor-test/p2s_screen_1.jpg
- img: https://wiki.bambulab.com/x1/troubleshooting/filament-sensor-test/insert_filament.jpg
- img: https://wiki.bambulab.com/x1/troubleshooting/filament-sensor-test/checkinstall_filament_sensor.webp
- img: https://public-cdn.bblmw.com/wiki/new/p2s/maintenance/extruder_unit/toolhead_housing_001.png
- img: https://wiki.bambulab.com/x1/troubleshooting/filament-sensor-test/remove_extruder_filament_sensor_cable.webp
- img: https://wiki.bambulab.com/x1/troubleshooting/filament-sensor-test/remove_2_screws.jpg
- img: https://wiki.bambulab.com/x1/troubleshooting/filament-sensor-test/remove_extruder_filament_sensor.webp
- img: https://wiki.bambulab.com/x1/troubleshooting/filament-sensor-test/inspect_the_arm.webp
- img: https://wiki.bambulab.com/x1/troubleshooting/filament-sensor-test/install_extruder_filament_sensor_cable.jpg
- img: https://wiki.bambulab.com/x1/troubleshooting/filament-sensor-test/install_extruder_filament_sensor_cover.webp
- img: https://wiki.bambulab.com/x1/troubleshooting/filament-sensor-test/install_tube.jpg
- img: https://wiki.bambulab.com/x1/troubleshooting/filament-sensor-test/install_the_toolhead_front_cover_cable.png
- img: https://public-cdn.bblmw.com/wiki/new/x2d/filament-sensor-test/016.jpg
- img: https://public-cdn.bblmw.com/wiki/new/x2d/filament-sensor-test/003.jpg
- img: https://public-cdn.bblmw.com/wiki/new/x2d/filament-sensor-test/023.webp
- img: https://public-cdn.bblmw.com/wiki/new/x2d/filament-sensor-test/010.png
- img: https://public-cdn.bblmw.com/wiki/new/x2d/filament-sensor-test/009.png
- img: https://public-cdn.bblmw.com/wiki/new/x2d/filament-sensor-test/011.png
- img: https://public-cdn.bblmw.com/wiki/new/x2d/filament-sensor-test/018.webp
- img: https://public-cdn.bblmw.com/wiki/new/x2d/filament-sensor-test/004.jpg
- img: https://public-cdn.bblmw.com/wiki/new/x2d/filament-sensor-test/015.png
- img: https://public-cdn.bblmw.com/wiki/new/x2d/filament-sensor-test/005.png
- img: https://public-cdn.bblmw.com/wiki/new/x2d/filament-sensor-test/007.png
- img: https://public-cdn.bblmw.com/wiki/new/x2d/filament-sensor-test/001.webp
- img: https://public-cdn.bblmw.com/wiki/new/x2d/filament-sensor-test/008.png
- img: https://public-cdn.bblmw.com/wiki/new/x2d/filament-sensor-test/020.webp
- img: https://public-cdn.bblmw.com/wiki/new/x2d/filament-sensor-test/017.jpg
- img: https://public-cdn.bblmw.com/wiki/new/x2d/filament-sensor-test/012.png
- img: https://public-cdn.bblmw.com/wiki/new/x2d/filament-sensor-test/auxiliary-hotend.jpg
- img: https://public-cdn.bblmw.com/wiki/new/x2d/filament-sensor-test/013.png
- img: https://public-cdn.bblmw.com/wiki/new/x2d/filament-sensor-test/024.webp
- img: https://public-cdn.bblmw.com/wiki/new/x2d/filament-sensor-test/019.webp
- img: https://public-cdn.bblmw.com/wiki/new/x2d/filament-sensor-test/014.png
- img: https://public-cdn.bblmw.com/wiki/new/x2d/filament-sensor-test/021.webp
- img: https://public-cdn.bblmw.com/wiki/new/x2d/filament-sensor-test/006.png
- img: https://public-cdn.bblmw.com/wiki/new/x2d/filament-sensor-test/002.webp
- img: https://wiki.bambulab.com/x1/maintenance/replace-front-housing-assembly/377px-remove_the_front_housing_assembly.png
- img: https://wiki.bambulab.com/x1/maintenance/replace-extru-sw-assembly/tube_and_lever.jpg
- img: https://wiki.bambulab.com/x1/troubleshooting/filament-sensor-test/%E6%89%8B%E5%8A%A8%E9%80%81%E6%96%99x1.jpg
- img: https://wiki.bambulab.com/x1/troubleshooting/filament-sensor-test/%E6%8E%A7%E5%88%B6.jpg
- img: https://wiki.bambulab.com/p1/pixpin_2025-05-27_12-04-43.png
- img: https://wiki.bambulab.com/x1/troubleshooting/filament-sensor-test/gif.webp
- img: https://wiki.bambulab.com/x1/maintenance/replace-extru-sw-assembly/disconnect_the_hotend_cables.jpg
- img: https://wiki.bambulab.com/x1/maintenance/replace-extru-sw-assembly/disconnect_the_hall_cable.jpg
- img: https://wiki.bambulab.com/x1/troubleshooting/filament-sensor-test/p1--.jpg
- img: https://wiki.bambulab.com/x1/troubleshooting/filament-sensor-test/x1e-.jpg
- img: https://wiki.bambulab.com/x1/troubleshooting/filament-sensor-test/%E5%88%87%E5%88%80%E8%9E%BA%E4%B8%9D.png
- img: https://wiki.bambulab.com/x1/troubleshooting/filament-sensor-test/%E5%88%87%E5%88%80%E4%B8%8B%E5%9E%82.png
- img: https://wiki.bambulab.com/x1/maintenance/replace-extru-sw-assembly/2_screws.jpg
- img: https://wiki.bambulab.com/x1/maintenance/replace-extru-sw-assembly/loose_the_assembly.jpg
- img: https://wiki.bambulab.com/x1/maintenance/replace-extru-sw-assembly/remove_the_assembly.jpg
- img: https://wiki.bambulab.com/x1/troubleshooting/filament-sensor-test/%E6%A3%80%E6%9F%A5x1-.jpg
- img: https://wiki.bambulab.com/x1/troubleshooting/filament-sensor-test/%E7%A7%BB%E9%99%A4%E8%9E%BA%E4%B8%9D-.jpg
- img: https://wiki.bambulab.com/x1/troubleshooting/filament-sensor-test/%E8%A7%82%E5%AF%9F%E6%91%87%E8%87%82.jpg
- img: https://wiki.bambulab.com/x1/troubleshooting/filament-sensor-test/%E6%91%87%E8%87%82x1.webp
- img: https://wiki.bambulab.com/x1/troubleshooting/filament-sensor-test/%E5%AE%89%E8%A3%85%E8%9E%BA%E4%B8%9D.jpg
- img: https://wiki.bambulab.com/x1/maintenance/replace-extru-sw-assembly/install_assembly.jpg
- img: https://wiki.bambulab.com/x1/maintenance/replace-extru-sw-assembly/install_assembly_2.jpg
- img: https://wiki.bambulab.com/x1/maintenance/replace-extru-sw-assembly/disconnect_the_hotend_cables_2.jpg
- img: https://wiki.bambulab.com/x1/maintenance/replace-extru-sw-assembly/insert_the_tube_and_fix_the_lever.jpg
- img: https://wiki.bambulab.com/x1/maintenance/replace-extru-sw-assembly/close_the_housing.jpg
- img: https://wiki.bambulab.com/x1/troubleshooting/filament-sensor-test/%E6%8B%86%E4%B8%8B%E4%B8%80%E6%A0%B9%E6%96%99%E7%AE%A1.jpg
- img: https://wiki.bambulab.com/x1/troubleshooting/filament-sensor-test/%E6%8D%85%E4%B8%80%E6%AE%B5%E6%96%99.jpg
- img: https://wiki.bambulab.com/a1/maintenance/filament-hub-cleaning/%E7%82%B9%E5%87%BB%E5%B1%8F%E5%B9%95%E8%80%97%E6%9D%90.jpg
- img: https://wiki.bambulab.com/x1/troubleshooting/filament-sensor-test/%E5%B0%8F%E7%BB%BF%E7%82%B9.jpg
- img: https://wiki.bambulab.com/x1/troubleshooting/filament-sensor-test/%E8%A7%82%E5%AF%9F%E5%B0%8F%E7%BB%BF%E7%82%B9.webp
- img: https://wiki.bambulab.com/x1/troubleshooting/filament-sensor-test/%E6%92%AC%E8%B5%B7%E7%9B%96%E5%AD%90.jpg
- img: https://wiki.bambulab.com/x1/troubleshooting/filament-sensor-test/%E5%8F%96%E4%B8%8B%E4%BA%94%E9%80%9A%E7%BB%84%E4%BB%B6.jpg
- img: https://wiki.bambulab.com/x1/troubleshooting/filament-sensor-test/%E7%A7%BB%E9%99%A4%E8%9E%BA%E4%B8%9D-%E4%BA%94%E9%80%9A.jpg
- img: https://wiki.bambulab.com/x1/troubleshooting/filament-sensor-test/%E5%8F%96%E5%87%BA%E5%BA%95%E5%BA%A7.jpg
- img: https://wiki.bambulab.com/x1/troubleshooting/filament-sensor-test/%E6%B3%A8%E6%84%8F%E6%8E%92%E7%BA%BF.jpg
- img: https://wiki.bambulab.com/a1/maintenance/filament-hub-cleaning/%E5%87%BA%E6%96%99%E7%9A%84%E5%9C%B0%E6%96%B9%E6%98%AF%E5%90%A6%E6%9C%89%E7%A3%A8%E6%8D%9F%E5%92%8C%E7%BC%BA%E5%8F%A3.jpg
- img: https://wiki.bambulab.com/x1/troubleshooting/filament-sensor-test/%E4%BA%94%E9%80%9A%E8%9E%BA%E4%B8%9D.jpg
- img: https://wiki.bambulab.com/a1/maintenance/filament-hub-cleaning/%E8%A7%82%E5%AF%9F%E6%AD%A4%E5%A4%84.jpg
- img: https://wiki.bambulab.com/a1/maintenance/filament-hub-cleaning/%E6%8D%85%E4%B8%80%E6%AE%B5%E6%96%99%E8%BF%9B%E5%8E%BB.webp
- img: https://wiki.bambulab.com/x1/troubleshooting/filament-sensor-test/%E7%A3%81%E9%93%81%E5%BD%92%E4%BD%8D.jpg
- img: https://wiki.bambulab.com/x1/troubleshooting/filament-sensor-test/%E6%8B%A7%E7%B4%A7%E8%9E%BA%E4%B8%9D.jpg
- img: https://wiki.bambulab.com/x1/troubleshooting/filament-sensor-test/%E5%AF%B9%E9%BD%90%E5%8D%A1%E6%89%A3.jpg
- img: https://wiki.bambulab.com/x1/troubleshooting/filament-sensor-test/%E5%90%91%E4%B8%8B%E6%8C%89%E7%B4%A7.jpg

