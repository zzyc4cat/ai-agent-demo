---
source: https://wiki.bambulab.com/zh/x1/troubleshooting/version-ams-main-board
fetched_at: 2026-10-26
title: AMS上下料器升级，如何区分AMS主板的版本
media_count: 8
---

> 来源：https://wiki.bambulab.com/zh/x1/troubleshooting/version-ams-main-board｜抓取日期：2026-10-26｜仅供本地检索演示，版权归原作者

AMS上下料器升级，如何区分AMS主板的版本
AMS上下料升级了，新版本的上下料与早期的AMS主板有兼容性问题，需要同步更换。

---

标签
区分ams主板
最后编辑
Yu Li
05/28/2024
为优化产品性能，我们对AMS上下料器的电路板进行了升级。这个升级会对使用了最早期主板的AMS造成影响，会在这些AMS更换新版上下料器（或入料口组件）后，因兼容性问题而无法正常使用上下料器（或入料口组件）。这部分AMS约有2000台，且绝大部份是在参加KS的用户手上，但也不能绝对排除有很小部分会流到普通用户手里的可能性。对于这部分AMS，如果其所有者购买了新版的AMS上下料器（或入料口组件），请联系拓竹服务团队，我们将免费为您寄送一块新的AMS主板，以保证您们能正常使用。下面的内容我们将向您说明如何区分AMS主板的版本、如何申请新的主板以及我们的一些处置方案。

开关版本（旧版）的上下料或者入料口组件，已经停售，客户从官方商城只能买到霍尔版本（新版）的上下料和入料口组件。

如果您在2023年1月1日之后通过官方电商平台（京东、天猫、抖音）购买AMS，您的AMS主板将是最新版本的，因此您无需担心AMS上下料器的兼容性问题。

如果您在2022年10月1日至2023年1月1日期间通过官方电商平台（京东、天猫、抖音）购买AMS，那么您的AMS主板很可能是新版本的。如果您不确定，可以按照以下方法检查AMS主板的版本，以免出现AMS上下料器不兼容的问题。

如果您在2022年10月1日之前通过官方电商平台（京东、天猫、抖音）购买AMS，请务必按照下面的方法进行检查，如果确定AMS主板是旧版本，可以联系售后团队寻求帮助。

### 1. AMS主板版本说明

可以通过检查以下红色方框内R151位置处的元器件的外观确认AMS主板版本。

![](https://wiki.bambulab.com/x1/troubleshooting/ams-first-feeder-upgraded/check_the_version.png)

| 旧主板 | 新主板 |
| --- | --- |

如上图所示，R151位置处的元器件，印有数字的是电阻版（旧主板），黑色无数字的是磁珠版（新主板）。下表是AMS上下料(或入料口组件)与主板的版本兼容性关系：

| 上下料与主板的版本兼容性 | R151 电阻 主板（旧） | R151 磁珠主板（新） |
| --- | --- | --- |
| 开关版上下料（旧） | OK | OK |
| 霍尔版上下料（新） | NO | OK |

这个关系表表明：

（1）用户在购买或更换新版的上下料器或入料口组件，需要先确认AMS主板的版本；

（2）如果用户的AMS使用的是R151电阻主板，需要同步向拓竹服务团队申请更换AMS主板；

（3）如果用户的AMS使用的是R151磁珠主板，可以正常使用，无需更换AMS主板。

### 2. AMS主板版本确认指引

#### （1）断开AMS连接，拆下料管；

断开AMS连接的情况下，按压AMS 五通组件上的按钮，从AMS背面拔出料管；

![](https://wiki.bambulab.com/x1/troubleshooting/ams-first-feeder-upgraded/remove_the_tube.png)

#### （2）松出AMS主框架

用H2.0内六角扳手移除2颗螺丝，然后将AMS主框架松出，注意避让五通按键。

|  |  |
| --- | --- |

#### （3）断开连接线，取出主框架，检查主板版本

断开AMS电源板上的2条连接电缆，取出主框架，根据主板R151位置元器件的外观确认主板版本。

|  |  |
| --- | --- |

#### （4）拍摄照片，提交服务工单

如果确认AMS主板是R151电阻版，请参照下图拍摄一张照片，要求AMS主板二维码要清晰，且能看清楚R151位置处的元器件是否带数字，然后提交服务工单，上传拍摄的照片并提供购买上下料器（或入料口组件）的订单号，等待拓竹服务团队处理即可。

提醒：我们会保留主板更换记录，重复申请的情况将会被拒绝。

![](https://wiki.bambulab.com/x1/troubleshooting/ams-first-feeder-upgraded/sample_2.png)

## 媒体资源

- img: https://wiki.bambulab.com/x1/troubleshooting/ams-first-feeder-upgraded/check_the_version.png
- img: https://wiki.bambulab.com/x1/troubleshooting/ams-first-feeder-upgraded/switch_version.png
- img: https://wiki.bambulab.com/x1/troubleshooting/ams-first-feeder-upgraded/haul_version.png
- img: https://wiki.bambulab.com/x1/troubleshooting/ams-first-feeder-upgraded/remove_the_tube.png
- img: https://wiki.bambulab.com/x1/troubleshooting/ams-first-feeder-upgraded/2_screws_2.jpg
- img: https://wiki.bambulab.com/x1/troubleshooting/ams-first-feeder-upgraded/lift_the_main_frame.png
- img: https://wiki.bambulab.com/x1/troubleshooting/ams-first-feeder-upgraded/disconnect_the_2_cables.png
- img: https://wiki.bambulab.com/x1/troubleshooting/ams-first-feeder-upgraded/sample_2.png

