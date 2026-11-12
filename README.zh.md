# lark-audio-release

[English](./README.md) | [中文版](./README.zh.md)

用于 **Veliso 音乐与睡眠播客上新通知**的 Codex / Agent Skill。

告诉 AI 本次新增了哪些音频，它会读取对应的飞书资料，生成海报和可点击的试听文案，再把完整消息私信发到发起人自己的飞书。发起人检查后，手动转发或复制到群里。

支持纯音乐、纯睡眠播客和混合清单，每次数量可以不同。

## 海报预览

![三首音乐的无缝铺满版式](./assets/reference.png)

封面直接铺满画布，图片之间不留空隙，保持原图亮度，不叠加遮罩。每件作品依次展示序号 / 音频类型、英文标题、中文标题、时长、中文简介、音色或场景标签。顶部副标题从作品数量接到「戴上耳机」提示。

预览图用于说明版式。实际生成时使用本次指定作品及其原始封面。

## 文件分工

| 文件 | 面向谁 | 用途 |
|---|---|---|
| `README.md` / `README.zh.md` | 使用者 | 安装、使用、依赖和包说明。 |
| `SKILL.md` | AI | 资料读取、内容提炼、海报生成和私信交付流程。 |
| `references/sources.md` | AI | 音乐、播客与音频标注的飞书来源。 |
| `references/rendering.md` | AI | 输入格式、字体、版式与图片检查。 |
| `references/delivery.md` | AI | 发起人身份核对、图片上传与私信发送。 |
| `scripts/render.py` | AI 执行的辅助脚本 | 本地渲染海报并准备试听链接文案。 |
| `assets/` | 渲染器 | HTML/CSS 模板、字体与版式参考图。 |
| `agents/openai.yaml` | Codex 界面 | 显示名称、简介与默认提示词。 |

仓库根目录就是 Skill 包。Skill 名称、仓库名称和安装目录统一为 `lark-audio-release`。

## 工作流程

1. 接收本次新增作品的名称或飞书链接，保持用户指定的顺序。
2. 核对发起人的飞书身份，接收人使用当前用户，不固定为某位制作人或某个群。
3. 按类别读取资料。音乐读取封面、元信息和生成提示词；播客读取封面、元信息及详细脚本。
4. 提炼中文短简介与标签，用包内模板和字体生成海报。
5. 检查图片及渲染报告，为每件作品准备可点击的试听入口，并在链接后附上制作人。
6. 将图片与试听文案私信发给发起人，并确认消息已送达。

AI 的工作到私信交付结束，群内发布由本人手动完成。明确只要本地预览时，不执行发送。

## 环境要求

- 支持本地 Skill、命令执行和图片查看的 Agent 环境。
- Python 3.10+，渲染器只使用 Python 标准库。
- Chrome、Chromium 或 Microsoft Edge，用于本地生成 PNG。
- 已安装并配置的 `lark-cli`。用户身份需通过验证，用于读取资料及确定接收人；机器人身份需能上传图片和发送私信。
- `lark-shared`、`lark-doc`、`lark-im`，以及需要时使用的 `lark-wiki` Skill。AI 也可通过 `lark-cli skills read <skill-name>` 读取相应说明。
- 本次作品所用飞书文档和素材的读取权限。

公开仓库中预设了 Veliso 的资料入口。能访问仓库不代表拥有飞书资料权限；包内不包含凭证或固定收件人 ID。

## 安装

```bash
npx skills add https://github.com/ZimaBlue1226/lark-audio-release
```

手动安装时，克隆仓库，将完整的 `lark-audio-release/` 目录放到 Agent 的 Skills 目录，例如 `~/.codex/skills/`。保留 `SKILL.md`、`agents/`、`references/`、`scripts/` 和 `assets/` 的完整结构。字体从包内加载，无需安装到系统。

## 使用

调用 Skill，并提供本次新增清单，可以使用作品名、飞书链接或两者混合：

```text
用 $lark-audio-release 做这次音频上新通知：
- 音乐：Soft White Cloud
- 音乐：Little Drop's Day
- 睡眠播客：The Late Autumn Orchard

生成海报和试听文案后，发到我自己的飞书。
```

也可以指定发布日期，或说明“这次只生成本地预览”。作品数量不限，不要求每次三首，也不要求每周固定发布。

使用者不需要手写 JSON。AI 负责读取资料并整理渲染输入。

## 输出内容

每次使用独立的任务目录保存产物：

| 文件 | 用途 |
|---|---|
| `poster-01.png` 等 | 可用于飞书消息的海报图片。 |
| `poster-01.html`、CSS、封面和字体 | 用于重渲染或调整的本地文件。 |
| `release-message.md` | 一句试听邀请，以及与海报顺序一致的链接和制作人署名。 |
| `links-post.json` | 同一份邀请、链接和制作人署名的飞书富文本。 |
| `manifest.json` | 图片尺寸、作品顺序、制作人、资料链接及渲染检查结果。 |

飞书消息先邀请大家试听，再放海报和试听链接。每行格式为 `试听《Soft White Cloud》柔和的白云 · 制作人：姓名`。只有作品名部分可点击，制作人紧跟在链接后面，使用同一行的普通文字。署名来自对应作品资料或用户明确提供的信息；缺少时 AI 会针对该作品询问，不默认把发起人当作制作人。制作人放在文字消息里，海报仍保留原有六层信息。

画布根据内容调整。每张最多六件作品，更多作品按顺序分图并保持连续编号。三件作品默认生成 1740 × 1480 px 海报；遇到长标题可增加宽度或高度。

## 单独运行渲染

如需脱离飞书单独生成海报，按[渲染说明](./references/rendering.md)准备输入文件，在仓库根目录运行：

```bash
python scripts/render.py --input /path/to/release.json --output /path/to/new-output
```

未自动找到浏览器时，通过 `--chrome /path/to/browser` 指定可执行文件。每次渲染使用新的输出目录。

该脚本只负责本地渲染和链接文案生成。资料读取与飞书交付由 AI 调用 `lark-cli` 完成。

## 调整与维护

更换团队资料库时，修改[飞书来源](./references/sources.md)。调整视觉时，同步修改[版式说明](./references/rendering.md)与 `assets/poster.html` / `assets/poster.css`。工作流程与收件人规则维护在 `SKILL.md` 和[交付说明](./references/delivery.md)。

模板附带 PingFang SC Regular、Medium、Semibold 及 Noto Sans SC。字体版权和许可信息见[字体说明](./assets/fonts/NOTICE.md)。
