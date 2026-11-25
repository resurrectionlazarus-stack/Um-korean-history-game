#!/usr/bin/env python3
"""R27 2차(디렉터 추가 지시서) — 4~6시대 일반 몹 6종 원화 연결(이미 톤다운된 원본은 굽기 톤다운 생략) ·
   리얼 전투 효과음 WAV 6종(첫 입력 때 디코딩 캐시 · 동시 발음 상한 · 합성음 폴백) 트리거 연결."""
import sys

P = sys.argv[1]
s = open(P, encoding="utf-8").read()
n = 0


def rep(old, new, cnt=1):
    global s, n
    c = s.count(old)
    if c != cnt:
        raise SystemExit(f"anchor count {c} != {cnt}: {old[:110]!r}")
    s = s.replace(old, new)
    n += 1


# ───────── 1. MOB_SPEC: 미술팀 파일 이름 → 실제 유닛 키 · 원본 톤다운 표시 ─────────
rep('''    khitan_inf: { era: 4, unit: "KHITAN_INF", h: 140 },
    mongol_rider: { era: 4, unit: "MONGOL_RIDER", h: 168 },''', '''    // [R27 2차] toned: 원본이 이미 12% 저채도 · 어두운 톤 → 굽기 톤다운 생략(이중 톤다운 방지)
    khitan_inf: { era: 4, unit: "KHITAN_INF", h: 140, toned: true },
    mongol_rider: { era: 4, unit: "MONGOL_RIDER", h: 168 },
    // [R27 2차] 미술팀 파일 이름 era4_mongol_cav_* = 몽골 기마 돌격병(MONGOL_RIDER)
    mongol_cav: { era: 4, unit: "MONGOL_RIDER", h: 168, toned: true },''')
rep('''    jp_gunner: { era: 5, unit: "JP_GUNNER", h: 134 },
    samurai: { era: 5, unit: "SAMURAI", h: 140 },''', '''    jp_gunner: { era: 5, unit: "JP_GUNNER", h: 134 },
    // [R27 2차] 미술팀 파일 이름 era5_gunner_* = 임진왜란 조총수(JP_GUNNER)
    gunner: { era: 5, unit: "JP_GUNNER", h: 134, toned: true },
    samurai: { era: 5, unit: "SAMURAI", h: 140, toned: true },''')
rep('''    jp_bayonet: { era: 6, unit: "JP_BAYONET", h: 134 },
    mg_nest: { era: 6, unit: "MG_NEST", h: 110 },''', '''    jp_bayonet: { era: 6, unit: "JP_BAYONET", h: 134, toned: true },
    mg_nest: { era: 6, unit: "MG_NEST", h: 110, toned: true },''')
# 굽기 톤다운: toned 몹 · MANIFEST tone 표식이 있으면 건너뜀
rep('''      // [R27] 일반 몹 명도 12% ↓(굽기 때 1회 · 실행 비용 0) — 주인공이 몹 무리 위로 튀어나오게. 피격 흰 실루엣은 그대로
      {
        const tx = c.getContext("2d");''', '''      // [R27] 일반 몹 명도 12% ↓(굽기 때 1회 · 실행 비용 0) — 주인공이 몹 무리 위로 튀어나오게. 피격 흰 실루엣은 그대로
      //  [R27 2차] 원본이 이미 톤다운된 몹(MOB_SPEC toned · MANIFEST tone 표식)은 건너뜀
      if (!(spec && spec.toned) && (M.meta[poses[i]] || {}).tone !== "low_sat_dark_12pct") {
        const tx = c.getContext("2d");''')
# file:// 내장 목록
rep('''        ...mobFiles(3, "tang_inf"),
        ...mobFiles(3, "cav_archer"),''', '''        ...mobFiles(3, "tang_inf"),
        ...mobFiles(3, "cav_archer"),
        // [R27 2차] 4~6시대 일반 몹 6종(미술팀 파일 이름 그대로)
        ...[[4, "khitan_inf"], [4, "mongol_cav"], [5, "gunner"], [5, "samurai"], [6, "jp_bayonet"], [6, "mg_nest"]].flatMap(([e, k]) => mobFiles(e, k)),''')

# ───────── 2. 효과음 엔진: WAV 6종 ─────────
rep('''    let muted = false;
    let voices = 0;
    const ensure = () => {''', '''    let muted = false;
    let voices = 0;
    // [R27 2차] 리얼 전투 효과음(assets/sfx WAV 6종) — 첫 키 · 터치 입력(오디오 잠금 해제) 때 받아 AudioBuffer로 디코딩해 두고 바로 재생.
    //  소리마다 동시 발음 상한(클리핑 방지) · 타격음은 피치 ±5% 흔들기 · file://이거나 받기/디코딩 실패면 기존 합성음. ?sfx=synth = 합성음만(비교용)
    const SMP = { slashLight: "slash_light", hitHeavy: "hit_heavy", breath: "breath_finisher", parryCounter: "parry_counter", relicAwaken: "relic_awaken", killcam: "killcam_slowmo" };
    const SMP_VOL = { slashLight: 0.7, hitHeavy: 0.75, breath: 0.75, parryCounter: 0.8, relicAwaken: 0.8, killcam: 0.8 };
    const SMP_MAXV = { slashLight: 3, hitHeavy: 3, breath: 2, parryCounter: 2, relicAwaken: 1, killcam: 1 };
    const SMP_JIT = { slashLight: 0.05, hitHeavy: 0.05, breath: 0.03, parryCounter: 0.02 };
    // 샘플을 못 쓸 때의 합성음("" = 소리 없음 · 예전과 같게)
    const SMP_FALLBACK = { slashLight: "hit", hitHeavy: "crit", breath: "", parryCounter: "counter", relicAwaken: "ult", killcam: "" };
    const smpBuf = {};
    const smpLive = {};
    const smpStat = { loaded: 0, failed: 0, played: 0, capped: 0, by: {} };
    let smpTried = false;
    const smpOff = (() => {
      try {
        return location.protocol === "file:" || readQuery().get("sfx") === "synth";
      } catch (e) {
        return true;
      }
    })();
    const loadSamples = () => {
      if (smpTried || smpOff || !ac || typeof fetch !== "function") return;
      smpTried = true;
      Object.keys(SMP).forEach((key) => {
        fetch(`assets/sfx/${SMP[key]}.wav`).then((r) => r.ok ? r.arrayBuffer() : Promise.reject(new Error(String(r.status)))).then((ab) => new Promise((res, rej) => ac.decodeAudioData(ab, res, rej))).then((b) => {
          smpBuf[key] = b;
          smpStat.loaded++;
        }).catch(() => {
          smpStat.failed++;
        });
      });
    };
    const playSample = (name) => {
      const b = smpBuf[name];
      if (!b) return false;
      if ((smpLive[name] || 0) >= (SMP_MAXV[name] || 2)) {
        smpStat.capped++;
        return true;
      }
      const src = ac.createBufferSource();
      src.buffer = b;
      const j = SMP_JIT[name] || 0;
      if (j) src.playbackRate.value = 1 + (Math.random() * 2 - 1) * j;
      const gn = ac.createGain();
      gn.gain.value = SMP_VOL[name] || 0.7;
      src.connect(gn);
      gn.connect(master);
      smpLive[name] = (smpLive[name] || 0) + 1;
      src.onended = () => {
        smpLive[name]--;
      };
      src.start();
      smpStat.played++;
      smpStat.by[name] = (smpStat.by[name] || 0) + 1;
      return true;
    };
    const ensure = () => {''')
rep('''        for (let i = 0; i < len; i++) d[i] = Math.random() * 2 - 1;
      } catch (e) {
        ac = null;
        return false;
      }''', '''        for (let i = 0; i < len; i++) d[i] = Math.random() * 2 - 1;
        loadSamples();
      } catch (e) {
        ac = null;
        return false;
      }''')
rep('''        try {
          (DEFS[name] || DEFS.ui)();
        } catch (e) {
        }''', '''        try {
          if (SMP[name]) {
            if (playSample(name)) return;
            const fb = SMP_FALLBACK[name];
            if (!fb) return;
            DEFS[fb]();
            return;
          }
          (DEFS[name] || DEFS.ui)();
        } catch (e) {
        }''')
rep('''      get bgmStats() {
        return bgmSeq ? bgmSeq.stats : null;
      },''', '''      get bgmStats() {
        return bgmSeq ? bgmSeq.stats : null;
      },
      // [R27 2차] 샘플 효과음 상태(검증용)
      get sampleStats() {
        return { ...smpStat, off: smpOff, tried: smpTried, by: { ...smpStat.by } };
      },''')
rep('''          openMidQuiz: (i) => openMidQuiz(i),''', '''          openMidQuiz: (i) => openMidQuiz(i),
          // [R27 2차] 샘플 효과음 상태(불러온 수 · 재생 수 · 이름별)
          sfxStats: () => sfxRef.current && sfxRef.current.sampleStats,''')

# ───────── 3. 트리거 ─────────
# 연격 1 · 2타 = 기본 검격(slash_light) · 3 · 4타 · 보스 적중 = 강타(hit_heavy)
rep('''        g._bowlFin = isFinisher;''', '''        g._bowlFin = isFinisher;
        g._comboStep = step;''')
rep('''        g._bowlFin = false;''', '''        g._bowlFin = false;
        g._comboStep = 0;''')
rep('''        sfx(isCounter ? "counter" : dealtCrit ? "crit" : "hit");''', '''        sfx(isCounter ? "counter" : target === g.boss || g._comboStep >= 3 ? "hitHeavy" : g._comboStep >= 1 ? "slashLight" : dealtCrit ? "crit" : "hit");''')
# 볼링 넉백 충돌 = 강타
rep('''            addTrauma(0.14);
            sfx("crit");
            if (T.hit.length >= 2) addDamagePopup(''', '''            addTrauma(0.14);
            sfx("hitHeavy");
            if (T.hit.length >= 2) addDamagePopup(''')
# 수묵 · 속성 호흡 피니시(4타 피니시 · 어퍼 · 돌진)
rep('''      g.breathCount = (g.breathCount || 0) + 1;
    };''', '''      if (power > 1) sfx("breath");
      g.breathCount = (g.breathCount || 0) + 1;
    };''')
# 저스트 패링 카운터 일섬
rep('''      g.counterSlashes = (g.counterSlashes || 0) + 1;''', '''      g.counterSlashes = (g.counterSlashes || 0) + 1;
      sfx("parryCounter");''')
# 유물 각성 빛기둥(샘플이 없으면 예전 ult 합성음)
rep('''      addLight(p.x, p.z, 60, 150, R.aura, 1, 30);
      sfx("ult");''', '''      addLight(p.x, p.z, 60, 150, R.aura, 1, 30);
      sfx("relicAwaken");''')
# 킬캠: 구역 마지막 적 · 보스 막타
rep('''              g.killCams = (g.killCams || 0) + 1;''', '''              g.killCams = (g.killCams || 0) + 1;
              sfx("killcam");''')
rep('''      addTrauma(0.55);
      explode(b.x, b.z, 70, 1.8, "#fde047");''', '''      addTrauma(0.55);
      explode(b.x, b.z, 70, 1.8, "#fde047");
      sfx("killcam");''')

open(P, "w", encoding="utf-8").write(s)
print("R27 2차 patch ok —", n, "edits")
