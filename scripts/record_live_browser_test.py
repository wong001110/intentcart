"""Capped live-model browser smoke test with an explicit local video artifact."""
import argparse
import json
from pathlib import Path
import re
import sys
import time


ROOT = Path(__file__).resolve().parents[1]


def wait_for_turn(page, timeout):
    page.locator('#send:disabled').wait_for(timeout=timeout)
    page.locator('#send:enabled').wait_for(timeout=timeout)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--base-url', default='http://127.0.0.1:8000')
    parser.add_argument('--output', default='artifacts/live-browser-recording')
    parser.add_argument('--width', type=int, default=1920)
    parser.add_argument('--height', type=int, default=1080)
    parser.add_argument('--allow-live', action='store_true', help='Required acknowledgement that this makes exactly two provider-backed turns.')
    args = parser.parse_args()
    if not args.allow_live:
        parser.error('--allow-live is required because this test calls the configured live model twice.')
    if args.width < 320 or args.height < 320:
        parser.error('Viewport dimensions must be at least 320 pixels.')

    output = ROOT / args.output
    video_dir = output / 'video'
    output.mkdir(parents=True, exist_ok=True)
    video_dir.mkdir(exist_ok=True)
    report = {
        'kind': 'capped live-model browser smoke test; two provider-backed turns',
        'status': 'running',
        'base_url': args.base_url,
        'viewport': {'width': args.width, 'height': args.height},
        'checks': [],
    }
    context = browser = None
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            context = browser.new_context(
                viewport={'width': args.width, 'height': args.height},
                record_video_dir=str(video_dir),
                record_video_size={'width': args.width, 'height': args.height},
            )
            page = context.new_page()
            video = page.video
            page.add_init_script("localStorage.setItem('intentcart-language', 'en')")
            page.goto(args.base_url, wait_until='networkidle')
            page.locator('#driver-badge').filter(has_text='Live model').wait_for(timeout=15_000)
            page.locator('#language-toggle').filter(has_text='中文').wait_for(timeout=15_000)
            report['checks'].append('English UI and live driver are visible')

            page.locator('#message').fill('I need a desk light and microphone for videos. My budget is RM300, and I already own a stand.')
            page.locator('#send').click()
            wait_for_turn(page, 120_000)
            page.locator('#messages').get_by_text(re.compile('USB-C|Lightning')).wait_for(timeout=15_000)
            state = page.evaluate("fetch('/api/state').then(response => response.json())")
            assert state['state']['constraints']['device_port'] == 'unknown'
            assert not state['state']['validation']['ready']
            report['checks'].append('Live model asks for the missing connector without claiming checkout')

            page.locator('#message').fill('My phone uses USB-C.')
            page.locator('#send').click()
            wait_for_turn(page, 120_000)
            page.locator('#checkout:enabled').wait_for(timeout=15_000)
            state = page.evaluate("fetch('/api/state').then(response => response.json())")
            assistant_text = '\n'.join(message['text'] for message in state['messages'] if message['role'] == 'assistant')
            assert state['state']['validation']['ready']
            assert not re.search(r'[\u3400-\u9fff]', assistant_text)
            report['checks'].append('Live model prepares a verified USB-C cart with English assistant output')

            page.screenshot(path=str(output / 'final-1920x1080.png'), full_page=True)
            report['status'] = 'passed'
            context.close()
            context = None
            report['video'] = str(video.path().relative_to(ROOT))
    except Exception as exc:
        report.update(status='failed', error=repr(exc))
    finally:
        if context:
            context.close()
        if browser:
            browser.close()
        (output / 'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report['status'] == 'passed' else 1


if __name__ == '__main__':
    raise SystemExit(main())
