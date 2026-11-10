#!/usr/bin/env python3
"""Render the approved audio-release poster with local fonts. No Feishu writes."""
import argparse
import datetime as dt
import json
import os
from pathlib import Path
import re
import shutil
import stat
import subprocess
import sys
import tempfile
from urllib.parse import urlparse

ASSETS = Path(__file__).resolve().parents[1] / 'assets'


def save_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')


def https_url(value):
    u = urlparse(value)
    return u.scheme == 'https' and bool(u.netloc) and not u.username and not u.password


def load_release(path):
    data = json.loads(path.read_text(encoding='utf-8-sig'))
    dt.date.fromisoformat(data['date'])
    if not isinstance(data.get('items'), list) or not data['items']:
        raise ValueError('items 必须是非空作品清单')
    data.setdefault('heading', '本周新声')
    if not isinstance(data['heading'], str) or not data['heading'].strip():
        raise ValueError('heading 不能为空')
    for index, item in enumerate(data['items'], 1):
        if item.get('type') not in ('music', 'podcast'):
            raise ValueError(f'第 {index} 件作品的 type 必须为 music 或 podcast')
        for field in ('title_en', 'title_zh', 'duration', 'description_zh', 'cover', 'source_url', 'listen_url'):
            if not isinstance(item.get(field), str) or not item[field].strip():
                raise ValueError(f'第 {index} 件作品缺少 {field}')
        if not all(https_url(item[k]) for k in ('source_url', 'listen_url')):
            raise ValueError(f'第 {index} 件作品需要有效 HTTPS 资料与试听链接')
        tags = item.get('tags')
        if not isinstance(tags, list) or not 2 <= len(tags) <= 4 or any(not isinstance(t, str) or not t.strip() for t in tags):
            raise ValueError(f'第 {index} 件作品需要两至四个非空标签')
        lines = item.get('title_lines')
        if lines is not None:
            if not isinstance(lines, list) or not 1 <= len(lines) <= 2 or any(not isinstance(s, str) or not s.strip() for s in lines):
                raise ValueError('title_lines 必须是一至两行文本')
            if ' '.join(' '.join(lines).split()) != ' '.join(item['title_en'].split()):
                raise ValueError('title_lines 不得改变完整英文作品名')
        pos = item.get('cover_position', '50% 50%')
        if not re.fullmatch(r'\d{1,3}(?:\.\d+)?% \d{1,3}(?:\.\d+)?%', pos) or any(float(x[:-1]) > 100 for x in pos.split()):
            raise ValueError('cover_position 使用 0% 至 100% 的两个坐标')
        cover = (path.parent / item['cover']).resolve()
        if cover.suffix.lower() not in ('.png', '.jpg', '.jpeg', '.webp') or not cover.is_file():
            raise ValueError(f'封面不是有效的本地图片文件: {item["cover"]}')
        item['_cover_path'] = cover
        item['ordinal'] = index
    layout = data.setdefault('layout', {})
    for key, default, maximum in (('column_width', 580, 2000), ('row_height', 1306, 4000)):
        layout.setdefault(key, default)
        if not isinstance(layout[key], int) or not default <= layout[key] <= maximum:
            raise ValueError(f'{key} 必须为 {default} 至 {maximum} 的整数')
    return data


def split_items(items):
    batches = []
    while items:
        take = 5 if len(items) == 7 else min(6, len(items))
        batches.append(items[:take])
        items = items[take:]
    return batches


def geometry(count, layout):
    col, row = layout['column_width'], layout['row_height']
    if count == 1:
        return max(760, col), max(1360, row), [1]
    if count <= 3:
        return col * count, max(1480, row), [count]
    return col * (2 if count == 4 else 3), row, [2, 2] if count == 4 else [3, count-3]


def chrome_binary(explicit):
    if explicit:
        if not Path(explicit).is_file():
            raise ValueError('--chrome 指定的浏览器不存在')
        return str(Path(explicit).resolve())
    candidates = [shutil.which(n) for n in ('google-chrome', 'chromium', 'chromium-browser', 'chrome', 'msedge')]
    for root in (os.environ.get('PROGRAMFILES'), os.environ.get('PROGRAMFILES(X86)'), os.environ.get('LOCALAPPDATA')):
        if root:
            candidates += [str(Path(root) / 'Google/Chrome/Application/chrome.exe'), str(Path(root) / 'Microsoft/Edge/Application/msedge.exe')]
    candidates += ['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', '/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge']
    for p in candidates:
        if p and Path(p).is_file():
            return p
    raise ValueError('未找到 Chromium 浏览器，使用 --chrome 指定 Chrome / Chromium / Edge')


def remove_profile(profile, output):
    target = profile.resolve()
    if target.parent != output.resolve() or not target.name.startswith('audio-release-chrome-'):
        raise ValueError('拒绝清理意外的临时目录')
    for p in [target, *target.rglob('*')]:
        if p.is_symlink() or getattr(p.lstat(), 'st_file_attributes', 0) & stat.FILE_ATTRIBUTE_REPARSE_POINT:
            raise ValueError('临时目录含链接，保留目录')
    shutil.rmtree(target)


def render(data, output, chrome):
    output.mkdir(parents=True, exist_ok=True)
    # Keep only expected render files in a task-specific output directory.
    if any(output.glob('poster-*.png')) or (output / 'manifest.json').exists():
        raise ValueError('输出目录已有海报；使用新的输出目录，以免旧图混入本次交付')
    shutil.copy2(ASSETS / 'poster.css', output / 'poster.css')
    shutil.copytree(ASSETS / 'fonts', output / 'fonts', dirs_exist_ok=True)
    covers = output / 'covers'; covers.mkdir(exist_ok=True)
    for item in data['items']:
        src = item.pop('_cover_path')
        rel = f'covers/cover-{item["ordinal"]:03d}{src.suffix.lower()}'
        shutil.copy2(src, output / rel); item['cover'] = rel
    template = (ASSETS / 'poster.html').read_text(encoding='utf-8')
    music = sum(x['type'] == 'music' for x in data['items']); podcasts = len(data['items'])-music
    subtitle = ' · '.join(filter(None, [f'{music} 首新音乐' if music else '', f'{podcasts} 期睡眠播客' if podcasts else '']))
    listening_note = '戴上耳机，选一段今晚的陪伴' if podcasts else '戴上耳机，挑一首听听'
    subtitle = f'{subtitle}，{listening_note}'
    batches = split_items(data['items']); pages = []
    profile = Path(tempfile.mkdtemp(prefix='audio-release-chrome-', dir=output))
    try:
        for number, items in enumerate(batches, 1):
            width, row_height, rows = geometry(len(items), data['layout']); height = row_height*len(rows)
            payload = dict(date=data['date'], heading=data['heading'], items=items, rows=rows, width=width, height=height, row_height=row_height, page=number, page_count=len(batches), subtitle=subtitle)
            encoded = json.dumps(payload, ensure_ascii=False).replace('<', '\\u003c')
            page = output / f'poster-{number:02d}.html'; png = page.with_suffix('.png')
            page.write_text(template.replace('__RELEASE_JSON__', encoded), encoding='utf-8')
            args = [chrome, '--headless=new', '--disable-gpu', '--no-first-run', '--no-default-browser-check', '--allow-file-access-from-files', '--hide-scrollbars', '--force-device-scale-factor=1', '--run-all-compositor-stages-before-draw', '--virtual-time-budget=5000', f'--user-data-dir={profile}', f'--window-size={width},{height}', f'--screenshot={png}', '--dump-dom', page.as_uri()]
            result = subprocess.run(args, capture_output=True, encoding='utf-8', errors='replace', timeout=90, creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
            match = re.search(r'<script id="render-report" type="application/json">(.*?)</script>', result.stdout, re.S)
            if result.returncode or not png.is_file() or not match:
                raise RuntimeError('浏览器未完成海报渲染: '+result.stderr[-1200:])
            report = json.loads(match.group(1))
            header = png.read_bytes()[:24]
            size = (int.from_bytes(header[16:20], 'big'), int.from_bytes(header[20:24], 'big'))
            if header[:8] != b'\x89PNG\r\n\x1a\n' or size != (width, height):
                report.setdefault('errors', []).append('PNG 尺寸不符合画布')
            if png.stat().st_size >= 10*1024*1024:
                report.setdefault('errors', []).append('PNG 超过飞书图片上传的 10 MB 限制')
            pages.append(dict(file=png.name, html=page.name, ordinals=[i['ordinal'] for i in items], width=width, height=height, report=report))
    finally:
        try: remove_profile(profile, output)
        except (OSError, ValueError) as exc: print('临时浏览器目录保留: '+str(exc), file=sys.stderr)
    def label(item): return f'试听《{item["title_en"]}》{item["title_zh"]}'
    invitation = '这周我们上新了睡前音频，欢迎大家来听听。'
    links = [[dict(tag='a', text=label(i), href=i['listen_url'])] for i in data['items']]
    content = [[dict(tag='text', text=invitation)], *links]
    save_json(output/'links-post.json', {'zh_cn': {'content': content}})
    def markdown_text(s): return re.sub(r'([\\\[\]])', r'\\\1', s)
    link_lines = [f'[{markdown_text(label(i))}](<{i["listen_url"]}>)' for i in data['items']]
    message = '\n\n'.join([invitation, *link_lines])+'\n'
    (output/'release-message.md').write_text(message, encoding='utf-8')
    manifest = {'date':data['date'], 'count':len(data['items']), 'pages':pages, 'items':[{k:v for k,v in i.items() if k in ('ordinal','type','title_en','title_zh','source_url','listen_url')} for i in data['items']], 'message':'release-message.md', 'post_links':'links-post.json', 'sent':False}
    save_json(output/'manifest.json', manifest)
    errors = [e for p in pages for e in p['report'].get('errors', [])]
    print(json.dumps({'ok':not errors,'manifest':str(output/'manifest.json'),'posters':[p['file'] for p in pages],'errors':errors}, ensure_ascii=False))
    return 2 if errors else 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--chrome')
    args = parser.parse_args()
    data = load_release(args.input.resolve())
    return render(data, args.output.resolve(), chrome_binary(args.chrome))


if __name__ == '__main__':
    try: sys.exit(main())
    except (ValueError, KeyError, OSError, RuntimeError, subprocess.TimeoutExpired) as exc:
        print('无法生成海报: '+str(exc), file=sys.stderr); sys.exit(2)
