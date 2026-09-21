#!/usr/bin/env python3
"""Generate narration, word-aligned burned-caption data, SRT/VTT and scene timing."""
import argparse
import asyncio
import hashlib
import json
import math
import re
import subprocess
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def normalized(text):
    return ''.join(c for c in unicodedata.normalize('NFKC', text).casefold() if c.isalnum())


def split_clauses(text, limit=28):
    result = []
    for sentence in re.split(r'(?<=[。！？!?])', text):
        current = ''
        for part in re.split(r'(?<=[，；,;])', sentence):
            if current and len((current + part).strip()) > limit:
                result.append(current.strip())
                current = part
            else:
                current += part
        if current.strip():
            result.append(current.strip())
    return result


def align_captions(text, boundaries, scene_id, voice_start, scene_end, segments=None):
    if not boundaries or ''.join(normalized(w['text']) for w in boundaries) != normalized(text):
        raise ValueError(f'Scene {scene_id}: boundary text mismatch; use corrected boundaries or forced alignment')
    ranges, cursor, previous = [], 0, -1
    for word in boundaries:
        if word['offset'] < previous or word['duration'] < 0:
            raise ValueError('Invalid word boundary time')
        previous = word['offset']
        length = len(normalized(word['text']))
        ranges.append((cursor, cursor + length, word))
        cursor += length
    if segments is not None:
        if not segments or any(not isinstance(seg.get('text'), str) or not seg['text'].strip()
                               or not isinstance(seg.get('speech'), str) or not normalized(seg['speech'])
                               for seg in segments):
            raise ValueError('Each segment needs nonempty display text and speech')
        if ''.join(seg['speech'] for seg in segments) != text:
            raise ValueError('Segment speech must concatenate exactly to narration')
        pairs = [(seg['speech'], seg['text']) for seg in segments]
    else:
        pairs = [(phrase, phrase.strip('，。；,; ')) for phrase in split_clauses(text)]
    cues, cursor = [], 0
    for segment, (phrase, display) in enumerate(pairs):
        count = len(normalized(phrase))
        if not count:
            continue
        words = [w for lo, hi, w in ranges if hi > cursor and lo < cursor + count]
        start = max(voice_start, voice_start + words[0]['offset'] / 1e7 - .05)
        end = min(scene_end - .08, voice_start + (words[-1]['offset'] + words[-1]['duration']) / 1e7 + .14)
        cues.append(dict(scene=scene_id, start=round(start, 4), end=round(end, 4),
                         text=display, source_text=phrase, segment=segment,
                         method='TTS WordBoundary + authored display text' if segments is not None else 'TTS WordBoundary'))
        cursor += count
    for a, b in zip(cues, cues[1:]):
        a['end'] = min(a['end'], round(b['start'] - .02, 4))
    if not all(c['start'] < c['end'] for c in cues):
        raise ValueError('Caption split overlaps a word; revise narration or boundaries')
    return cues


def stamp(seconds, separator=','):
    ms = round(seconds * 1000)
    hours, ms = divmod(ms, 3600000)
    minutes, ms = divmod(ms, 60000)
    seconds, ms = divmod(ms, 1000)
    return f'{hours:02}:{minutes:02}:{seconds:02}{separator}{ms:03}'


def write_subtitles(cues, output):
    output.mkdir(exist_ok=True)
    srt, vtt = [], ['WEBVTT\n']
    for i, cue in enumerate(cues, 1):
        srt.append(f"{i}\n{stamp(cue['start'])} --> {stamp(cue['end'])}\n{cue['text']}\n")
        vtt.append(f"{stamp(cue['start'], '.')} --> {stamp(cue['end'], '.')}\n{cue['text']}\n")
    (output / 'captions.srt').write_text('\n'.join(srt), encoding='utf-8')
    (output / 'captions.vtt').write_text('\n'.join(vtt), encoding='utf-8')


def cache_signature(scene, voice, rate):
    payload = json.dumps([scene['narration'], voice, rate, 'edge-tts-7.2.8/WordBoundary'], ensure_ascii=False)
    return hashlib.sha256(payload.encode()).hexdigest()


async def generate_segment(text, voice, rate, mp3, words_path):
    import edge_tts
    for attempt in range(3):
        temp = mp3.with_suffix('.tmp')
        try:
            words = []
            with temp.open('wb') as out:
                stream = edge_tts.Communicate(text, voice, rate=rate, boundary='WordBoundary')
                async for event in stream.stream():
                    if event['type'] == 'audio':
                        out.write(event['data'])
                    elif event['type'] == 'WordBoundary':
                        words.append(event)
            if not words or not temp.stat().st_size:
                raise ValueError('TTS returned no audio or boundaries')
            temp.replace(mp3)
            words_path.write_text(json.dumps(words, ensure_ascii=False, indent=2))
            return
        except Exception:
            temp.unlink(missing_ok=True)
            if attempt == 2:
                raise
            await asyncio.sleep(2)


async def prepare(root, voice, rate, cached_only=False):
    scenes = json.loads((root / 'scenes.json').read_text())
    if not scenes or [s['id'] for s in scenes] != list(range(1, len(scenes) + 1)):
        raise ValueError('Scene IDs must be consecutive integers from 1')
    config = json.loads((root / 'video.config.json').read_text())
    fps = config['fps']
    if not isinstance(fps, int) or fps <= 0:
        raise ValueError('fps must be a positive integer')
    audio = root / 'audio'
    audio.mkdir(exist_ok=True)
    (root / 'output').mkdir(exist_ok=True)
    start, result, captions, padded = 0., [], [], []
    for scene in scenes:
        if not scene['title'].strip() or not normalized(scene['narration']):
            raise ValueError('Empty scene title or narration')
        stem = f"{scene['id']:02}"
        mp3, words_path, cache = [audio / (stem + suffix) for suffix in ['.mp3', '_boundaries.json', '_cache.json']]
        signature = cache_signature(scene, voice, rate)
        valid_cache = all(p.exists() for p in [mp3, words_path, cache]) and json.loads(cache.read_text()).get('signature') == signature
        if not valid_cache:
            if cached_only:
                raise ValueError(f'Scene {stem}: missing or stale audio cache')
            await generate_segment(scene['narration'], voice, rate, mp3, words_path)
            cache.write_text(json.dumps(dict(signature=signature)))
        duration = float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', str(mp3)]))
        if not math.isfinite(duration) or duration <= 0:
            raise ValueError('Invalid audio duration')
        length = math.ceil(max(scene.get('min_duration', 0), duration + 1.2) * fps) / fps
        voice_start = start + .45
        cues = align_captions(scene['narration'], json.loads(words_path.read_text()), scene['id'], voice_start, start + length, scene.get('segments'))
        captions.extend(cues)
        dest = audio / (stem + '_padded.wav')
        subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', str(mp3), '-af', 'adelay=450:all=1,apad', '-t', str(length), '-ar', '48000', '-ac', '2', str(dest)], check=True)
        padded.append(dest)
        result.append(dict(id=scene['id'], title=scene['title'], start=start, duration=length,
                           voice_start=voice_start, voice_duration=duration))
        start = round((start + length) * fps) / fps
    import wave
    with wave.open(str(audio / 'narration.wav'), 'wb') as out:
        out.setparams((2, 2, 48000, 0, 'NONE', 'not compressed'))
        for path in padded:
            with wave.open(str(path), 'rb') as part:
                out.writeframes(part.readframes(part.getnframes()))
    timing = dict(total_duration=start, scenes=result)
    (root / 'src/timing.json').write_text(json.dumps(timing, ensure_ascii=False, indent=2))
    (root / 'src/subtitles.json').write_text(json.dumps(captions, ensure_ascii=False, indent=2))
    (audio / 'status.json').write_text(json.dumps(dict(narrated=True, voice=voice, rate=rate, alignment='TTS WordBoundary')))
    write_subtitles(captions, root / 'output')
    print(json.dumps(dict(seconds=start, scenes=len(result), captions=len(captions)), ensure_ascii=False))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--voice', default='zh-CN-XiaoxiaoNeural')
    parser.add_argument('--rate', default='+10%')
    parser.add_argument('--cached-only', action='store_true')
    args = parser.parse_args()
    asyncio.run(prepare(ROOT, args.voice, args.rate, args.cached_only))
