/** Original geometric product illustrations; no external images or claimed real brands. */
export function productArt(product, hero = false) {
  const kind = product.kind || 'light';
  const tones = {ivory: ['#eee8dc', '#d9d1be'], sage: ['#a6b5a5', '#738875'], black: ['#42484a', '#242c2d']};
  const [base, shade] = tones[product.color] || tones.ivory;
  const shadow = '<ellipse cx="140" cy="204" rx="70" ry="12" fill="#293b30" opacity=".08"/>';
  const light = `<path d="M140 100v92" stroke="${shade}" stroke-width="11"/><ellipse cx="140" cy="190" rx="41" ry="9" fill="${shade}"/><ellipse cx="140" cy="185" rx="41" ry="9" fill="${base}"/><circle cx="140" cy="79" r="51" fill="${shade}"/><circle cx="140" cy="75" r="49" fill="${base}"/><circle cx="140" cy="75" r="37" fill="#fffcdf"/><circle cx="140" cy="75" r="30" fill="#fffef6"/>`;
  const microphone = `<path d="M140 157v31" stroke="${shade}" stroke-width="9"/><ellipse cx="140" cy="193" rx="36" ry="8" fill="${shade}"/><rect x="112" y="42" width="56" height="118" rx="27" fill="${shade}"/><rect x="118" y="48" width="44" height="77" rx="21" fill="${base}"/><path d="M124 62h32M121 73h38M121 84h38M121 95h38M124 106h32" stroke="${shade}" stroke-width="3" opacity=".8"/><path d="M103 125v10q0 33 37 33t37-33v-10" fill="none" stroke="${base}" stroke-width="6"/><circle cx="140" cy="141" r="4" fill="#c7e2b0"/>`;
  const stand = `<path d="M140 147v41M140 176l-45 28m45-28 45 28" stroke="${shade}" stroke-width="8" stroke-linecap="round"/><g transform="rotate(-12 140 94)"><rect x="106" y="25" width="68" height="129" rx="13" fill="${shade}"/><rect x="112" y="32" width="56" height="108" rx="9" fill="${base}"/><rect x="120" y="42" width="40" height="88" rx="5" fill="#dce7d9"/><circle cx="140" cy="146" r="3" fill="${base}"/></g>`;
  const accessory = `<rect x="83" y="75" width="114" height="99" rx="24" fill="${shade}"/><rect x="87" y="70" width="106" height="99" rx="23" fill="${base}"/><path d="M113 79v-8q0-28 27-28t27 28v8" fill="none" stroke="${shade}" stroke-width="8"/><path d="M108 106h64" stroke="${shade}" stroke-width="3"/><circle cx="174" cy="107" r="5" fill="#fbf8ef"/>`;
  return `<svg viewBox="0 0 280 235" role="img" aria-label="${hero ? '桌面用品示意' : '合成商品示意圖'}">${shadow}${({light, microphone, stand, accessory})[kind] || accessory}</svg>`;
}
