"""Synthetic fixture v1. Prices are MYR cents, inclusive of all simulated fees.
No rating, merchant, compatibility, or stock value is scraped or presented as real.
"""
from copy import deepcopy

FIXTURE_VERSION = 'desk-recording-v1'
PRODUCTS = []


def add(family, name, zh, kind, price, *, colors=('ivory', 'sage'), ports=('any',),
        connector_ports=(), stock=8, requires=(), desk=True, note=''):
    for color in colors:
        for port in ports:
            PRODUCTS.append(dict(
                id=f'{family}-{color}' + (f'-{port}' if port != 'any' else ''),
                family_id=family, name=name, name_zh=zh, kind=kind, color=color,
                port=port, connector_ports=list(connector_ports or (() if port == 'any' else (port,))),
                price_cents=price, stock=stock, requires=list(requires),
                desk_fit=desk, description=note or f'Synthetic {kind} for a desk recording setup.',
                fee_scope='All simulated fees included', synthetic=True,
            ))


add('dawn', 'Dawn desk light', '晨光桌面補光燈', 'light', 8900)
add('pocket', 'Pocket panel', '口袋柔光燈', 'light', 5900)
add('halo', 'Halo ring light', 'Halo 環形補光燈', 'light', 10900)
add('beam', 'Beam mini', 'Beam 迷你燈', 'light', 6900)
add('studio', 'Studio panel', 'Studio 桌面光板', 'light', 15900)
add('floor', 'Floor softbox', '落地柔光箱', 'light', 12900, desk=False)
add('clip', 'Clip wired microphone', 'Clip 有線領夾麥克風', 'microphone', 7900,
    colors=('black', 'ivory'), ports=('usb-c', 'lightning'))
add('air', 'Air wireless microphone', 'Air 無線領夾麥克風', 'microphone', 11900,
    colors=('black', 'ivory'), ports=('usb-c', 'lightning'))
add('voice', 'Voice desktop microphone', 'Voice 桌面麥克風', 'microphone', 12900,
    colors=('black', 'sage'), ports=('usb-c', 'lightning'))
add('pro', 'Pro microphone kit', 'Pro 收音組', 'microphone', 9900,
    colors=('black',), ports=('usb-c', 'lightning'), requires=('power',))
add('mystery', 'Unspecified microphone', '規格待確認麥克風', 'microphone', 4900,
    colors=('black',), ports=('unknown',), note='Connector specification is not provided. Do not assume compatibility.')
add('retired', 'Archive microphone', 'Archive 麥克風', 'microphone', 3900,
    colors=('black',), ports=('usb-c',), stock=0)
add('angle', 'Angle phone stand', 'Angle 手機支架', 'stand', 4500)
add('fold', 'Fold travel stand', 'Fold 摺疊支架', 'stand', 2900)
add('arm', 'Desk mounting arm', '桌面懸臂支架', 'stand', 7900)
add('mini', 'Mini tripod', 'Mini 桌面腳架', 'stand', 3900)
add('power', 'Power adapter', '電源轉接器', 'accessory', 2500, colors=('ivory',))
add('cable', 'USB-C cable', 'USB-C 連接線', 'accessory', 1900, colors=('black',), connector_ports=('usb-c',))
add('wind', 'Microphone windshield', '麥克風防風罩', 'accessory', 1500, colors=('black',))
add('case', 'Storage pouch', '收納袋', 'accessory', 2200, colors=('sage',))
BY_ID = {p['id']: p for p in PRODUCTS}
assert len(BY_ID) == len(PRODUCTS)


def get_product(variant_id):
    p = BY_ID.get(variant_id)
    return deepcopy(p) if p else None


def search_products(query='', kind=None, color=None, port=None, max_price_cents=None, stock=None):
    result = []
    for raw in PRODUCTS:
        p = deepcopy(raw)
        p['stock'] = (stock or {}).get(p['id'], p['stock'])
        if kind and p['kind'] != kind:
            continue
        if color and p['color'] != color:
            continue
        if port and p['port'] not in ('any', port):
            continue
        if max_price_cents is not None and p['price_cents'] > max_price_cents:
            continue
        if query and query.casefold() not in (' '.join([p['id'], p['name'], p['name_zh'], p['kind'], p['description']])).casefold():
            continue
        result.append(p)
    return sorted(result, key=lambda p: (p['price_cents'], p['id']))
