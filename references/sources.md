# 飞书来源

每次读取当前内容。下列链接是入口，不是固定的上新清单。

| 类别 | 来源 | 取材方式 |
|---|---|---|
| 音乐 | https://hcnt3t130lav.feishu.cn/wiki/WLIQwIlupiPJDRkL1amckXYinNB | 按英文或中文名称定位作品章节，读取原封面、成品、介绍、时长及提示词 |
| 睡眠播客 | https://hcnt3t130lav.feishu.cn/wiki/VXIFwzvv1iuyHOkNiqvcRMWonod | 定位指定播客的作品节点及其成品、封面、详细脚本，内容可能分散在子节点 |
| 音频源标注 | https://hcnt3t130lav.feishu.cn/wiki/UeCpwYP5kiyTbckFaaKcIPxdnXg | 补充正式中英文名称、简介、声音元素和时长等字段；只读，不在通知任务中改写标注 |

## 读取与定位

先按名称定位，必要时查看目录后读取完整章节：

```text
lark-cli docs +fetch --doc <类别资料库URL> --scope keyword --keyword <作品名> --detail with-ids --as user
lark-cli docs +fetch --doc <文档URL> --scope outline --max-depth 3 --as user
lark-cli docs +fetch --doc <文档URL> --scope section --start-block-id <标题块ID> --detail full --as user
```

正文中的 `reference_map` 与内容是一组数据，图片和附件的临时引用需在其中解析。局部返回的 `excerpt` 不表示完整章节，需按 `top-block-id` 扩展读取。

如果播客库正文只提供导航，读取其子节点：

```text
lark-cli wiki +node-get --node-token <播客库URL> --as user
lark-cli wiki +node-list --space-id <返回的数字space_id> --parent-node-token <返回的node_token> --as user
```

有 `has_more` 时续页，进入匹配的作品或脚本节点。只读取本次作品所需的节点。目录中的成品文档和脚本文档分别回答“在哪里试听”与“故事讲什么”，不能用脚本链接代替成品入口。

下载已定位的原封面：

```text
lark-cli docs +media-download --token <封面资源token> --output ./covers/作品文件名.png --as user
```

命令从本次任务目录运行，CLI 路径参数使用目录内相对路径。保存真实扩展名；如果实际返回 JPEG，不将扩展名伪装成 PNG。文档读取与资源下载失败时按 CLI 的具体提示处理，不以网页截图或别的作品封面顶替。

## 取材判断

音乐的提示词用来帮助理解乐器、音色和氛围，不是需要读者学习的内容。播客的详细脚本帮助提炼场景、动作和聆听意象；遵循当前成品的实际语言、声线与时长。若男女声共用一集入口，作为一个播客项目呈现；只有用户明确把两个版本列为不同上新项目时才拆分。

一旦找到作品，记录对应 `source_url` 和 `listen_url`。已有分享锚点保留原链接；通过块 ID 定位时使用工具返回的链接或其文档直达格式，不猜测不存在的锚点。资料源访问受当前账号权限控制。
