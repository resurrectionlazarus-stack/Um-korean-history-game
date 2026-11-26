#!/usr/bin/env python3
"""R33 — 4시대 고려 코어 대확장(전선별 전용 맵 4장 실시간 전환 · 전선 날씨 · 4대 보스 소손녕 · 아골타 · 살리타이 · 파두반) ·
부처님의 가호(팔만대장경 강림) 경건 · 신비 리뉴얼(종소리 → 0.3초 뒤 차임 · 황금빛 암전 · 연꽃 광륜 · 손바닥 빛기둥 · 대장경 두루마리) ·
전 시대 손 ↔ 무기 쥔 자리 전수 보정 · R32 원화(척준경 무신 4자세 · 질주 8장 · 김원봉 총기 4자세 · 이펙트 4 · 효과음 6) 연결.

사용: python3 -I r33_patch.py <shinsi-R33/index.html>   (R31 index.html 위에 적용 · 쥔 자리 표는 같은 폴더 grips_r33.json)
"""
import json
import os
import re
import sys

P = sys.argv[1]
s = open(P, encoding="utf-8").read()
n = 0
HERE = os.path.dirname(os.path.abspath(__file__))


def rep(old, new, count=1):
    global s, n
    c = s.count(old)
    if c != count:
        raise SystemExit(f"anchor count {c} (want {count}): {old[:160]!r}")
    s = s.replace(old, new)
    n += 1


# ───────── 1. 손 ↔ 무기 쥔 자리(R33 전수 점검 결과 · tools/r33/grips_r33.json) ─────────
G = json.load(open(os.path.join(HERE, "grips_r33.json"), encoding="utf-8"))
for name, tab in G.items():
    pat = re.compile(r"  var " + name + r" = \{.*?\};")
    if len(pat.findall(s)) != 1:
        raise SystemExit("grip table " + name)
    s = pat.sub(lambda m: "  var " + name + " = " + json.dumps(tab, separators=(",", ":")) + ";", s)
    n += 1
rep('''  var R26_CJG_FRAMES = {''', '''  // [R33] 손 ↔ 무기 쥔 자리 전수 보정(74장 — 사냥꾼 22 · 해모수 26 · 척준경 26) — 무기 원화의 주먹이 몸 원화의 손(맨주먹 살색 · 팔 보호대 끝 구멍)을 남김없이 덮는 자리를
  //  3등급 무기 모두로 ±10px 전수 탐색(tools/r33/grip_fit.py) + 겹쳐 그리기 시트 육안 확인(grip_try.py · grip_zoom.py).
  //  고친 곳: 사냥꾼 idle(30px — 주먹이 팔뚝 가운데) · 해모수 slam_prep(27px — 두 주먹 사이 허공) · heavy_cleave · atk3_2 · slam_hit · summon_sky ·
  //  척준경 새 질주 8장(R32 원화) · 무신 4자세(cleave_prep 두 손 머리 위 파지 · cleave_hit · charge · dragon_stance) 새로 잼
  var R26_CJG_FRAMES = {''')

# ───────── 2. 배우 · 보스 · 이펙트 사양 ─────────
# 척준경: R32 새 질주 8장(허리 가운데가 idle보다 29px 앞 → poseDX로 맞춤) + 무신 4자세
rep('''"atk2_3", "atk3_prep", "atk3", "atk3_2", "atk3_3"], ext: "webp", groundY: 470, anchorX: 234, view: 0.28, topY: 30, footW: 70, feet: 30, atk: { melee: ["atk2", "atk1"], fin: "atk3" }, weapon: { frames: R26_CJG_FRAMES,''',
    '''"atk2_3", "atk3_prep", "atk3", "atk3_2", "atk3_3", "cleave_prep", "cleave_hit", "charge", "dragon_stance"], ext: "webp", groundY: 470, anchorX: 234, view: 0.28, topY: 30, footW: 70, feet: 30, poseDX: { run: -29, run2: -29, run3: -29, run4: -29, run5: -29, run6: -29, run7: -29, run8: -29, dragon_stance: -30 }, atk: { melee: ["atk2", "atk1"], fin: "atk3" }, weapon: { frames: R26_CJG_FRAMES,''')
rep('''    era6_hero: { role: "hero", kind: "hero", poses: ["idle", "run", "atk1", "atk2", "hit"], extra: ["run2", "run3", "run4", "run5", "run6", "run7", "run8"], groundY: 470,''',
    '''    // [R32 → R33] 김원봉 총기 4자세(모젤 권총 · 쌍권총 · 소총 · 폭탄 투척 — 총을 그려 넣은 전신 webp) · idle도 webp로 교체(R32)
    era6_hero: { role: "hero", kind: "hero", poses: ["idle", "run", "atk1", "atk2", "hit"], extra: ["run2", "run3", "run4", "run5", "run6", "run7", "run8", "pistol", "dual", "rifle", "bomb"], extPose: { idle: "webp", pistol: "webp", dual: "webp", rifle: "webp", bomb: "webp" }, groundY: 470,''')
rep('''    mongol: { role: "mid", kind: "MB_MONGOL", poses: ["idle", "charge", "volley", "hit"], groundY: 600,''',
    '''    // [R33] 몽골 천호장(MB_MONGOL) → 3전선 보스 살리타이로 교체 — 원화는 남겨 두고 읽지 않음(skip)
    mongol: { role: "mid", kind: "MB_MONGOL", skip: true, poses: ["idle", "charge", "volley", "hit"], groundY: 600,''')
rep('''    siege: { role: "boss", kind: "siege", poses: ["idle", "flame", "smash", "hit"],''',
    '''    // [R33] 철갑 공성 사령관(siege) → 최종 보스 파두반으로 교체 — 원화는 남겨 두고 읽지 않음(skip)
    siege: { role: "boss", kind: "siege", skip: true, poses: ["idle", "flame", "smash", "hit"],''')
rep('''    // [R21] 6차 패키지 — 6시대 광복: 주인공 독립군 장교''',
    '''    // [R33] 4시대 고려 4대 보스(768×640 · 발 y600 · 오른쪽 보기 · idle / walk / slash / hit) — 파일 boss/era4_boss_{이름}_{동작}.webp
    //  anchorX = idle 두 발 가운데와 머리 가운데 사이(실측) · feet = 앞 · 뒷발(게임 단위) · walk 1장은 idle과 번갈아(몸통 가운데 맞춤 alignWalk)
    //  크기: 전선 보스 셋 키 183~189(주인공의 약 1.5배) · 최종 보스 파두반 196
    boss_sosonnyeong: { role: "mid", kind: "MB_SOSON", poses: ["idle", "slash", "hit"], extra: ["walk"], ext: "webp", groundY: 600, anchorX: 418, view: 0.32, topY: 28, footW: 128, gait: 9, feet: [35, -31], alignWalk: true },
    boss_aguda: { role: "mid", kind: "MB_AGUDA", poses: ["idle", "slash", "hit"], extra: ["walk"], ext: "webp", groundY: 600, anchorX: 330, view: 0.33, topY: 34, footW: 138, gait: 9, feet: [41, -41], alignWalk: true },
    boss_sartai: { role: "mid", kind: "MB_SARTAI", poses: ["idle", "slash", "hit"], extra: ["walk"], ext: "webp", groundY: 600, anchorX: 372, view: 0.33, topY: 28, footW: 120, gait: 9, feet: [31, -25], alignWalk: true },
    boss_paduban: { role: "boss", kind: "paduban", poses: ["idle", "slash", "hit"], extra: ["walk"], ext: "webp", groundY: 600, anchorX: 340, view: 0.36, topY: 55, footW: 150, gait: 10, feet: [48, -52], alignWalk: true },
    // [R21] 6차 패키지 — 6시대 광복: 주인공 독립군 장교''')
rep('''fx_bronze_mirror_halo: { view: 0.46 }, fx_thunder_crack: { view: 0.54 } };''',
    '''fx_bronze_mirror_halo: { view: 0.46 }, fx_thunder_crack: { view: 0.54 },
    // [R33] 부처님의 가호 3종(톤다운 금지 — 굽기 때 딤 없음) · [R32] 척준경 무신 이펙트 4종
    fx_buddha_lotus_halo: { view: 0.72 }, fx_buddha_palm_light: { view: 1.05 }, fx_tripitaka_scrolls: { view: 0.66 },
    fx_armor_break: { view: 0.56 }, fx_fortress_ram: { view: 0.56 }, fx_azure_dragon: { view: 0.9 }, fx_blade_storm: { view: 0.62 } };
  // [R33] 4시대 전선 = 구역: Z1 거란(폭우 · 번개) → Z2 여진(눈보라) → Z3 몽골(붉은 노을 · 잿가루) → Z4 왜구 · 홍건적(개경 화염 · 불티 폭풍)
  var R33_ZONE_BG = ["khitan", "jurchen", "mongol", "kaegyeong_fire"];
  var R33_BG_WEATHER = { khitan: "KHITAN_STORM", jurchen: "JURCHEN_BLIZZARD", mongol: "MONGOL_ASH", kaegyeong_fire: "FIRE_STORM" };
  var R33_BG_FADE = 96;
  var R33_BG_PAR = 0.16;''')

# 4대 보스 HP · 전선 보스(중간보스) 3인: 체력 = 기준(살리타이) 대비 비율 · 50%에서 2페이즈(분노 · 연격 패턴)
rep('''    // [R14] 4시대 장기전: 몽골 천호장 체력 10 → 17 (보스 체력도 ×1.7)
    4: { key: "MB_MONGOL",''', '''    // [R33] 4시대 전선 보스 기준 = 3전선 살리타이(MIDBOSS_R33). 옛 몽골 천호장은 쓰지 않음(아래 키는 기록용)
    4: { key: "MB_SARTAI", zone: 2, ref: true, hp: 10, patterns: ["cone"], name: "살리타이", title: "", color: "#fca5a5" },
    // [R14] 4시대 장기전: 몽골 천호장 체력 10 → 17 (보스 체력도 ×1.7)
    4.5: { key: "MB_MONGOL",''')
rep('''  var midbossFor = (era, zone) => [MIDBOSS_SPECS[era], MIDBOSS_EXTRA[era]].find((M) => M && (M.zone != null ? M.zone : 2) === zone) || null;
  var eraMidbosses = (era) => [MIDBOSS_SPECS[era], MIDBOSS_EXTRA[era]].filter(Boolean);''',
    '''  // [R33] 4시대 전선 보스 3인 — 각 전선(구역)의 클라이맥스. 체력 비율(hp ÷ 기준 10): 소손녕 0.6 · 아골타 0.75 · 살리타이 0.9 (옛 천호장 1개 = 1.0)
  //  p2 = 체력 50% 이하 2페이즈 패턴(포효 · 섬광 · 속도 ×1.15) · labels = 예고 문구(역사 장수의 기술 이름) · toast · fairy = 등장 · 격파 해설
  var MIDBOSS_R33 = {
    4: [
      { key: "MB_SOSON", zone: 0, name: "거란 장수 소손녕", title: "993년 80만 대군을 내세워 쳐들어온 거란의 동경유수", hp: 6, patterns: ["cone", "lunge", "cone", "volley"], p2: ["storm", "lunge", "cone", "volley"], escort: "KHITAN_INF", color: "#cbd5e1",
        labels: { cone: "소손녕의 언월도 베기!", lunge: "거란 철기 돌진!", volley: "거란 궁기병 일제 사격!", storm: "80만 대군 호령 연격!" },
        toast: ["1전선 보스 · 거란 장수 소손녕", "993 — '고구려 땅은 거란의 것'이라며 압록강을 건넌 대장"],
        p2line: "🗡️ 소손녕: '80만 대군이 강을 건넜다!' — 분노 2페이즈!",
        fairy: "📜 993년 서희는 소손녕과 담판을 벌여 고려가 고구려를 이었음을 밝히고 강동 6주를 얻었어요 — 싸우지 않고 이긴 외교!" },
      { key: "MB_AGUDA", zone: 1, name: "여진 완안부 용장 아골타", title: "동북 9성을 노린 완안부 여진의 용장 — 훗날 금나라를 세운다(1115)", hp: 7.5, patterns: ["cone", "charge", "cone", "lunge"], p2: ["storm", "charge", "dash3", "cone"], escort: "JURCHEN_INF", color: "#e7e5e4",
        labels: { cone: "아골타의 거대 도끼 내려찍기!", charge: "여진 철기 돌격!", lunge: "도끼 돌진 베기!", storm: "완안부 도끼 폭풍!", dash3: "아골타 3연 도약 참격!" },
        toast: ["2전선 보스 · 여진 용장 아골타", "1107~1109 동북 9성 — 눈보라 속 완안부 여진의 도끼 대장"],
        p2line: "🪓 아골타의 포효! 도끼 폭풍 2페이즈!",
        fairy: "📜 1107년 윤관의 별무반이 여진을 몰아내고 동북 9성을 쌓았어요. 아골타가 이끈 완안부는 1115년 금나라를 세워요!" },
      { key: "MB_SARTAI", zone: 2, name: "몽골 원수 살리타이", title: "1231년 몽골 1차 침입을 이끈 원수(살리타) — 처인성에서 쓰러지다", hp: 9, patterns: ["volley", "lunge", "cone", "charge"], p2: ["volley", "dash3", "storm", "charge"], escort: "MONGOL_RIDER", color: "#fca5a5",
        labels: { volley: "몽골 기사(騎射) 일제 사격!", lunge: "만곡도 돌진 베기!", cone: "살리타이 만곡도 참격!", charge: "변발 기마대 돌격!", dash3: "초원의 3연 돌격!", storm: "만곡도 회오리 연격!" },
        toast: ["3전선 보스 · 몽골 원수 살리타이", "1231 — 붉은 노을 아래 변발 기마대를 거느린 원수"],
        p2line: "🏹 살리타이: '고려의 성은 모두 무너진다!' — 2페이즈!",
        fairy: "📜 1232년 처인성에서 승장 김윤후가 쏜 화살에 몽골 원수 살리타이가 쓰러졌어요! 몽골군은 곧 물러갔어요." }
    ]
  };
  var midbossFor = (era, zone) => [MIDBOSS_SPECS[era], MIDBOSS_EXTRA[era], ...MIDBOSS_R33[era] || []].find((M) => M && !M.ref && (M.zone != null ? M.zone : 2) === zone) || null;
  var eraMidbosses = (era) => [MIDBOSS_SPECS[era], MIDBOSS_EXTRA[era], ...MIDBOSS_R33[era] || []].filter((M) => M && !M.ref);''')

# 파일 목록(file:// 내장 목록) — R33 몹 webp 교체 · 4대 보스 · 전선 배경 · 이펙트 · 척준경 · 김원봉 새 자세
rep('''  var actorFiles = (era, dir, name) => {
    const S = actorSpecOf(era, name);
    return [...S.poses, ...S.extra || []].map((p) => `assets/${dir}/era${era}_${name}_${p}.${S.ext || "png"}`);
  };''', '''  var actorFiles = (era, dir, name) => {
    const S = actorSpecOf(era, name);
    return [...S.poses, ...S.extra || []].map((p) => `assets/${dir}/era${era}_${name}_${p}.${S.extPose && S.extPose[p] || S.ext || "png"}`);
  };''')
rep('''        ...[[4, "khitan_inf"], [4, "mongol_cav"], [5, "gunner"],''', '''        // [R33] 거란 보병 · 몽골 기병 리뉴얼 원화(webp — 옛 png 삭제)
        ...["khitan_inf", "mongol_cav"].flatMap((k) => MOB_POSES.map((p) => `assets/mob/era4_${k}_${p}.webp`)),
        // [R33] 4시대 전선 배경 4장 · 4대 보스 16장 · 부처님의 가호 3종 · [R32] 척준경 무신 이펙트 4종
        ...R33_ZONE_BG.map((k) => `assets/bg/era4_bg_${k}.webp`),
        ...["sosonnyeong", "aguda", "sartai", "paduban"].flatMap((b) => ["idle", "walk", "slash", "hit"].map((p) => `assets/boss/era4_boss_${b}_${p}.webp`)),
        ...["buddha_lotus_halo", "buddha_palm_light", "tripitaka_scrolls", "armor_break", "fortress_ram", "azure_dragon", "blade_storm"].map((k) => `assets/fx/era4_fx_${k}.webp`),
        ...[[5, "gunner"],''')

# planFor: skip 배우 · 4대 보스 원화 · 전선 배경
rep('''    const itemRe = new RegExp("(?:^|/)item/era" + era + "_([a-z0-9_]+)[.](?:png|webp)$");
    const items = {};''', '''    const itemRe = new RegExp("(?:^|/)item/era" + era + "_([a-z0-9_]+)[.](?:png|webp)$");
    const items = {};
    // [R33] 4대 보스 boss/era4_boss_{이름}_{동작} → 배우 boss_{이름} · 전선 배경 bg/era4_bg_{전선}
    const bossRe = new RegExp(`(?:^|/)boss/era${era}_boss_([a-z]+)_([a-z0-9]+)\\\\.(?:png|webp)$`);
    const fbgRe = new RegExp(`(?:^|/)bg/era${era}_bg_([a-z_]+)\\\\.(?:png|webp|jpg)$`);
    const fbg = {};''')
rep('''    keys.forEach((k) => {
      const it = k.match(itemRe);''', '''    keys.forEach((k) => {
      const fb = k.match(fbgRe);
      if (fb) {
        fbg[fb[1]] = k;
        return;
      }
      const bb = k.match(bossRe);
      if (bb) {
        const nm = "boss_" + bb[1];
        if (!actorSpecOf(era, nm)) return;
        const BA = actors[nm] || (actors[nm] = { name: nm, era, dir: "boss", files: {}, meta: {} });
        BA.files[bb[2]] = k;
        BA.meta[bb[2]] = files[k] || {};
        return;
      }
      const it = k.match(itemRe);''')
rep('''      const sp = actorSpecOf(era, name);
      if (sp && sp.hold && sp.hold.includes(pose) && !state.holdOff) {''', '''      const sp = actorSpecOf(era, name);
      if (sp && sp.skip) return;
      if (sp && sp.hold && sp.hold.includes(pose) && !state.holdOff) {''')
rep('''    const bgOk = bg.far && bg.mid && bg.ground;
    if (!bgOk && !Object.keys(ok).length && !Object.keys(fx).length && !dawn && !Object.keys(mobOk).length) return null;
    return { bg: bgOk ? bg : null, act2:''', '''    const bgOk = bg.far && bg.mid && bg.ground;
    // [R33] 전선 배경 4장이 모두 있으면 옛 3겹 배경(far · mid · ground · arena)은 읽지 않는다(메모리 · 로딩 절약)
    const fbgOk = era === 4 && R33_ZONE_BG.every((q) => fbg[q]);
    if (!bgOk && !fbgOk && !Object.keys(ok).length && !Object.keys(fx).length && !dawn && !Object.keys(mobOk).length) return null;
    return { fbg: fbgOk ? fbg : null, bg: bgOk && !fbgOk ? bg : null, act2:''')

# loadEraAssets: 전선 배경 굽기(하늘 · 땅 두 장 · 딤 · dpr 1.5 상한)
rep('''      for (const name of Object.keys(plan.actors)) {
        try {
          const a = await bakeActor(plan.actors[name], dpr);''', '''      if (plan.fbg) {
        try {
          const names = Object.keys(plan.fbg);
          const imgs = await Promise.all(names.map((q) => loadImage(plan.fbg[q])));
          const d2 = Math.min(dpr, 1.5);
          const k = ASSET_VIEW_SCALE * d2;
          const fronts = {};
          for (let i = 0; i < names.length; i++) {
            await nextFrame();
            const im = imgs[i];
            const H0 = plan.horizonY;
            const W = Math.round(im.width * k);
            const sky = mkCanvas(W, Math.round(H0 * k));
            const sx = sky.getContext("2d", { alpha: false });
            sx.imageSmoothingQuality = "high";
            sx.drawImage(im, 0, 0, im.width, H0, 0, 0, sky.width, sky.height);
            const gnd = mkCanvas(W, Math.round((im.height - H0) * k));
            const gx = gnd.getContext("2d", { alpha: false });
            gx.imageSmoothingQuality = "high";
            gx.drawImage(im, 0, H0, im.width, im.height - H0, 0, 0, gnd.width, gnd.height);
            const S1 = dimLayer(sky);
            const G1 = dimLayer(gnd);
            // 지평선 안개 띠 색 = 하늘 아래 · 땅 위 몇 줄의 평균색(눈밭은 밝게 · 노을은 붉게 — 검은 줄로 보이지 않게)
            let mist = "4,6,12";
            try {
              const t = mkCanvas(16, 2);
              const tx = t.getContext("2d", { willReadFrequently: true });
              const hh = Math.max(1, Math.round(8 * k));
              tx.drawImage(S1, 0, S1.height - hh, S1.width, hh, 0, 0, 16, 1);
              tx.drawImage(G1, 0, 0, G1.width, hh, 0, 1, 16, 1);
              const px = tx.getImageData(0, 0, 16, 2).data;
              let r = 0, gg = 0, bb = 0;
              for (let q = 0; q < 32; q++) {
                r += px[q * 4];
                gg += px[q * 4 + 1];
                bb += px[q * 4 + 2];
              }
              mist = `${Math.round(r / 32)},${Math.round(gg / 32)},${Math.round(bb / 32)}`;
              t.width = t.height = 0;
            } catch (e) {
            }
            fronts[names[i]] = { sky: S1, ground: G1, d2, mist };
            warmRaster([sky, gnd]);
          }
          out.bg = { fronts, horizon: plan.horizonY * ASSET_VIEW_SCALE, dim: BG_DIM, d2 };
        } catch (e) {
          fails.push("front bg " + e.message);
        }
      }
      for (const name of Object.keys(plan.actors)) {
        try {
          const a = await bakeActor(plan.actors[name], dpr);''')

# ───────── 3. 전선 배경 실시간 전환(교차 1.6초) · 전선 날씨(폭우 빗줄기 · 번개 · 눈보라 · 잿가루 · 불티) ─────────
rep('''    LIBERATION_LIGHT: { n: 68,''', '''    // [R33] 4시대 전선 날씨 — 거란 폭우(빗줄기 선 · 번개는 배경에서) · 여진 눈보라 · 몽골 잿가루 · 개경 불티 폭풍
    KHITAN_STORM: { n: 84, drift: -2.6, fall: 10.5, sway: 0, twinkle: 0, riseRatio: 0, colors: ["#cbd5e1"], size: [9, 15], style: "rain" },
    JURCHEN_BLIZZARD: { n: 96, drift: -2.8, fall: 1.9, sway: 0.9, twinkle: 0.3, riseRatio: 0.04, colors: ["#f8fafc", "#e2e8f0", "#bfdbfe"], size: [1.2, 3.3] },
    MONGOL_ASH: { n: 70, drift: -0.9, fall: 0.42, sway: 0.65, twinkle: 0.5, riseRatio: 0.3, colors: ["#a8a29e", "#78716c", "#fb923c", "#f97316"], size: [1, 2.6] },
    FIRE_STORM: { n: 86, drift: -1.5, fall: -0.95, sway: 0.8, twinkle: 1, riseRatio: 0.82, colors: ["#f97316", "#fb923c", "#fde047", "#ef4444"], size: [1, 2.7] },
    LIBERATION_LIGHT: { n: 68,''')
rep('''      }
      return arr;
    };
    const switchEraDirectly = (targetEra) => {''', '''      }
      arr.style = cfg.style || null;
      return arr;
    };
    const switchEraDirectly = (targetEra) => {''')
rep('''          if (m.y > 440) m.y = -8;''', '''          if (m.y > (g.weatherMotes.style === "rain" ? 548 : 440)) m.y = -8;''')
rep('''  function drawWeatherLayer(ctx, motes, camX, tick) {
    ctx.save();''', '''  function drawWeatherLayer(ctx, motes, camX, tick) {
    // [R33] 폭우: 점 대신 비스듬한 빗줄기 — 먼 줄 · 가까운 줄 두 번에 나눠 한 경로로 긋는다(그리기 2회)
    if (motes.style === "rain") {
      ctx.save();
      ctx.lineCap = "round";
      for (let pass = 0; pass < 2; pass++) {
        ctx.strokeStyle = pass ? "rgba(226,232,240,0.42)" : "rgba(148,163,184,0.3)";
        ctx.lineWidth = pass ? 1.3 : 0.8;
        ctx.beginPath();
        for (let i = 0; i < motes.length; i++) {
          const m = motes[i];
          if (!!m.near !== !!pass) continue;
          const par = m.near ? PAR.moteNear : PAR.moteFar;
          const sx = ((m.x - camX * par) % VIEW_W + VIEW_W) % VIEW_W;
          const L = m.size * (m.near ? 1.45 : 1);
          ctx.moveTo(sx, m.y);
          ctx.lineTo(sx + m.vx * L * 0.22, m.y + L);
        }
        ctx.stroke();
      }
      ctx.restore();
      return;
    }
    ctx.save();''')
rep('''      const drawAssetBackdrop = (B, g, F, act2, dawn) => {''', '''      // [R33] 4시대 전선 배경 — 원화 1장(1920×1080)을 지평선(y670)에서 하늘 · 땅 두 장으로 나눠 굽고,
      //  하늘 = 느린 시차(0.16) · 땅 = 카메라와 함께(좌우 반전 쌍으로 이어 붙여 이음매 없음) · 구역이 바뀌면 약 1.6초 교차(지금 구역 = 전선)
      //  전선이 바뀌는 순간 그 전선의 날씨로 바꾸고, 거란 전선은 하늘에만 번개(번쩍 · 갈래 번개 · 낮은 천둥)
      const drawFrontBackdrop = (B, g, F) => {
        const zi = g.r33bgForce != null ? g.r33bgForce : Math.max(0, Math.min(3, g.zoneIdx || 0));
        const want = R33_ZONE_BG[zi];
        let st = g.r33bg;
        if (!st || st.era !== g.era || !B.fronts[st.cur]) {
          st = g.r33bg = { era: g.era, cur: want, prev: null, t0: g.tick, z: zi };
          g.weatherMotes = makeMotes({ ...eraObjOf(), weatherType: R33_BG_WEATHER[want] });
          (g.r33bgLog || (g.r33bgLog = [])).push({ bg: want, zone: zi, tick: g.tick, fade: false });
        } else if (st.cur !== want) {
          st.prev = zi > st.z || g.r33bgForce != null ? st.cur : null;
          st.cur = want;
          st.t0 = g.tick;
          st.z = zi;
          g.weatherMotes = makeMotes({ ...eraObjOf(), weatherType: R33_BG_WEATHER[want] });
          (g.r33bgLog || (g.r33bgLog = [])).push({ bg: want, zone: zi, tick: g.tick, fade: !!st.prev });
        }
        const cur = B.fronts[st.cur];
        const prv = st.prev && B.fronts[st.prev];
        const a = prv ? Math.max(0, Math.min(1, (g.tick - st.t0) / R33_BG_FADE)) : 1;
        if (prv && a >= 1) st.prev = null;
        const dpr = F.dpr;
        const z = F.zoom;
        const exact = Math.abs(z - 1) < 1e-3;
        const tx = dpr * (F.cx * (1 - z) + z * F.shX);
        const ty = dpr * (F.cy * (1 - z) + z * F.shY);
        screen.save();
        screen.setTransform(z, 0, 0, z, exact ? Math.round(tx) : tx, exact ? Math.round(ty) : ty);
        // 굽기 배율 = 그리기 배율(dpr 1.5 이하)이면 픽셀 그대로 복사(소프트웨어 래스터에서 더 싸다) · 그보다 크면 부드럽게 확대
        screen.imageSmoothingEnabled = dpr > (cur.d2 || 1) + 0.01;
        const D = (v) => Math.round(v * dpr);
        const Wd = D(VIEW_W);
        const Hd = D(VIEW_H);
        const H0d = D(B.horizon);
        const M = D(60);
        const shaking = Math.abs(F.shY) > 0.4 || !exact;
        const strip = (img, par, yd, hd) => {
          const P2 = 2 * Wd;
          const off = (F.camRX * par * dpr % P2 + P2) % P2;
          const x0 = -Math.round(off);
          for (let k = -1; k <= 1; k++) {
            const xa = x0 + k * P2;
            if (!(xa > Wd + M || xa + Wd < -M)) screen.drawImage(img, xa, yd, Wd, hd);
            const xb = xa + Wd;
            if (!(xb > Wd + M || xb + Wd < -M)) {
              screen.save();
              screen.translate(xb + Wd, 0);
              screen.scale(-1, 1);
              screen.drawImage(img, 0, yd, Wd, hd);
              screen.restore();
            }
          }
        };
        const layer = (L, al) => {
          screen.globalAlpha = al;
          if (shaking) {
            screen.drawImage(L.sky, 0, 0, L.sky.width, 2, -M, -M, Wd + 2 * M, M + 1);
            screen.drawImage(L.ground, 0, L.ground.height - 2, L.ground.width, 2, -M, Hd - 1, Wd + 2 * M, M);
          }
          if (!PERF_OFF.far) strip(L.sky, R33_BG_PAR, 0, H0d + D(2));
          if (!PERF_OFF.ground) strip(L.ground, 1, H0d, Hd - H0d);
        };
        if (prv) layer(prv, 1);
        layer(cur, a);
        screen.globalAlpha = 1;
        if (st.cur === "khitan" && !PERF_OFF.weather) {
          const LB = g.r33bolt || (g.r33bolt = { next: g.tick + 140, t0: -99, seed: 12345, x: 480 });
          if (g.tick >= LB.next) {
            LB.t0 = g.tick;
            LB.seed = LB.seed * 16807 % 2147483647;
            LB.next = g.tick + 210 + LB.seed % 250;
            LB.x = 110 + LB.seed % 740;
            g.r33bolts = (g.r33bolts || 0) + 1;
            if ((g.r33bolts & 1) === 1) sfx("stomp");
          }
          const age = g.tick - LB.t0;
          if (age >= 0 && age < 14) {
            const fl = age < 3 ? 1 : age < 6 ? 0.35 : age < 8 ? 0.8 : Math.max(0, 1 - (age - 8) / 6);
            screen.globalCompositeOperation = "lighter";
            // 하늘 전체 칠하기 대신 번개 둘레만 빛 번짐(채우는 면적 약 1/3)
            screen.globalAlpha = 0.55 * fl;
            screen.drawImage(getGlowSprite("#c7d2fe"), D(LB.x - 300), -M, D(600), H0d + M);
            screen.globalAlpha = 1;
            screen.strokeStyle = `rgba(235,240,255,${(0.9 * fl).toFixed(3)})`;
            screen.lineWidth = D(2.2);
            screen.lineJoin = "round";
            screen.beginPath();
            let bx = D(LB.x);
            let by = -M;
            screen.moveTo(bx, by);
            let r = LB.seed;
            for (let i = 0; i < 9; i++) {
              r = r * 48271 % 2147483647;
              bx += D(r % 41 - 20);
              by += H0d * 0.72 / 9;
              screen.lineTo(bx, by);
            }
            screen.stroke();
            screen.globalCompositeOperation = "source-over";
          }
        }
        // 지평선 이음매(하늘 · 땅 시차가 달라 생기는 경계)를 그 전선 지평선 평균색의 옅은 안개 띠로 감춘다
        const y0 = H0d - D(9);
        const y1 = H0d + D(9);
        const mc = cur.mist || "4,6,12";
        const gb = screen.createLinearGradient(0, y0, 0, y1);
        gb.addColorStop(0, `rgba(${mc},0)`);
        gb.addColorStop(0.5, `rgba(${mc},0.78)`);
        gb.addColorStop(1, `rgba(${mc},0)`);
        screen.fillStyle = gb;
        screen.fillRect(-M, y0, Wd + 2 * M, y1 - y0);
        screen.restore();
        g._r33bgState = { cur: st.cur, prev: st.prev, a: Math.round(a * 100) / 100 };
        return 1;
      };
      const drawAssetBackdrop = (B, g, F, act2, dawn) => {
        if (B.fronts) return drawFrontBackdrop(B, g, F);''')

# ───────── 4. 4대 보스 · 전선 = 구역(Z4 왜구 · 홍건적 웨이브 → 최종 보스) · 체력 · 2페이즈 · 예고 문구 ─────────
rep('''  ];
  var ERA_LIGHT = {''', '''  ];
  // [R33] 4시대 최종 보스 = 홍건적 대장 파두반(1361 개경 함락) — 왜구 무리까지 거느린 '연합 대장'은 게임 설정
  ERAS_DATA[3].bossName = "홍건적 대장 파두반";
  ERAS_DATA[3].bossTitle = "1361년 개경을 함락한 홍건적의 장수 — 남해의 왜구까지 끌어모은 침략군 연합 대장(게임 설정)";
  var ERA_LIGHT = {''')
rep('''  var R31_WAVE_FRONT = [["khitan", "khitan", "khitan"], ["jurchen", "jurchen", "mongol"], ["wakou", "redturban", "redturban"]];''',
    '''  // [R33] 전선 = 구역: Z1 거란 ×2 → Z2 여진 ×2 → Z3 몽골 ×2 → Z4 왜구 · 홍건적 (각 구역 끝 = 전선 보스, Z4 끝 = 최종 보스 파두반)
  var R31_WAVE_FRONT = [["khitan", "khitan"], ["jurchen", "jurchen"], ["mongol", "mongol"], ["wakou", "redturban"]];''')
rep('''  var ERA4_ZONE_WAVES = [
    [6, 7, 5],
    [7, 8, 6],
    [8, 8, 7]
  ];''', '''  // [R33] 구역마다 2웨이브(총 58명 — R31 62명 + 천호장 대신 전선 보스 3 + 최종 보스) · Z4도 웨이브 뒤 보스
  var ERA4_ZONE_WAVES = [
    [6, 7],
    [7, 8],
    [7, 7],
    [8, 8]
  ];''')
rep('''  var ERA4_BOSS_HP_MULT = 1.7;''', '''  var ERA4_BOSS_HP_MULT = 1.7;
  // [R33] 앞 전선 보스 셋이 생겨 최종 보스 파두반 체력(목표 처치 시간)은 R31 공성 사령관의 85%
  var R33_FINAL_HP = 0.85;
  var R33_BOSS_LABELS = { slash: "파두반 쌍도 참격!", bombard: "홍건적 화공 포격!" };''')
rep('''  var MOUNTED_CAP = { 4: { 1: 4 }, 5: { 2: 3 } };''', '''  var MOUNTED_CAP = { 4: { 1: 4, 2: 4 }, 5: { 2: 3 } };''')
rep('''    4: ["flame", "bombard", "stomp"],''', '''    4: ["slash", "charge", "bombard", "slash", "stomp"],''')
rep('''        hpK = R25_TTK.boss * R25_CURVE.boss[e] * (R25_LONGWAR[era] || 1) * POWER_REF / base0;''',
    '''        hpK = R25_TTK.boss * R25_CURVE.boss[e] * (R25_LONGWAR[era] || 1) * POWER_REF / base0 * (era === 4 ? R33_FINAL_HP : 1);''')
rep('''      sheets.boss.kind = { 2: "hanwu", 3: "cavalry", 4: "siege", 5: "bannerman", 6: "mech" }[era];''',
    '''      sheets.boss.kind = { 2: "hanwu", 3: "cavalry", 4: "paduban", 5: "bannerman", 6: "mech" }[era];''')
rep('''      const front = g.era === 4 && g.zoneIdx < 3 && !roles;''', '''      const front = g.era === 4 && g.zoneIdx < 4 && !roles;''')
rep('''      if (era === 4 && zi === 0) {
        g.front4 = null;''', '''      if (era === 4 && zi === 0) {
        g.r33final = false;
        g.r33midDone = {};
        g.front4 = null;''')
rep('''      if (era === 4 && zi === 3) addTimer(90, () => setCompanionBubble("📜 1362년 고려군은 홍건적에게 빼앗긴 개경을 되찾았어요. 이제 침략군의 철갑 공성 사령관만 남았어요!", 200));''',
    '''      if (era === 4 && zi === 3) addTimer(90, () => setCompanionBubble("📜 1361년 홍건적이 개경까지 쳐들어왔어요. 남쪽 바닷가에선 왜구가 날뛰어요 — 두 적을 막아 내고 개경을 되찾아요!", 200));''')
rep('''      if (zi === 3) {
        g.waves = [];
        spawnEraBoss();
      }''', '''      // [R33] 4시대 Z4는 왜구 · 홍건적 웨이브를 먼저 막고 나서 최종 보스(아래 LOCKED 단계)
      if (zi === 3 && era !== 4) {
        g.waves = [];
        spawnEraBoss();
      }''')
rep('''            } else if (g.era >= 2 && midbossFor(g.era, g.zoneIdx) && !(g.midSpawned || {})[g.zoneIdx]) {
              (g.midSpawned || (g.midSpawned = {}))[g.zoneIdx] = true;
              g.midBossSpawned = true;
              spawnEraMidBoss(midbossFor(g.era, g.zoneIdx));
            } else {
              // [R31] 4시대: 구역이 정리되면 진행 중인 전선 미션 판정(몽골 · 홍건적)
              if (g.era === 4 && g.front4) r31FrontEnd(g, g.front4);''', '''            } else if (g.era >= 2 && midbossFor(g.era, g.zoneIdx) && !(g.midSpawned || {})[g.zoneIdx]) {
              (g.midSpawned || (g.midSpawned = {}))[g.zoneIdx] = true;
              g.midBossSpawned = true;
              spawnEraMidBoss(midbossFor(g.era, g.zoneIdx));
              r33MidIntro(g, midbossFor(g.era, g.zoneIdx));
            } else if (g.era === 4 && g.zoneIdx === 3 && !g.r33final) {
              // [R33] Z4 왜구 · 홍건적 웨이브를 모두 막으면 최종 보스 파두반 강림(전선 미션 판정 먼저)
              g.r33final = true;
              if (g.front4) r31FrontEnd(g, g.front4);
              spawnEraBoss();
              (g.r33bossLog || (g.r33bossLog = [])).push({ key: "paduban", ev: "spawn", tick: g.tick });
              addTimer(110, () => setCompanionBubble("📜 파두반은 1361년 개경을 빼앗은 홍건적의 장수예요. 이듬해(1362) 고려군이 개경을 되찾았어요 — 그 싸움을 우리가 끝내요!", 230));
            } else {
              // [R31] 4시대: 구역이 정리되면 진행 중인 전선 미션 판정(몽골 · 홍건적)
              if (g.era === 4 && g.front4) r31FrontEnd(g, g.front4);
              if (g.era === 4 && g.zoneIdx <= 2) r33MidDefeated(g, g.zoneIdx);''')
rep('''    const r31EnterFront = (key) => {''', '''    // [R33] 전선 보스 등장(역사 한 줄 토스트) · 격파(선녀 역사 해설)
    const r33MidIntro = (g, M) => {
      if (!M || !M.toast) return;
      setStageToast({ era: g.era, fieldName: M.toast[0], name: M.name, detail: M.toast[1] });
      setTimeout(() => setStageToast((t) => t && t.fieldName === M.toast[0] ? null : t), 2600);
      (g.r33bossLog || (g.r33bossLog = [])).push({ key: M.key, ev: "spawn", tick: g.tick });
    };
    const r33MidDefeated = (g, zi) => {
      const M = (MIDBOSS_R33[g.era] || []).find((m) => m.zone === zi);
      if (!M || (g.r33midDone || (g.r33midDone = {}))[M.key]) return;
      g.r33midDone[M.key] = true;
      (g.r33bossLog || (g.r33bossLog = [])).push({ key: M.key, ev: "down", tick: g.tick });
      addTimer(30, () => setCompanionBubble(M.fairy, 230));
    };
    const r31EnterFront = (key) => {''')
# 전선 보스 2페이즈(체력 50%) · 예고 문구
rep('''        if (M && M.aura === "baesu" && !en.baesu && en.hp <= en.maxHp * 0.5) {''', '''        // [R33] 전선 보스 2페이즈(체력 50% 이하) — 패턴 교체(연격) · 포효 · 섬광 · 이동 속도 ×1.15
        if (M && M.p2 && !en.r33p2 && en.hp <= en.maxHp * 0.5 && en.state !== "DYING") {
          en.r33p2 = true;
          en.mid = Object.assign({}, M, { patterns: M.p2 });
          en.patIdx = 0;
          en.speed *= 1.15;
          en.attackCooldown = Math.min(en.attackCooldown || 0, 24);
          sfx("bossRoar");
          addShock(en.x, en.z, M.color || "#f87171", 210, 22);
          addTrauma(0.45);
          g.flashAlpha = Math.max(g.flashAlpha, 0.3);
          g.flashColor = "#fecaca";
          setPlayerBubble(M.p2line || "🔥 2페이즈!", 120);
          (g.r33bossLog || (g.r33bossLog = [])).push({ key: M.key, ev: "p2", tick: g.tick });
        }
        if (M && M.aura === "baesu" && !en.baesu && en.hp <= en.maxHp * 0.5) {''')
rep('''        const M = en.mid;
        const pat = M.patterns[en.patIdx % M.patterns.length];''', '''        const M = en.mid;
        const pat = M.patterns[en.patIdx % M.patterns.length];
        const _t0 = g.mobTele ? g.mobTele.length : 0;''')
rep('''        en.uBusy = first + 4;
        en.windupTimer = Math.min(first, 34);
        sfx("alarm");
      };''', '''        // [R33] 전선 보스: 역사 장수의 기술 이름으로 예고 문구 바꿈
        if (M.labels && M.labels[pat] && g.mobTele) for (let i = _t0; i < g.mobTele.length; i++) g.mobTele[i].label = M.labels[pat];
        en.uBusy = first + 4;
        en.windupTimer = Math.min(first, 34);
        sfx("alarm");
      };''')
rep('''                  if (pat !== "stomp") startBossSignature(g, b, p, pat);''', '''                  if (pat !== "stomp") {
                    const _bt0 = g.bossTele ? g.bossTele.length : 0;
                    startBossSignature(g, b, p, pat);
                    // [R33] 4시대 최종 보스 파두반 — 예고 문구
                    const LB4 = g.era === 4 && R33_BOSS_LABELS[pat];
                    if (LB4 && g.bossTele) for (let i = _bt0; i < g.bossTele.length; i++) if (g.bossTele[i].label) g.bossTele[i].label = LB4;
                  }''')
# 자세: walk 1장 배우(idle ↔ walk 교차) · 전선 보스 3인 공용 · 파두반
rep('''        if (walkArt) o.name = beat & 1 ? "walk2" : "walk1";''', '''        if (walkArt) o.name = beat & 1 ? "walk2" : "walk1";
        else if (A && A.frames.walk) o.name = beat & 1 ? "walk" : "idle";''')
rep('''      const BOSS_POSE = { tiger: tigerPose, golem: golemPose, hanwu: hanwuPose, cavalry: cavalryPose, siege: siegePose, bannerman: bannermanPose, mech: mechPose };''',
    '''      // [R33] 4시대 전선 보스 3인(소손녕 · 아골타 · 살리타이) 공용 자세 — idle / walk / slash / hit
      const r33MidPose = (en, g) => {
        const o = { name: "idle", sx: 1, sy: 1, rot: 0, lift: 0, dx: 0 };
        if (en.state === "DYING" || en.state === "KNOCKDOWN") {
          o.name = "hit";
          o.rot = -0.08;
          o.sy = 0.96;
        } else if (en.state === "SPAWN") o.name = "idle";
        else if (en.hitStun > 10) o.name = "hit";
        else if (en.charge) {
          o.name = "slash";
          o.rot = 0.04;
          o.dx = 8;
        } else if (en.windupTimer > 0) {
          o.rot = -0.05;
          o.sy = 1.03;
          o.dx = -4;
        } else if (en.atkAnim > 0) {
          const k = en.atkAnim / 14;
          o.name = "slash";
          o.rot = 0.04 * k;
          o.dx = 10 * k;
        } else if (en.uBusy > 0 && en.curPat === "volley") {
          o.name = "slash";
          o.sy = 1 + 8e-3 * Math.sin(g.rtick * 0.7);
        } else if (en.moving) bigWalk(o, en);
        else breathe(o, g.rtick, 0.08, 0.012);
        return o;
      };
      MID_POSE.MB_SOSON = MID_POSE.MB_AGUDA = MID_POSE.MB_SARTAI = r33MidPose;
      // [R33] 최종 보스 파두반(쌍도) — 돌진 · 참격 = slash · 예비 동작 = 젖힘 · 걷기 = idle ↔ walk
      const padubanPose = (b, g) => {
        const o = { name: "idle", sx: 1, sy: 1, rot: 0, lift: 0 };
        if (b.dying || b.hitStun > 10) o.name = "hit";
        else if (b.charge) {
          o.name = "slash";
          o.rot = 0.05;
        } else if (b.chargePending) {
          o.rot = -0.07;
          o.sy = 1.03;
        } else if (b.atkAnim > 0) {
          o.name = "slash";
          const k = b.atkAnim / 20;
          o.sx = 1 + 0.03 * k;
          o.sy = 1 - 0.05 * k;
        } else if (b.windupTimer > 0) {
          o.rot = -0.05;
          o.sy = 1.03;
        } else if (b.moving) bigWalk(o, b);
        else breathe(o, g.rtick, 0.05, 0.01);
        return o;
      };
      const BOSS_POSE = { tiger: tigerPose, golem: golemPose, hanwu: hanwuPose, cavalry: cavalryPose, siege: siegePose, bannerman: bannermanPose, mech: mechPose, paduban: padubanPose };''')
rep('''            const M = [MIDBOSS_SPECS[g.era], MIDBOSS_EXTRA[g.era]].find((m) => m && m.key === key);''',
    '''            const M = [MIDBOSS_SPECS[g.era], MIDBOSS_EXTRA[g.era], ...MIDBOSS_R33[g.era] || []].find((m) => m && !m.ref && m.key === key);''')

# ───────── 5. 부처님의 가호(팔만대장경 강림) — 삭제 없이 경건 · 신비 연출로 전면 업그레이드 ─────────
#  종소리(buddha_temple_bell) → 0.3초 뒤 차임(buddha_mystic_chime) · 은은한 황금빛 암전 · 부처님 뒤 연꽃 광륜이 천천히 회전 ·
#  손바닥 빛기둥이 하늘에서 보스 위로 수직 강림(결계 파쇄 순간 번쩍) · 대장경 두루마리가 주인공을 감싸며 상승 — ctx.filter 없음, 알파 · 가산 합성만
rep('''      b.charge = b.chargePending = null;
      sfx("ult");''', '''      b.charge = b.chargePending = null;
      // [R33] 경건한 범종 → 0.3초 뒤 신비로운 차임
      sfx("buddhaBell");
      setTimeout(() => sfx("buddhaChime"), 300);
      const RB = g._r33buddha || (g._r33buddha = { n: 0 });
      RB.n++;
      RB.bell = performance.now();''')
rep('''        sky.addColorStop(0, `rgba(8,6,20,${(0.66 * dark).toFixed(3)})`);
        sky.addColorStop(0.62, `rgba(8,6,20,${(0.3 * dark).toFixed(3)})`);
        sky.addColorStop(1, `rgba(8,6,20,${(0.1 * dark).toFixed(3)})`);''', '''        // [R33] 보랏빛 암전 → 은은한 황금빛 암전(위는 깊게 · 아래는 옅게) + 금빛 가산 한 겹
        sky.addColorStop(0, `rgba(30,20,4,${(0.64 * dark).toFixed(3)})`);
        sky.addColorStop(0.62, `rgba(26,16,3,${(0.32 * dark).toFixed(3)})`);
        sky.addColorStop(1, `rgba(18,12,2,${(0.12 * dark).toFixed(3)})`);''')
rep('''        ctx.fillStyle = sky;
        ctx.fillRect(0, 0, VIEW_W, VIEW_H);
        ctx.globalCompositeOperation = "lighter";
        ctx.globalAlpha = Math.min(1, k * 1.4) * fade * (0.7 + 0.2 * Math.sin(t * 0.16) + burst * 0.6);''', '''        ctx.fillStyle = sky;
        ctx.fillRect(0, 0, VIEW_W, VIEW_H);
        ctx.globalCompositeOperation = "lighter";
        ctx.fillStyle = `rgba(251,191,36,${(0.07 * dark).toFixed(3)})`;
        ctx.fillRect(0, 0, VIEW_W, VIEW_H);
        ctx.globalAlpha = Math.min(1, k * 1.4) * fade * (0.7 + 0.2 * Math.sin(t * 0.16) + burst * 0.6);''')
rep('''        screen.globalAlpha = Math.min(1, k * 2) * fade;
        screen.drawImage(FXA.img, cx - FXA.w / 2, cy - FXA.h / 2, FXA.w, FXA.h);''', '''        // [R33] 연꽃 광륜(fx_buddha_lotus_halo) — 부처님 뒤에서 장엄하게 천천히 회전(약 15°/초) · 가산 합성 · 숨 쉬듯 밝기
        const LH = frameAssets.fx && frameAssets.fx.fx_buddha_lotus_halo;
        if (LH) {
          screen.save();
          screen.globalCompositeOperation = "lighter";
          screen.globalAlpha = Math.min(1, k * 1.6) * fade * (0.72 + 0.14 * Math.sin(t * 0.07) + burst * 0.3);
          screen.translate(cx, cy);
          screen.rotate(t * 45e-4);
          const hw = LH.w * (0.9 + 0.1 * ease);
          screen.drawImage(LH.img, -hw / 2, -hw / 2, hw, hw);
          screen.restore();
          (g._assetSeen || (g._assetSeen = {}))["fx:fx_buddha_lotus_halo"] = g.tick;
        }
        screen.globalAlpha = Math.min(1, k * 2) * fade;
        screen.drawImage(FXA.img, cx - FXA.w / 2, cy - FXA.h / 2, FXA.w, FXA.h);''')
rep('''        if (FXA && g._buddhaBeam) {
          drawBuddhaBeams(g, t, g._buddhaBeam.cx, g._buddhaBeam.y0, g._buddhaBeam.fade);
          return;
        }''', '''        if (FXA && g._buddhaBeam) {
          // [R33] 손바닥 빛기둥 · 대장경 두루마리(HD 덧그리기) — 새 원화가 없으면 R25 빛줄기 그대로
          const FX = frameAssets.fx;
          if (FX.fx_buddha_palm_light || FX.fx_tripitaka_scrolls) {
            const fd = g._buddhaBeam.fade;
            overlay.push((o) => drawR33BuddhaFx(g, o, t, fd));
          } else drawBuddhaBeams(g, t, g._buddhaBeam.cx, g._buddhaBeam.y0, g._buddhaBeam.fade);
          return;
        }''')
rep('''      const drawBuddhaFx = (g) => {''', '''      // [R33] 부처님의 가호 HD 덧그리기(세계 좌표) — 손바닥 빛기둥: 28틱부터 하늘에서 보스 발밑까지 수직 강림 → 결계 파쇄(BUDDHA_HIT_AT) 순간 번쩍 → 머물다 흐려짐
      //  대장경 두루마리: 주인공 발밑에서 두 겹(좌우 반전 · 26틱 엇갈림)이 휘감듯(가로 폭 맥동) 떠오르며 사라짐
      const drawR33BuddhaFx = (g, S, t, fade) => {
        const FX = frameAssets.fx || {};
        const PL = FX.fx_buddha_palm_light;
        const TS = FX.fx_tripitaka_scrolls;
        const b = g.boss;
        const p = g.player;
        const H = BUDDHA_HIT_AT;
        const RB = g._r33buddha || (g._r33buddha = { n: 0 });
        S.save();
        if (PL && b) {
          const t0 = 28;
          const u = Math.max(0, Math.min(1, (t - t0) / (H - t0)));
          const e = 1 - (1 - u) * (1 - u) * (1 - u);
          const hold = t >= H ? Math.max(0, 1 - (t - H - 34) / 26) : 1;
          const a = Math.min(1, u * 2.2) * hold * fade;
          if (a > 0.01) {
            const w = PL.w;
            const h = PL.h;
            const footY = b.z + 8;
            const y = footY - h - (1 - e) * (footY + 60);
            S.globalCompositeOperation = "lighter";
            S.globalAlpha = a * (0.86 + 0.14 * Math.sin(t * 0.3));
            S.drawImage(PL.img, b.x - w / 2, y, w, h);
            if (t >= H && t < H + 20) {
              S.globalAlpha = a * (1 - (t - H) / 20);
              S.drawImage(PL.img, b.x - w * 0.6, y - 12, w * 1.2, h + 12);
            }
            RB.palm = (RB.palm || 0) + 1;
          }
        }
        if (TS && p) {
          for (let j = 0; j < 2; j++) {
            const tt = t - 10 - j * 26;
            const life = 112;
            if (tt < 0 || tt >= life) continue;
            const v = tt / life;
            const al = (v < 0.15 ? v / 0.15 : v > 0.7 ? (1 - v) / 0.3 : 1) * fade * 0.9;
            const sc = (0.78 + 0.3 * v) * (j ? 0.86 : 1);
            const w = TS.w * sc;
            const h = TS.h * sc;
            const x = p.x + (j ? -14 : 10);
            const y = p.z - p.y - h * 0.6 - v * 120;
            S.save();
            S.translate(x, y + h / 2);
            S.scale((j ? -1 : 1) * (0.86 + 0.14 * Math.cos(tt * 0.09)), 1);
            S.globalCompositeOperation = "source-over";
            S.globalAlpha = al;
            S.drawImage(TS.img, -w / 2, -h / 2, w, h);
            S.globalCompositeOperation = "lighter";
            S.globalAlpha = al * 0.35;
            S.drawImage(TS.img, -w / 2, -h / 2, w, h);
            S.restore();
            RB.scroll = (RB.scroll || 0) + 1;
          }
        }
        S.restore();
        RB.halo = !!FX.fx_buddha_lotus_halo;
        (g._assetSeen || (g._assetSeen = {}))["fx:buddha_r33"] = g.tick;
      };
      const drawBuddhaFx = (g) => {''')

# ───────── 6. R32 원화 연결(척준경 무신 4자세 · 이펙트 4 · 효과음 / 김원봉 총기 4자세 · 총소리) ─────────
rep('''bombBlast: "bomb_uiyeol_blast" };''', '''bombBlast: "bomb_uiyeol_blast", buddhaBell: "buddha_temple_bell", buddhaChime: "buddha_mystic_chime", bladeSlash1: "blade_slash_1", bladeSlash2: "blade_slash_2", bladeArmor: "blade_armor_cleave", dragonRoar: "dragon_roar_slash", gunPistol: "gun_pistol_crisp", gunRifle: "gun_rifle_heavy" };''')
rep('''bombBlast: 0.85 };''', '''bombBlast: 0.85, buddhaBell: 0.9, buddhaChime: 0.8, bladeSlash1: 0.7, bladeSlash2: 0.7, bladeArmor: 0.85, dragonRoar: 0.85, gunPistol: 0.7, gunRifle: 0.85 };''')
rep('''bombBlast: 2 };''', '''bombBlast: 2, buddhaBell: 1, buddhaChime: 1, bladeSlash1: 3, bladeSlash2: 3, bladeArmor: 2, dragonRoar: 1, gunPistol: 3, gunRifle: 1 };''')
rep('''bombBlast: 0.04 };''', '''bombBlast: 0.04, bladeSlash1: 0.06, bladeSlash2: 0.06, bladeArmor: 0.03, gunPistol: 0.05 };''')
rep('''bombBlast: "explosion" };''', '''bombBlast: "explosion", buddhaBell: "ult", buddhaChime: "levelup", bladeSlash1: "hit", bladeSlash2: "hit", bladeArmor: "crit", dragonRoar: "ult", gunPistol: "shot", gunRifle: "explosion" };''')
rep('''        else if (g._comboStep >= 1) sfx((g._r31alt = !g._r31alt) ? "sliceCrisp1" : "sliceCrisp2");''',
    '''        else if (g._comboStep >= 1) sfx((g._r31alt = !g._r31alt) ? g.era === 4 ? "bladeSlash1" : "sliceCrisp1" : g.era === 4 ? "bladeSlash2" : "sliceCrisp2");''')
rep('''          g.gunShots = (g.gunShots || 0) + 1;
          sfx("shot");''', '''          g.gunShots = (g.gunShots || 0) + 1;
          sfx(g.era === 6 ? "gunPistol" : "shot");''')
rep('''      sfx("shot");
      g.airMauser = (g.airMauser || 0) + 1;''', '''      sfx("gunPistol");
      g.airMauser = (g.airMauser || 0) + 1;
      // [R33] 공중 모젤 = 쌍권총(dual) 자세
      g.player._r31pose = { name: "dual", until: g.tick + 16, lift: 0 };
      const E6 = g.r33e6 || (g.r33e6 = {});
      E6.dual = (E6.dual || 0) + 1;''')
rep('''      g.uiyeolThrows = (g.uiyeolThrows || 0) + 1;
      sfx("throw");''', '''      g.uiyeolThrows = (g.uiyeolThrows || 0) + 1;
      sfx("throw");
      // [R33] 폭탄 투척(bomb) 자세
      p._r31pose = { name: "bomb", until: g.tick + 14, lift: 0 };
      const E6 = g.r33e6 || (g.r33e6 = {});
      E6.bomb = (E6.bomb || 0) + 1;''')
rep('''          o.lift = 5 * Math.min(1, (RP.until - g.tick) / 8);''', '''          o.lift = (RP.lift != null ? RP.lift : 5) * Math.min(1, (RP.until - g.tick) / 8);''')
rep('''        if (shoot) base = sp.shoot || "atk2";''', '''        if (shoot) base = sp.shoot2 && F[sp.shoot2] ? sp.shoot2 : sp.shoot || "atk2";''')
rep('''atk: { melee: ["atk1"], shoot: "atk2" }, swing: { atk1: { c: [300, 222], r: 182, a: [-45, 150] } } },''',
    '''atk: { melee: ["atk1"], shoot: "atk2", shoot2: "pistol" }, swing: { atk1: { c: [300, 222], r: 182, a: [-45, 150] } } },''')
rep('''        // [R25] 4타 피니시 전용 사슬(fin) · 연격만 melee 순서를 따르고, 돌진(atk1) · 어퍼(atk2)는 자기 동작을 쓴다
        let base;''', '''        // [R33] 4시대 척준경 무신 자세(R32 원화) — 돌진 = charge · 3타 = cleave_prep → cleave_hit(갑옷 쪼개기)
        if (F.cleave_hit && F.cleave_prep && !shoot) {
          if (p._atkSrc === "dash" && F.charge) return { prep: "charge", chain: ["charge"], key: "atk1", shoot: false };
          if (p._atkSrc === "combo" && p.comboStep === 3 && !p.rush) return { prep: "cleave_prep", chain: ["cleave_hit"], key: "atk3", shoot: false };
        }
        // [R25] 4타 피니시 전용 사슬(fin) · 연격만 melee 순서를 따르고, 돌진(atk1) · 어퍼(atk2)는 자기 동작을 쓴다
        let base;''')
rep('''    // 2시대 3타 — 호랑이 발톱 강타(heavy_cleave 자세 + fx_tiger_claw)''', '''    // [R33] 4시대 척준경 무신(R32 원화) — 3타 갑옷 쪼개기(cleave_hit + fx_armor_break + 갑옷 가르는 소리) · 돌진 = 요새 충차(charge + fx_fortress_ram) ·
    //  일섬 · 각성 = 청룡(dragon_stance + fx_azure_dragon + 용의 포효 베기) · 질풍연참 = 칼날 폭풍(fx_blade_storm) · 일반 베기 = blade_slash_1/2
    const r33Cleave = () => {
      const g = gameRef.current;
      const p = g.player;
      const x = p.x + p.facing * 104;
      pushArtFx("fx_armor_break", x, p.z - p.y - 58, { k: "burst", dur: 460, dir: p.facing });
      r31Hfx(4, x, p.z - 4, 300, { c: "#93c5fd", s: 1.25 });
      sfx("bladeArmor");
      addTrauma(0.18);
      g.r33cleaves = (g.r33cleaves || 0) + 1;
    };
    const r33Ram = () => {
      const g = gameRef.current;
      const p = g.player;
      pushArtFx("fx_fortress_ram", p.x + p.facing * 70, p.z - p.y - 52, { k: "ram", dur: 420, dir: p.facing });
      g.r33rams = (g.r33rams || 0) + 1;
    };
    const r33Dragon = (ult) => {
      const g = gameRef.current;
      const p = g.player;
      p._r31pose = { name: "dragon_stance", until: g.tick + (ult ? 60 : 18), lift: 0 };
      pushArtFx("fx_azure_dragon", p.x + p.facing * 30, p.z - p.y - 96, { k: "dragon", dur: ult ? 1400 : 980, s: ult ? 1.18 : 1, dir: p.facing });
      sfx("dragonRoar");
      g.r33dragons = (g.r33dragons || 0) + 1;
    };
    const r33Storm = () => {
      const g = gameRef.current;
      const p = g.player;
      pushArtFx("fx_blade_storm", p.x + p.facing * 60, p.z - p.y - 64, { k: "storm", dur: 820, dir: p.facing });
      g.r33storms = (g.r33storms || 0) + 1;
    };
    // [R33] 6시대 김원봉 각성 = 소총(rifle 자세) + 묵직한 소총 사격음
    const r33Rifle = () => {
      const g = gameRef.current;
      g.player._r31pose = { name: "rifle", until: g.tick + 54, lift: 0 };
      sfx("gunRifle");
      const E6 = g.r33e6 || (g.r33e6 = {});
      E6.rifle = (E6.rifle || 0) + 1;
    };
    // 2시대 3타 — 호랑이 발톱 강타(heavy_cleave 자세 + fx_tiger_claw)''')
rep('''          chopImpact();
          if (g.era === 2) r31Cleave();''', '''          chopImpact();
          if (g.era === 2) r31Cleave();
          if (g.era === 4) r33Cleave();''')
rep('''      if (g.era === 2) r31Summon(false);
      addTimer(12, () => specialDash(0));''', '''      if (g.era === 2) r31Summon(false);
      if (g.era === 4) r33Dragon(false);
      addTimer(12, () => specialDash(0));''')
rep('''      if (g.era === 2) {
        r31Summon(true);
        r31SkySword(g.cameraX + VIEW_W / 2, 424, 380, true);
      }''', '''      if (g.era === 2) {
        r31Summon(true);
        r31SkySword(g.cameraX + VIEW_W / 2, 424, 380, true);
      }
      if (g.era === 4) r33Dragon(true);
      if (g.era === 6) r33Rifle();''')
rep('''      p._atkSrc = "dash";
      p._fin = false;''', '''      p._atkSrc = "dash";
      p._fin = false;
      if (g.era === 4) r33Ram();''')
rep('''      sfx("sliceFlurry");
      rushSlash(1);''', '''      sfx("sliceFlurry");
      if (g.era === 4) r33Storm();
      rushSlash(1);''')
# 무신 이펙트 4종의 움직임(그리기 공용 함수 drawArtFx에 종류 추가)
rep('''          } else if (e.k === "sword") {''', '''          } else if (e.k === "burst") {
            const g1 = Math.min(1, t / 0.18);
            const sc = 0.6 + 0.55 * (1 - (1 - g1) * (1 - g1));
            w *= sc;
            h *= sc;
            a = t < 0.4 ? 1 : 1 - (t - 0.4) / 0.6;
            glow = t < 0.2 ? 0.8 : 0;
          } else if (e.k === "ram") {
            x += e.dir * 150 * t;
            w *= 0.9 + 0.15 * t;
            h *= 0.9 + 0.15 * t;
            a = t < 0.6 ? 1 : 1 - (t - 0.6) / 0.4;
            glow = t < 0.25 ? 0.35 : 0;
          } else if (e.k === "dragon") {
            const g1 = Math.min(1, t / 0.25);
            const sc = 0.75 + 0.35 * g1;
            w *= sc;
            h *= sc;
            y -= 30 * t;
            a = t < 0.12 ? t / 0.12 : t > 0.7 ? 1 - (t - 0.7) / 0.3 : 1;
            glow = 0.45;
          } else if (e.k === "storm") {
            const sc = 0.7 + 0.45 * Math.min(1, t / 0.3);
            w *= sc;
            h *= sc;
            e._rot = t * 5.5;
            a = t < 0.75 ? 1 : 1 - (t - 0.75) / 0.25;
            glow = 0.3;
          } else if (e.k === "sword") {''')
rep('''          S.translate(x, y);
          if (e.dir < 0) S.scale(-1, 1);''', '''          S.translate(x, y);
          if (e.dir < 0) S.scale(-1, 1);
          if (e._rot) S.rotate(e._rot);''')

# ───────── 7. 검증용 DEV 훅 ─────────
rep('''          r31ult: () => {
            gameRef.current.stats.ult = 100;
            triggerTrueAwakeningUlt();
          },''', '''          r31ult: () => {
            gameRef.current.stats.ult = 100;
            triggerTrueAwakeningUlt();
          },
          // [R33] 검증용 — 전선 배경 강제(0~3 · null = 구역 따라) · 상태 · 전선 보스 즉시 소환 · 최종 보스 소환
          r33bg: (i) => {
            gameRef.current.r33bgForce = i == null ? null : Math.max(0, Math.min(3, i));
            return gameRef.current._r33bgState || null;
          },
          r33: () => {
            const g = gameRef.current;
            return { bg: g._r33bgState || null, bgLog: (g.r33bgLog || []).slice(), bolts: g.r33bolts || 0, weather: g.weatherMotes ? g.weatherMotes.style || "dots" : null, motes: g.weatherMotes ? g.weatherMotes.length : 0, bossLog: (g.r33bossLog || []).slice(), final: !!g.r33final, buddha: g._r33buddha ? Object.assign({}, g._r33buddha) : null, e4: { cleaves: g.r33cleaves || 0, rams: g.r33rams || 0, dragons: g.r33dragons || 0, storms: g.r33storms || 0 }, e6: Object.assign({}, g.r33e6 || {}) };
          },
          r33mid: (key) => {
            const g = gameRef.current;
            const M = (MIDBOSS_R33[g.era] || []).find((m) => m.key === key);
            if (!M) return null;
            spawnEraMidBoss(M);
            r33MidIntro(g, M);
            return g.enemies.find((e) => e.isMidBoss && e.mid === M) || null;
          },
          r33final: () => {
            const g = gameRef.current;
            g.r33final = true;
            spawnEraBoss();
            return !!g.boss;
          },''')

# ───────── 8. 결계 문구(옛 철갑 공성 사령관 → 파두반) · 검증용 피해 훅 ─────────
B = chr(92)


def esc(t):
    """실제 글자 → 파일 속 \\uXXXX 표기(원본이 이스케이프로 저장된 문구 찾기용)."""
    return "".join(B + "u%04X" % ord(c) if ord(c) > 127 else c for c in t)


rep(esc("철벽 공성 결계"), "홍건적 요술 결계", 3)
rep('''          r33final: () => {''', '''          r33hp: (which, frac) => {
            const g = gameRef.current;
            const T = which === "boss" ? g.boss : g.enemies.find((e) => e.isMidBoss && e.state !== "DYING");
            if (!T) return null;
            T.hp = Math.max(1, Math.round(T.maxHp * frac));
            return T.hp;
          },
          r33kill: (which) => {
            const g = gameRef.current;
            const T = which === "boss" ? g.boss : g.enemies.find((e) => e.isMidBoss && e.state !== "DYING");
            if (!T) return false;
            T.hp = 1;
            T.guardTimer = 0;
            T.guardRate = 0;
            if (T.fortress) T.fortress = null;
            applyDamageToEnemy(T, 1, 4, 0, 1, false, 1);
            return true;
          },
          r33final: () => {''')

open(P, "w", encoding="utf-8").write(s)
print("R33 patch ok —", n, "edits")
