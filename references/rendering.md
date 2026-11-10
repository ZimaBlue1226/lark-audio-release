# 输入与已确认版式

`release.json` 为 UTF-8 JSON。下例仅示范字段，实际内容取自本次指定作品。

```json
{
  "date": "2026-11-10",
  "heading": "本周新声",
  "items": [
    {
      "type": "music",
      "title_en": "Soft White Cloud",
      "title_zh": "柔和的白云",
      "duration": "31:52",
      "description_zh": "舒缓的键盘声，陪云朵在天空中慢慢舒展开。",
      "tags": ["白噪音", "合成器", "键盘"],
      "cover": "covers/soft-white-cloud.png",
      "cover_position": "60% 50%",
      "source_url": "https://资料文档",
      "listen_url": "https://对应作品试听入口"
    }
  ]
}
```

`type` 为 `music` 或 `podcast`，封面路径相对输入文件。路径由 AI 根据已下载素材填写。`title_lines` 可选，用一至两条原文文本控制英文标题断行，其拼接内容必须仍是原名。默认不手动断行。`heading` 默认“本周新声”。数量、日期和标题没有固定样例值。

可选 `layout` 参数：`column_width` 默认 580，`row_height` 默认 1306。加宽列和增高行用于容纳更长内容，不能缩窄到旧版的狭长封面。单件默认 760 × 1360，二至三件每列 580、高 1480；四件两行两列，五件三列加两列，六件两行三列。默认每张最多六件，更多作品按顺序分图，保持全局序号、全部试听入口和一致字号。缺两件的一排均分画布宽度，不留下空白占位。

## 视觉规范

以 `assets/reference.png` 为已确认三首音乐参考。封面无缝铺满，行列间距均为 0。图片保持原比例裁切，不拉伸；按主体位置调整 `cover_position`。正文左边距 40 px。保留顶部轻遮罩及底部深色遮罩，暖白文字 `#fff4dc`。

| 顺序 | 文字 | 字体与字重 | 尺寸 |
|---|---|---|---|
| 1 | 序号 / 音频类型 | PingFang SC Medium | 22 px，行高 1.5 |
| 2 | 英文标题 | PingFang SC Medium | 48 px，行高 1.12 |
| 3 | 中文标题 | Noto Sans SC Medium | 30 px，行高 1.4 |
| 4 | 时长 | PingFang SC Regular | 26 px，独立一行 |
| 5 | 中文简介 | Noto Sans SC Regular | 26 px，行高 1.55，通常两至三行 |
| 6 | 音色 / 元素标签 | Noto Sans SC Regular | 22 px，两至四个短标签 |

英文名称主导，中文名称紧随其后。时长不要与标签混在一行。同排按实际最高内容对齐英文标题、中文标题、简介和标签。音乐显示 `SLEEP MUSIC`，播客显示 `SLEEPCAST`。

海报顶部副标题把作品数量和「戴上耳机」提示写在同一段里，以逗号衔接，沿用同一字号与样式。

包内 PingFang Regular、Medium、Semibold 来自用户提供的字体目录；中文 Noto Sans SC 同样随模板提供。HTML 通过相对路径加载，无需安装到系统。字体、模板、脚本一起迁移。渲染器会复制所需字体进输出目录，便于 HTML 重渲染。

## 检查与修正

脚本生成 PNG 后返回 `manifest.json`，其中记录每张图片尺寸、作品序号、链接和渲染报告。检查缺图、字体加载、文字溢出与标题占行。三行以上标题先调整合理断行或列宽；描述过长时依据源资料压缩，而不是缩小整张海报。通过检查后再执行飞书交付。

`release-message.md` 和 `links-post.json` 分别以 Markdown 和飞书富文本记录同一句开场邀请和同一组试听链接。组装飞书消息时，在两者之间插入海报。只保留可直接转发给听众的文案。
