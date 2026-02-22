#!/usr/bin/env python3
"""
音频验证脚本
用法: python validate_audio.py 分镜.md ./audio
"""

import os
import re
import json
import argparse
from pathlib import Path
from mutagen.wave import WAVE


def get_duration(wav_path: str) -> float:
    """获取 WAV 文件时长"""
    try:
        audio = WAVE(wav_path)
        return audio.info.length
    except:
        return 0


def validate_audio(storyboard_md: str, audio_dir: str) -> dict:
    """验证音频文件并更新分镜"""
    
    # 读取分镜文件
    with open(storyboard_md, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 查找音频文件名
    audio_files = re.findall(r'audio_(\d+)_\w+\.wav', content)
    
    audio_dir = Path(audio_dir)
    results = []
    
    # 验证每个音频
    for scene in audio_files:
        filename = f"audio_{int(scene):03d}.wav"
        filepath = audio_dir / filename
        
        if filepath.exists():
            duration = get_duration(str(filepath))
            results.append({
                'scene': int(scene),
                'file': filename,
                'duration': round(duration, 2)
            })
            print(f"✓ {filename}: {duration:.2f}s")
        else:
            print(f"✗ {filename}: 不存在")
            results.append({
                'scene': int(scene),
                'file': filename,
                'duration': 0
            })
    
    # 保存 audio_info.json
    info_path = audio_dir / 'audio_info.json'
    with open(info_path, 'w', encoding='utf-8') as f:
        json.dump({'files': results}, f, ensure_ascii=False, indent=2)
    
    print(f"\n验证完成，生成了 {info_path}")
    return results


def main():
    parser = argparse.ArgumentParser(description='验证音频文件')
    parser.add_argument('storyboard', help='分镜文件路径')
    parser.add_argument('audio_dir', help='音频目录')
    
    args = parser.parse_args()
    validate_audio(args.storyboard, args.audio_dir)


if __name__ == '__main__':
    main()
