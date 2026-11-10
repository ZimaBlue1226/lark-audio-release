# lark-audio-release

[English](./README.md) | [中文版](./README.zh.md)

A Codex / agent skill for announcing new **Veliso Sleep Music and SleepCast** releases in Feishu.

Tell the agent which audio works are new. It reads the corresponding Feishu sources, creates posters and clickable listening links, and sends the finished message to your own Feishu account. You review it and manually share it with the group.

Music, sleep podcasts, and mixed batches are supported. The number of works can vary each time.

## Poster preview

![Three music releases in the approved full-bleed layout](./assets/reference.png)

Covers fill the canvas without gaps. Each work shows its number and type, English title, Chinese title, duration, Chinese introduction, and sound or scene tags. Listening links stay in the Feishu text below the images so people can click them.

The preview illustrates the layout. Each run uses the selected works and their original covers.

## Who reads what

| File | Audience | Purpose |
|---|---|---|
| `README.md` / `README.zh.md` | Humans | Installation, usage, dependencies, and package notes. |
| `SKILL.md` | Agent | Source lookup, editorial rules, rendering, and delivery workflow. |
| `references/sources.md` | Agent | Separate Feishu sources for music, podcasts, and audio metadata. |
| `references/rendering.md` | Agent | Input schema, typography, layout, and image checks. |
| `references/delivery.md` | Agent | Recipient verification, image upload, and private-message delivery. |
| `scripts/render.py` | Agent-executable helper | Renders local posters and prepares listening-link content. |
| `assets/` | Renderer | HTML/CSS template, fonts, and layout reference. |
| `agents/openai.yaml` | Codex UI | Display name, description, and default prompt. |

The repository root is the skill package itself. The skill name, repository name, and installation directory are all `lark-audio-release`.

## Workflow

1. Take the names or Feishu links supplied for this release, keeping the requested order.
2. Verify the initiating user's Feishu identity. The recipient is the current user, never a fixed producer or group.
3. Read each work's source. Music uses its cover, metadata, and generation notes; podcasts use their cover, metadata, and detailed script.
4. Prepare concise Chinese introductions and tags, then render posters using the bundled template and fonts.
5. Inspect the images and rendering reports, and prepare one clickable listening link per work.
6. Send the images and links to the initiating user's Feishu private chat and verify delivery.

The AI's work ends at private delivery. Group publishing remains a manual action. A request for a local preview only stops before sending.

## Requirements

- An agent environment that supports local Skills, shell commands, and image inspection.
- Python 3.10+. The renderer uses only the Python standard library.
- Chrome, Chromium, or Microsoft Edge for local PNG rendering.
- An installed and configured `lark-cli`, with a verified user login for reading sources and identifying the recipient, plus a bot identity that can upload images and send private messages.
- The `lark-shared`, `lark-doc`, and `lark-im` skills, plus `lark-wiki` when needed. The agent can also read their instructions through `lark-cli skills read <skill-name>`.
- Read access to the Feishu documents and media used in the release.

This public repository includes the configured Veliso source locations. Repository access does not grant access to the Feishu content. Credentials and recipient IDs are not bundled.

## Install

```bash
npx skills add https://github.com/ZimaBlue1226/lark-audio-release
```

For manual installation, clone this repository and place the complete `lark-audio-release/` directory under your agent's skills directory, such as `~/.codex/skills/`. Keep `SKILL.md`, `agents/`, `references/`, `scripts/`, and `assets/` together. The fonts load from local files and do not need to be installed system-wide.

## Usage

Invoke the skill with a list of the new works, using names, Feishu links, or both:

```text
Use $lark-audio-release for this week's new audio:
- Music: Soft White Cloud
- Music: Little Drop's Day
- SleepCast: The Late Autumn Orchard

Make the posters and listening-link message, then send them to my Feishu.
```

You can also specify a release date or ask for a local preview only. There is no fixed requirement to supply three works or to publish every week.

You do not need to prepare JSON yourself. The agent gathers the source material and creates the renderer input.

## Output

Each run writes its files to a separate task directory:

| File | Purpose |
|---|---|
| `poster-01.png`, … | Images ready for Feishu. |
| `poster-01.html`, CSS, covers, and fonts | Local files for reproducing or adjusting the render. |
| `release-message.md` | Listening links in the same order as the posters. |
| `links-post.json` | Feishu rich-text link content. |
| `manifest.json` | Page dimensions, work order, source links, and rendering checks. |

The message uses labels such as `试听《Soft White Cloud》柔和的白云`. Descriptions stay on the posters.

Canvas size adapts to the content. Up to six works fit on one image; larger batches are split into multiple images while preserving order and numbering. A three-work poster defaults to 1740 × 1480 px. Width and height can increase to accommodate longer titles.

## Local rendering

To render separately from Feishu, prepare an input file using [the rendering reference](./references/rendering.md), then run this from the repository root:

```bash
python scripts/render.py --input /path/to/release.json --output /path/to/new-output
```

Use `--chrome /path/to/browser` if the browser is not detected automatically. Choose a fresh output directory for each render.

The script renders local files and prepares link content. The agent performs source retrieval and Feishu delivery through `lark-cli`.

## Customizing

Edit [the source map](./references/sources.md) to use another team's Feishu libraries. Edit [the rendering reference](./references/rendering.md) and `assets/poster.html` / `assets/poster.css` together when changing the design. Keep workflow and recipient rules in `SKILL.md` and [the delivery reference](./references/delivery.md).

PingFang SC Regular, Medium, and Semibold, plus Noto Sans SC, are bundled with the template. Font copyright and license information is in [the font notices](./assets/fonts/NOTICE.md).
