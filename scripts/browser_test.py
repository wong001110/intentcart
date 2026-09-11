"""Real browser -> HTTP -> SQLite checks. Policy/browser failures are BLOCKED, never passed."""
import argparse
import json
import os
from pathlib import Path
import shutil
import socket
import subprocess
import sys
import tempfile
import time
import urllib.request

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', default='artifacts/browser')
    args = parser.parse_args()
    output = ROOT / args.output
    output.mkdir(parents=True, exist_ok=True)
    report = {'kind': 'browser-http-state integration; deterministic demo, not LLM evidence', 'status': 'running', 'checks': []}
    server = None
    try:
        from playwright.sync_api import sync_playwright
        with tempfile.TemporaryDirectory(prefix='intentcart-browser-') as tmp:
            with socket.socket() as sock:
                sock.bind(('127.0.0.1', 0))
                port = sock.getsockname()[1]
            url = f'http://127.0.0.1:{port}'
            env = dict(os.environ, INTENTCART_DRIVER='demo', INTENTCART_DB_PATH=str(Path(tmp)/'product.sqlite'))
            with (output/'server.log').open('w') as log:
                server = subprocess.Popen([sys.executable,'-m','uvicorn','intentcart.api:create_app','--factory','--host','127.0.0.1','--port',str(port)],cwd=ROOT,env=env,stdout=log,stderr=log)
                for _ in range(100):
                    try:
                        with urllib.request.urlopen(url+'/api/health', timeout=1): break
                    except OSError: time.sleep(.1)
                else: raise RuntimeError('Server did not start')
                with sync_playwright() as p:
                    binary = os.getenv('CHROMIUM_PATH') or shutil.which('chromium')
                    browser = p.chromium.launch(headless=True,**({'executable_path':binary} if binary else {}))
                    page = browser.new_page(viewport={'width':1440,'height':1000})
                    errors=[]
                    page.on('pageerror',lambda e:errors.append(str(e)))
                    page.on('console',lambda m:errors.append(m.text) if m.type=='error' else None)
                    page.goto(url)
                    page.wait_for_function("document.querySelector('#driver-badge').textContent.includes('非 LLM')")
                    assert page.locator('h1').is_visible()
                    report['checks'].append('loads with explicit demo label')
                    page.screenshot(path=str(output/'desktop.png'),full_page=True)
                    page.locator('#message').fill('我需要桌面燈和麥克風，預算 RM300，已有支架。')
                    page.locator('#send').click()
                    page.wait_for_function("!document.querySelector('#send').disabled && document.querySelectorAll('.message').length >= 2")
                    assert page.locator('#checkout').is_disabled()
                    def state(): return page.evaluate("fetch('/api/state').then(r=>r.json())")
                    first=state()
                    assert first['state']['constraints']['device_port']=='unknown'
                    assert first['state']['cart'] and not first['orders']
                    page.locator('#message').fill('我的手機是 USB-C。')
                    page.locator('#send').click()
                    page.wait_for_function("!document.querySelector('#send').disabled && !document.querySelector('#checkout').disabled")
                    assert state()['state']['validation']['ready']
                    report['checks'].append('clarification, real cart writes, no order')
                    before=state()['state']
                    page.locator('[data-view="browse"]').click()
                    page.locator('[data-details="dawn-sage"]').click()
                    assert page.locator('#product-dialog').is_visible()
                    assert state()['state']==before
                    page.locator('[data-close="product-dialog"]').click()
                    page.locator('#return-chat').click()
                    lamp=next(x['product']['id'] for x in before['items'] if x['product']['kind']=='light')
                    page.locator(f'[data-replace="{lamp}"]').click()
                    page.locator('[data-add="dawn-sage"]').click()
                    page.wait_for_function("document.querySelector('[data-cart-item=\"dawn-sage\"] .lock-badge') !== null")
                    page.locator('#return-chat').click()
                    assert state()['state']['cart']['dawn-sage']['locked']
                    report['checks'].append('read-only browsing and manual replacement share state')
                    page.locator('#message').fill('保留燈，預算改成 RM180。')
                    page.locator('#send').click()
                    page.wait_for_function("!document.querySelector('#send').disabled && !document.querySelector('#checkout').disabled")
                    revised=state()['state']
                    assert revised['validation']['total_cents']<=18000 and revised['cart']['dawn-sage']['locked']
                    page.reload()
                    page.wait_for_function("!document.querySelector('#checkout').disabled")
                    assert state()['state']==revised
                    page.screenshot(path=str(output/'prepared-cart.png'),full_page=True)
                    report['checks'].append('locked budget repair persists across reload')
                    page.locator('#checkout').click()
                    assert page.locator('#checkout-dialog').is_visible()
                    assert not state()['orders']
                    page.locator('#confirm-order').click()
                    page.locator('#receipt').wait_for(state='visible')
                    final=state()
                    assert len(final['orders'])==1 and not final['state']['cart']
                    report['checks'].append('only explicit final human confirmation creates simulated order')
                    page.set_viewport_size({'width':390,'height':844})
                    page.reload()
                    page.wait_for_function("document.querySelector('#driver-badge').textContent.includes('非 LLM')")
                    assert not page.evaluate('document.documentElement.scrollWidth > innerWidth')
                    page.screenshot(path=str(output/'mobile.png'),full_page=True)
                    assert not errors, errors
                    report['checks'].append('mobile no horizontal overflow and no console errors')
                    report['status']='passed'
                    browser.close()
    except Exception as exc:
        message=str(exc)
        blocked=any(word in message for word in ['ERR_BLOCKED_BY_ADMINISTRATOR','Executable doesn\'t exist','No module named','BrowserType.launch','Operation not permitted'])
        report.update(status='blocked' if blocked else 'failed',error=message)
    finally:
        if server:
            server.terminate()
            try: server.wait(timeout=5)
            except subprocess.TimeoutExpired: server.kill();server.wait()
        (output/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
    print(json.dumps(report,ensure_ascii=False,indent=2))
    return 0 if report['status']=='passed' else 2 if report['status']=='blocked' else 1

if __name__=='__main__': raise SystemExit(main())
