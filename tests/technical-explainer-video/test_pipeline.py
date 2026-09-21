import asyncio
import importlib.util
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SKILL = ROOT / 'technical-explainer-video'
STARTER = SKILL / 'assets/starter'


def module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


audio = module(STARTER / 'scripts/prepare_audio.py', 'audio_helpers')
scaffolder = module(SKILL / 'scripts/scaffold.py', 'scaffolder')


class PipelineTests(unittest.TestCase):
    def test_normalization_preserves_meaningful_text(self):
        self.assertEqual(audio.normalized('投影，１２ px。'), '投影12px')
        self.assertNotEqual(audio.normalized('1.4米'), audio.normalized('2.5米'))

    def test_caption_alignment_uses_boundaries_and_scene_offset(self):
        words = [{'text':'你好','offset':1000000,'duration':2000000},
                 {'text':'世界','offset':8000000,'duration':3000000}]
        cues = audio.align_captions('你好。世界。', words, 2, 10.45, 13)
        self.assertEqual(len(cues), 2)
        self.assertAlmostEqual(cues[0]['start'], 10.5)
        self.assertAlmostEqual(cues[1]['start'], 11.2)
        self.assertLessEqual(cues[0]['end'], cues[1]['start'])

    def test_boundary_mismatch_is_error(self):
        with self.assertRaisesRegex(ValueError, 'mismatch'):
            audio.align_captions('你好。', [{'text':'世界','offset':0,'duration':1000000}], 1, .45, 3)

    def test_negative_and_reversed_boundaries_are_rejected(self):
        with self.assertRaises(ValueError):
            audio.align_captions('你好世界', [{'text':'你好','offset':1000000,'duration':-1}, {'text':'世界','offset':0,'duration':10000}], 1, .45, 3)

    def test_long_clause_split_is_semantic(self):
        self.assertEqual(audio.split_clauses('观察空间中的投影位置，改变深度后重新计算。', 12), ['观察空间中的投影位置，', '改变深度后重新计算。'])

    def test_stamp_carries_milliseconds(self):
        self.assertEqual(audio.stamp(59.9998), '00:01:00,000')
        self.assertEqual(audio.stamp(3661.23, '.'), '01:01:01.230')

    def test_signature_changes_with_narration_voice_rate(self):
        a = {'narration':'你好'}
        self.assertNotEqual(audio.cache_signature(a,'a','+10%'), audio.cache_signature(a,'b','+10%'))
        self.assertNotEqual(audio.cache_signature(a,'a','+10%'), audio.cache_signature({'narration':'世界'},'a','+10%'))
        self.assertNotEqual(audio.cache_signature(a,'a','+10%'), audio.cache_signature(a,'a','+20%'))

    def test_scaffold_is_self_contained_and_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as directory:
            path = scaffolder.scaffold(Path(directory) / '含空格 project')
            self.assertTrue((path / 'audio/narration.wav').exists())
            self.assertFalse(json.loads((path / 'audio/status.json').read_text())['narrated'])
            self.assertTrue((path / 'output/captions.srt').exists())
            self.assertTrue((path / 'package-lock.json').exists())
            original = (path / 'scenes.json').read_bytes()
            with self.assertRaises(ValueError):
                scaffolder.scaffold(path)
            self.assertEqual((path / 'scenes.json').read_bytes(), original)

    @unittest.skipUnless(shutil.which('ffmpeg') and shutil.which('ffprobe'), 'ffmpeg needed')
    def test_cached_audio_pipeline_offline(self):
        with tempfile.TemporaryDirectory() as directory:
            root = scaffolder.scaffold(Path(directory) / 'demo')
            scenes = [dict(id=1,title='测试',narration='你好，世界。',min_duration=2)]
            (root / 'scenes.json').write_text(json.dumps(scenes, ensure_ascii=False))
            # Synthetic audio and matching times exercise the pipeline; not real TTS evidence.
            subprocess.run(['ffmpeg','-v','error','-f','lavfi','-i','anullsrc=r=24000:cl=mono','-t','1','-y',str(root/'audio/01.mp3')],check=True)
            words = [{'text':'你好','offset':0,'duration':3000000},{'text':'世界','offset':4000000,'duration':3000000}]
            (root/'audio/01_boundaries.json').write_text(json.dumps(words))
            (root/'audio/01_cache.json').write_text(json.dumps({'signature':audio.cache_signature(scenes[0],'test','+10%')}))
            asyncio.run(audio.prepare(root,'test','+10%',True))
            t=json.loads((root/'src/timing.json').read_text())
            self.assertGreater(t['total_duration'], 2)
            self.assertAlmostEqual(t['total_duration']*30, round(t['total_duration']*30))
            self.assertIn('你好，世界', (root/'output/captions.srt').read_text())
            scenes[0]['narration']='改过了'
            (root/'scenes.json').write_text(json.dumps(scenes))
            with self.assertRaisesRegex(ValueError,'stale'):
                asyncio.run(audio.prepare(root,'test','+10%',True))


if __name__ == '__main__':
    unittest.main()
