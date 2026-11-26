#!/usr/bin/env python3
"""R33 납품 비교 이미지 — 전선 배경 4장 · 교차 순간 · 4대 보스 · 부처님의 가호 3순간 · R32 무신 · 총기 자세 원화 시트
사용: python3 -I compose33.py <캡처 폴더(capture33.js 출력)> <assets 폴더> <grips_r33.json> <출력 폴더>
"""
import json
import sys
from PIL import Image, ImageDraw, ImageFont

C, A, GJ, OUT = sys.argv[1:5]
F = ImageFont.truetype('/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc', 22)
FS = ImageFont.truetype('/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc', 17)


def label(im, text, sub=None):
    d = ImageDraw.Draw(im)
    w = max(d.textlength(text, font=F), d.textlength(sub, font=FS) if sub else 0) + 24
    h = 36 + (26 if sub else 0)
    d.rectangle([0, im.height - h, w, im.height], fill=(10, 10, 14))
    d.text((12, im.height - h + 6), text, fill=(253, 224, 71), font=F)
    if sub:
        d.text((12, im.height - h + 36), sub, fill=(230, 230, 230), font=FS)
    return im


def grid(items, cols, w, out, q=88):
    ims = []
    for path, t, sub in items:
        im = Image.open(path).convert('RGB')
        im = im.resize((w, int(im.height * w / im.width)), Image.LANCZOS)
        ims.append(label(im, t, sub))
    h = ims[0].height
    rows = (len(ims) + cols - 1) // cols
    S = Image.new('RGB', (cols * w + (cols - 1) * 6, rows * h + (rows - 1) * 6), (0, 0, 0))
    for i, im in enumerate(ims):
        S.paste(im, ((i % cols) * (w + 6), (i // cols) * (h + 6)))
    S.save(out, quality=q)
    print(out, S.size)


grid([(f'{C}/map1.png', 'Z1 · 1전선 거란 — 폭우 · 번개', '993~1019 거란의 침입 · 보병 리뉴얼 원화 · 전선 보스 소손녕'),
      (f'{C}/map2.png', 'Z2 · 2전선 여진 — 눈보라', '1107 동북 9성 · 도끼병 · 기병 · 미션 동북 9성 사수 · 전선 보스 아골타'),
      (f'{C}/map3.png', 'Z3 · 3전선 몽골 — 붉은 노을 · 잿가루', '1231~ 몽골의 침입 · 변발 기병 리뉴얼 · 미션 돌격 저지 · 전선 보스 살리타이'),
      (f'{C}/map4.png', 'Z4 · 4 · 5전선 왜구 · 홍건적 — 개경 화염 · 불티 폭풍', '왜구 · 홍건적 웨이브 + 미션 2 → 최종 보스 파두반')], 2, 960, f'{OUT}/R33-maps.jpg')
grid([(f'{C}/map_fade_khitan_jurchen.png', '전선이 바뀌는 순간 — 약 1.6초 교차(거란 → 여진)', '구역을 정리하면 다음 전선 배경 · 날씨로 실시간 전환')], 1, 1280, f'{OUT}/R33-map-crossfade.jpg')
grid([(f'{C}/boss_MB_SOSON.png', '1전선 보스 · 거란 장수 소손녕', '언월도 베기 · 거란 철기 돌진 · 궁기병 사격 → 50% 2페이즈 80만 대군 호령 연격'),
      (f'{C}/boss_MB_AGUDA.png', '2전선 보스 · 여진 완안부 용장 아골타', '거대 도끼 내려찍기 · 철기 돌격 → 50% 2페이즈 도끼 폭풍 · 3연 도약 참격'),
      (f'{C}/boss_MB_SARTAI.png', '3전선 보스 · 몽골 원수 살리타이', '기사 일제 사격 · 만곡도 돌진 · 변발 기마대 돌격 → 50% 2페이즈 3연 돌격 · 회오리 연격'),
      (f'{C}/boss_paduban.png', '최종 보스 · 홍건적 대장 파두반', '쌍도 참격 · 붉은 두건 돌격 · 화공 포격 → 35% 요술 결계 → 부처님의 가호')], 2, 960, f'{OUT}/R33-bosses.jpg')
grid([(f'{C}/buddha_a_descend.png', '① 범종 → 0.3초 뒤 차임 · 황금빛 암전', '부처님 뒤 연꽃 광륜 회전 · 손바닥 빛기둥이 하늘에서 강림 · 대장경 두루마리 상승'),
      (f'{C}/buddha_b_palm_hit.png', '② 빛기둥이 보스 발밑에 닿는 순간 결계 파쇄', '가산 합성 번쩍 · 최대 체력 20% 피해 · 3초 기절'),
      (f'{C}/buddha_c_scrolls.png', '③ 두루마리가 주인공을 감싸며 떠오름', '알파 페이드 · 가산 합성만(ctx.filter 없음)')], 1, 1280, f'{OUT}/R33-buddha.jpg')

# R32 원화 시트: 척준경 무신 4자세(최종 쥔 자리로 장검 얹음) · 김원봉 총기 4자세
G = json.load(open(GJ, encoding='utf-8'))['R26_CJG_FRAMES']
wp = Image.open(f'{A}/weapon/era4_t2.png').convert('RGBA')


def with_weapon(fr):
    body = Image.open(f'{A}/hero/era4_hero_{fr}.webp').convert('RGBA')
    PAD = 220
    can = Image.new('RGBA', (512 + 2 * PAD, 512 + 2 * PAD), (0, 0, 0, 0))
    can.alpha_composite(body, (PAD, PAD))
    x, y, a, f = G[fr]
    w = wp.transpose(Image.FLIP_TOP_BOTTOM) if f else wp
    gy = (w.height - 60) if f else 60
    big = Image.new('RGBA', (w.width * 2 + 4, w.height * 2 + w.width * 2), (0, 0, 0, 0))
    cx, cy = big.width // 2, big.height // 2
    big.alpha_composite(w, (cx - 70, cy - gy))
    rot = big.rotate(-a, center=(cx, cy), resample=Image.BICUBIC)
    lay = Image.new('RGBA', can.size, (0, 0, 0, 0))
    lay.paste(rot, (int(x + PAD - cx), int(y + PAD - cy)), rot)
    can.alpha_composite(lay)
    return can.crop((PAD - 120, PAD - 40, PAD + 512 + 120, PAD + 512 + 10))


cells = [(with_weapon(fr), f'척준경 {fr}', d) for fr, d in [('cleave_prep', '3타 선딜(두 손 머리 위)'), ('cleave_hit', '3타 갑옷 쪼개기'), ('charge', '돌진 = 요새 충차'), ('dragon_stance', '일섬 · 각성 = 청룡')]]
for fr, d in [('pistol', '3타 모젤 권총'), ('dual', '공중 쌍권총'), ('bomb', '4타 의열단 폭탄'), ('rifle', '각성 소총')]:
    cells.append((Image.open(f'{A}/hero/era6_hero_{fr}.webp').convert('RGBA'), f'김원봉 {fr}', d))
cw, ch = 330, 330
S = Image.new('RGB', (4 * cw, 2 * (ch + 52) + 40), (24, 26, 32))
d = ImageDraw.Draw(S)
d.text((10, 8), 'R32 원화 연결 — 척준경 무신 4자세(장검 = 최종 쥔 자리) · 김원봉 총기 4자세(총 그려 넣은 전신)', fill=(250, 250, 250), font=F)
for i, (im, t, sub) in enumerate(cells):
    bg = Image.new('RGBA', im.size, (52, 58, 70, 255))
    bg.alpha_composite(im)
    th = bg.convert('RGB')
    th.thumbnail((cw - 10, ch - 10), Image.LANCZOS)
    x0 = (i % 4) * cw + (cw - th.width) // 2
    y0 = 40 + (i // 4) * (ch + 52)
    S.paste(th, (x0, y0))
    d.text(((i % 4) * cw + 10, y0 + ch - 4), t, fill=(253, 224, 71), font=FS)
    d.text(((i % 4) * cw + 10, y0 + ch + 18), sub, fill=(220, 220, 220), font=FS)
S.save(f'{OUT}/R33-r32-poses.png')
print('poses', S.size)
