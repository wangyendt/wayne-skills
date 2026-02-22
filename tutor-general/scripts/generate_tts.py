#!/usr/bin/env python3
"""
TTS 生成脚本
用法: python generate_tts.py audio_list.csv ./audio --voice xiaoxiao
"""

import argparse
import asyncio
import edge_tts
import os
import csv
import json


async def generate_tts(csv_file: str, output_dir: str, voice: str = "zh-CN-XiaoxiaoNeural"):
    """生成 TTS 音频"""
    os.makedirs(output_dir, exist_ok=True)
    
    # 读取 CSV
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    results = []
    
    for row in rows:
        scene = row['scene']
        name = row['name']
        text = row['text']
        
        filename = f"audio_{int(scene):03d}_{name}.wav"
        filepath = os.path.join(output_dir, filename)
        
        print(f"生成: {filename}")
        
        # 生成 MP3
        communicate = edge_tts.Communicate(text, voice)
        mp3_path = filepath.replace('.wav', '.mp3')
        await communicate.save(mp3_path)
        
        # 转换为 WAV
        os.system(f"ffmpeg -y -i {mp3_path} -ar 16000 -ac 1 {filepath} >/dev/null 2>&1")
        os.remove(mp3_path)
        
        results.append({
            'scene': int(scene),
            'file': filename,
            'duration': 0  # 稍后验证
        })
    
    # 保存 audio_info.json
    info_path = os.path.join(output_dir, 'audio_info.json')
    with open(info_path, 'w', encoding='utf-8') as f:
        json.dump({'files': results}, f, ensure_ascii=False, indent=2)
    
    print(f"\n生成了 {len(results)} 个音频文件")


def main():
    parser = argparse.ArgumentParser(description='生成 TTS 音频')
    parser.add_argument('csv', help='CSV 文件路径')
    parser.add_argument('output', help='输出目录')
    parser.add_argument('--voice', default='zh-CN-XiaoxiaoNeural', help='语音')
    
    args = parser.parse_args()
    asyncio.run(generate_tts(args.csv, args.output, args.voice))


if __name__ == '__main__':
    main()
