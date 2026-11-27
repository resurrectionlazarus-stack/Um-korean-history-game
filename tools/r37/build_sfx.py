#!/usr/bin/env python3
"""R37 — 리얼리티 효과음 전처리 파이프라인(음향감독 발주서 [작업 1] · [작업 2]).

원본: 신시 효과음.zip(또는 푼 폴더) — 48kHz · 16bit · 스테레오 WAV 104개 · 33개 프리픽스(파일 이름 <prefix>_#<take>-<timestamp>.wav)
결과: <빌드>/assets/sfx/sfx_*.mp3 64개 + <빌드>/assets/sfx/sfx_manifest.json(게임 엔진이 읽는 키 → 파일 · 루프 지점 표)
      + tools/r37/build_sfx_log.json(파일마다 트림 전후 길이 · 앞무음 제거량 · 게인 · 리미팅 양 — 검수 보고용)

사용: python -I tools/r37/build_sfx.py <WAV 폴더 또는 zip> <빌드 폴더>
      (Windows: tools/r37/run_py.ps1 로 가상환경 · DLL 경로를 맞춰 실행)

공정(파일마다 · 순서대로)
  1 26Hz 2차 하이패스(DC · 초저역 잡음) → 키 그룹별 EQ(검격 220Hz HPF + 4~7kHz +2.5dB / 돌도끼 1.5~3.5kHz +2dB / 코뿔소 · 말발굽 60~100Hz +2dB · 3kHz 위 -1.5dB)
  2 구간 고르기
      trim    : 앞 무음 = 피크 대비 -32dBFS(또는 절대값 0.025) 최초 돌파 5ms 앞에서 컷 · 뒤 무음 = -42dBFS 마지막 돌파 뒤 40ms만 남김
      natural : 긴 소리(포효 · 총성 · 종) — 가장 센 0.1초 창보다 14dB 아래를 처음 넘는 곳(앞 0.12초 여유)에서 시작 · 24dB 아래로 꺼진 뒤 0.3초에서 끝(상한 있음)
      dense   : 10~25초 클립 — 0.5초 RMS 창으로 가장 밀도 높은 L초 구간만
      loop    : L초 심리스 루프(0.45초 등출력 크로스페이드) — 리듬이 있으면 그 주기의 배수로 L을 맞춤(이음매에서 리듬이 어긋나지 않게) ·
                파일 앞뒤에 0.1초씩 주기 연장을 덧대고 루프 지점(loopStart · loopEnd)을 안쪽에 둠 → MP3 디코더의 앞머리 지연과 무관하게 이음매 없음
      파생     : 흑요석 명중(검격 +10% 피치 + 돌도끼 어택 80ms 30%) · 활 당김(원테이크 앞 1초) · 권총(소총 #2 +18% · 0.55초) · 병사 쓰러짐(갑옷 낙하 0.35초)
  3 3ms 페이드인 · 15~30ms 페이드아웃(자연 끝) / 자른 끝은 더 길게(소리 중간을 끊은 자리라 120~500ms)
  4 44.1kHz 리샘플(폴리페이즈) · 모노(단발) 또는 스테레오(공간감)
  5 RMS 정규화: 카테고리 목표(가장 센 0.4초 창의 RMS) → 피크 -1.0dBFS 룩어헤드 리미터(3ms · 릴리스 60ms).
     리미터가 깎는 양이 상한(타격 5dB · 그 밖 8dB)을 넘으면 게인을 줄여 목표에 못 미치는 만큼을 로그에 적는다(소리를 눌러 뭉개지 않게)
  6 MP3 CBR(lameenc · 모노 112kbps · 스테레오 128kbps · 품질 2). lameenc가 없으면 ffmpeg(libmp3lame)로.
"""
import json
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from fractions import Fraction

import numpy as np
from scipy import signal
from scipy.io import wavfile
from scipy.ndimage import minimum_filter1d, uniform_filter1d

SR_OUT = 44100
CEIL_DB = -1.0
LEAD_REL_DB, LEAD_ABS, LEAD_PRE_MS = -32.0, 0.025, 5
TAIL_DB, TAIL_KEEP_MS = -42.0, 40
FADE_IN_MS, FADE_OUT_MS = 3, 25

# ───────── 카테고리: 목표 RMS(dBFS · 가장 센 0.4초 창) · 스테레오 · kbps · EQ · 리미터 허용량(dB) ─────────
#  win = RMS를 재는 창(초). 타격 · 활 · 총처럼 수십 ms에 에너지가 몰린 소리는 0.1초, 포효 · 함성처럼 이어지는 소리는 0.4초
#  (0.4초 창으로 재면 돌도끼 '퍽'은 피크 -1dB 제약 때문에 목표 RMS에 닿을 수 없다 — 1차 굽기에서 -22dB로 나와 바꿈)
CATS = {
    # [청음 반영 1차] 칼: 목표를 1dB 낮추고(-14.5) 봉우리를 둥글린다(soft) — 고려 · 조선 구간의 '깡깡' 금속성 · 단단한 피크(오너)
    "hit_sword": dict(rms=-14.5, stereo=False, kbps=96, eq="sword", gr=5, win=0.1, soft=1.4),
    "hit_axe": dict(rms=-13.5, stereo=False, kbps=96, eq="axe", gr=5, win=0.1),
    "hit": dict(rms=-13.5, stereo=False, kbps=96, eq=None, gr=5, win=0.1),
    "swing": dict(rms=-15.5, stereo=False, kbps=96, eq=None, gr=5, win=0.1),
    "voice": dict(rms=-15.5, stereo=False, kbps=112, eq=None, gr=8),
    "hero_hit": dict(rms=-13.5, stereo=False, kbps=112, eq=None, gr=8),
    "bow": dict(rms=-15.5, stereo=False, kbps=112, eq=None, gr=6, win=0.1),
    "gun": dict(rms=-13.5, stereo=False, kbps=112, eq=None, gr=5, win=0.1),
    "beast": dict(rms=-15.5, stereo=True, kbps=128, eq=None, gr=8),
    "beast_rhino": dict(rms=-15.5, stereo=True, kbps=128, eq="low", gr=8),
    "beast_big": dict(rms=-13.5, stereo=True, kbps=128, eq=None, gr=8),
    "death": dict(rms=-15.5, stereo=True, kbps=128, eq=None, gr=8),
    "cry": dict(rms=-16.0, stereo=True, kbps=128, eq=None, gr=8),
    "crowd": dict(rms=-19.0, stereo=True, kbps=128, eq=None, gr=8),
    "loop": dict(rms=-19.0, stereo=True, kbps=128, eq=None, gr=8),
    "loop_low": dict(rms=-19.0, stereo=True, kbps=128, eq="low", gr=8),
    "cav": dict(rms=-16.0, stereo=True, kbps=128, eq="low", gr=8),
    "horn": dict(rms=-16.0, stereo=True, kbps=128, eq=None, gr=8),
    "volley": dict(rms=-15.5, stereo=True, kbps=128, eq=None, gr=8),
    "bell": dict(rms=-13.5, stereo=True, kbps=128, eq=None, gr=6),
    "aura": dict(rms=-19.0, stereo=True, kbps=128, eq=None, gr=8),
}

# ───────── 키 표([작업 2]) — 음향감독이 고른 테이크 번호 그대로. mode: trim · natural · dense · loop · crop · 파생 ─────────
K = []


def add(key, src, cat, mode="trim", note="", **p):
    K.append(dict(key=key, src=src, cat=cat, mode=mode, note=note, p=p))


# A. 무기 타격 · 스윙
add("sfx_sword_slash_01", ("ultra_sharp_thin_ste", 3), "hit_sword", note="검격 1(리니지 쾌속)")
add("sfx_sword_slash_02", ("ultra_sharp_thin_ste", 4), "hit_sword", note="검격 2")
add("sfx_sword_slash_03", ("ultra_sharp_thin_ste", 1), "hit_sword", note="검격 3")
add("sfx_sword_cut_hit", ("razor_sharp_steel_bl", 4), "hit_sword", note="찰진 절단 타격감 · 앞무음 0ms 컷")
add("sfx_stone_axe_hit_01", ("heavy_rough_stone_ax", 3), "hit_axe", note="돌도끼 평타 '퍽' 1")
add("sfx_stone_axe_hit_02", ("heavy_rough_stone_ax", 4), "hit_axe", note="돌도끼 평타 2")
add("sfx_stone_axe_hit_03", ("heavy_rough_stone_ax", 2), "hit_axe", note="돌도끼 평타 3")
add("sfx_stone_axe_heavy_01", ("massive_prehistoric_", 2), "hit_axe", note="돌도끼 강공격 '콰직' 1")
add("sfx_stone_axe_heavy_02", ("massive_prehistoric_", 4), "hit_axe", note="돌도끼 강공격 2")
add("sfx_obsidian_jab_01", ("fast_tight_wooden_sp", 1), "swing", note="슴베찌르개 직선 스윙 1")
add("sfx_obsidian_jab_02", ("fast_tight_wooden_sp", 4), "swing", note="슴베찌르개 직선 스윙 2")
add("sfx_obsidian_hit", ("razor_sharp_steel_bl", 4), "hit", mode="obsidian_hit", note="[파생] 검격 #4 피치 +10% + 돌도끼 #3 앞 80ms 어택 30% 레이어", layer=("heavy_rough_stone_ax", 3))
# B. 주인공 목소리
add("sfx_hero_effort_light_01", ("short_tight_masculin", 1), "voice", note="짧은 힘주기 1")
add("sfx_hero_effort_light_02", ("short_tight_masculin", 2), "voice", note="짧은 힘주기 2")
add("sfx_hero_effort_light_03", ("short_tight_masculin", 3), "voice", note="짧은 힘주기 3")
# [청음 반영 1차] 1시대의 긴 '으허!'가 필살기처럼 자주 들린다(오너) → 강한 기합은 0.9초 · 원시 포효는 1.4초까지만(빈도는 엔진에서 크게 낮춤)
add("sfx_hero_effort_heavy_01", ("brief_heavy_masculin", 4), "voice", mode="natural", max_len=0.9, fade=0.15, note="강공격 힘주기 1(0.9초까지)")
add("sfx_hero_effort_heavy_02", ("brief_heavy_masculin", 2), "voice", mode="natural", max_len=0.9, fade=0.15, note="강공격 힘주기 2(0.9초까지)")
add("sfx_hero_barbarian_roar_01", ("fierce_muscular_prim", 1), "voice", mode="natural", max_len=1.4, fade=0.2, note="원시 포효 1(1.4초까지)")
add("sfx_hero_barbarian_roar_02", ("fierce_muscular_prim", 4), "voice", mode="natural", max_len=1.4, fade=0.2, note="원시 포효 2(1.4초까지)")
add("sfx_hero_hit_light_01", ("short_sharp_masculin", 4), "hero_hit", note="일반 피격 1")
add("sfx_hero_hit_light_02", ("short_sharp_masculin", 2), "hero_hit", note="일반 피격 2")
add("sfx_hero_hit_light_03", ("short_sharp_masculin", 1), "hero_hit", note="일반 피격 3")
add("sfx_hero_hit_heavy_01", ("heavy_breathless_mas", 3), "hero_hit", note="보스 강타 피격 1")
add("sfx_hero_hit_heavy_02", ("heavy_breathless_mas", 2), "hero_hit", note="보스 강타 피격 2")
add("sfx_hero_death_01", ("heroic_masculine_war", 4), "hero_hit", note="주인공 사망 1(비명 → 쓰러짐)")
add("sfx_hero_death_02", ("heroic_masculine_war", 1), "hero_hit", note="주인공 사망 2")
# C. 1시대 야수
add("sfx_wolf_attack_01", ("ferocious_wild_wolf_", 2), "beast", mode="dense", L=2.5, note="늑대 공격 핵심 2.5초")
add("sfx_wolf_attack_02", ("ferocious_wild_wolf_", 4), "beast", mode="dense", L=2.5, note="늑대 공격 2")
add("sfx_rhino_charge_01", ("massive_furious_preh", 3), "beast_rhino", mode="dense", L=3.5, note="코뿔소 돌진 핵심 3.5초")
add("sfx_rhino_charge_02", ("massive_furious_preh", 1), "beast_rhino", mode="dense", L=3.5, note="코뿔소 돌진 2")
add("sfx_bear_roar_01", ("enormous_angry_grizz", 1), "beast_big", mode="natural", max_len=3.5, note="동굴 곰 포효 1")
add("sfx_bear_roar_02", ("enormous_angry_grizz", 2), "beast_big", mode="natural", max_len=3.5, note="동굴 곰 포효 2(앞 1.5초 낮은 으르렁은 잘라냄)")
add("sfx_tiger_roar_01", ("massive_Siberian_tig", 4), "beast_big", mode="natural", max_len=4.3, note="산군 포효 1(두 번 울음)")
add("sfx_tiger_roar_02", ("massive_Siberian_tig", 3), "beast_big", mode="natural", max_len=4.0, note="산군 포효 2")
add("sfx_beast_death", ("massive_wild_apex_pr", 3), "beast_big", mode="natural", max_len=3.5, note="곰 · 호랑이 · 코뿔소 공용 사망음(게임에서 음높이 분기)")
add("sfx_beast_boss_death", ("enormous_prehistoric", 1), "beast_big", mode="natural", max_len=4.0, note="야수 보스 최후 붕괴")
# D. 원거리
add("sfx_bow_full_01", ("heavy_wooden_warbow_", 3), "bow", mode="bow_tight", note="활 당겨 쏘기 원테이크(당김과 발사 사이의 긴 무음은 0.25초로 줄임)")
add("sfx_bow_full_02", ("heavy_wooden_warbow_", 1), "bow", mode="bow_tight", note="활 당겨 쏘기 2")
add("sfx_bow_shoot_01", ("heavy_wooden_hunting", 4), "bow", mode="natural", max_len=1.6, note="즉발 단발 사격 1")
add("sfx_bow_shoot_02", ("heavy_wooden_hunting", 1), "bow", mode="natural", max_len=1.6, note="즉발 단발 사격 2(앞무음 854ms 컷)")
add("sfx_bow_draw", ("heavy_wooden_warbow_", 3), "bow", mode="crop", a=0.0, b=1.0, fade=0.12, note="[파생] 원테이크 #3 앞 당김 1초")
add("sfx_arrow_volley", ("massive_volley_of_do", 4), "volley", mode="natural", max_len=3.3, start_db=30, note="일제 사격 화살비(앞무음 802ms 컷 · 날아가는 바람 → 꽂힘)")
add("sfx_rifle_shot_01", ("vintage_early_1900s_", 4), "gun", mode="natural", max_len=1.6, note="볼트액션 소총 1")
add("sfx_rifle_shot_02", ("vintage_early_1900s_", 1), "gun", mode="natural", max_len=1.6, note="볼트액션 소총 2")
add("sfx_pistol_shot", ("vintage_early_1900s_", 2), "gun", mode="pistol", note="[파생] 소총 #2 피치 +18% · 0.55초")
# E. 적 피격 · 적장 사망
add("sfx_enemy_katana_hurt_01", ("razor_sharp_katana_b", 2), "voice", eq="katana", note="칼 베임 1(실측: 날 소리가 주 · 중역 7% — 청음 반영: 4kHz 위 -8dB)")
add("sfx_enemy_katana_hurt_02", ("razor_sharp_katana_b", 1), "voice", eq="katana", note="칼 베임 2")
add("sfx_enemy_bullet_hurt_01", ("heavy_dull_bullet_im", 4), "voice", mode="natural", max_len=1.0, note="총탄 피격 1")
add("sfx_enemy_bullet_hurt_02", ("heavy_dull_bullet_im", 3), "voice", mode="natural", max_len=1.0, note="총탄 피격 2")
add("sfx_boss_general_death_01", ("deep_masculine_warri", 3), "death", mode="natural", max_len=3.5, note="적장 최후 1")
add("sfx_boss_general_death_02", ("deep_masculine_warri", 1), "death", mode="natural", max_len=3.6, note="적장 최후 2")
add("sfx_soldier_down", ("deep_masculine_warri", 3), "death", mode="soldier_down", alt=("deep_masculine_warri", 1), note="[파생] 후반부 갑옷 낙하 0.35초(비명 제외) — #3에 낙하 사건이 없으면 #1에서")
# F. 기병 · 함성
add("sfx_cavalry_hooves_loop", ("massive_horde_of_hun", 4), "loop_low", mode="loop", L=4.0, xf=0.45, note="말발굽 심리스 루프 4.0초")
add("sfx_cavalry_charge", ("fierce_armored_caval", 3), "cav", mode="dense", L=3.5, note="정면 돌격 쇄도 3.5초")
add("sfx_cavalry_horn", ("ominous_deep_ancient", 3), "horn", mode="natural", max_len=4.0, start_db=12, end_db=60, note="침공 경보 뿔피리 4.0초(뿔피리 시작점 기준)")
add("sfx_army_warcry_01", ("hundreds_of_ancient_", 4), "crowd", mode="dense", L=4.0, note="정규군 함성 1")
add("sfx_army_warcry_02", ("hundreds_of_ancient_", 2), "crowd", mode="dense", L=4.0, note="정규군 함성 2")
add("sfx_nomad_horde_cry_01", ("terrifying_horde_of_", 2), "crowd", mode="dense", L=4.5, note="북방 기병 돌격 괴성 1")
add("sfx_nomad_horde_cry_02", ("terrifying_horde_of_", 1), "crowd", mode="dense", L=4.5, note="북방 기병 돌격 괴성 2")
add("sfx_nomad_chant_loop", ("menacing_army_of_anc", 3), "loop", mode="loop", L=4.5, xf=0.45, note="포위 대치 후두 구호 루프(리듬 주기에 맞춰 길이 조정)")
add("sfx_nomad_ambush_cry_01", ("sudden_chilling_noma", 1), "cry", mode="natural", max_len=2.6, note="기습 단발 괴성 1")
add("sfx_nomad_ambush_cry_02", ("sudden_chilling_noma", 2), "cry", mode="natural", max_len=2.6, note="기습 단발 괴성 2")
# G. 부처님 강림 · 광명
add("sfx_buddha_emille_bell", ("giant_ancient_Korean", 2), "bell", mode="natural", max_len=5.0, end_db=40, fade=0.5, note="에밀레종(#2 · #4 가운데 저역이 더 깊은 #2 — 150Hz 아래 15% ↔ 0%)")
add("sfx_buddha_light_aura", ("warm_radiant_golden_", 1), "aura", mode="crop", a=0.0, b=4.0, fade=0.4, note="광명 지속 오라 4초")

assert len(K) == 64, len(K)
assert len({k["key"] for k in K}) == 64


# ───────── 입력 ─────────
def gather(src):
    """WAV 폴더 또는 zip → {(prefix, take): path}. zip은 빈 임시 폴더에 풀고 경로 탈출을 막는다(첨부는 신뢰하지 않는 데이터)."""
    if src.lower().endswith(".zip"):
        tmp = tempfile.mkdtemp(prefix="r37wav_")
        with zipfile.ZipFile(src) as z:
            for i in z.infolist():
                if i.is_dir() or not i.filename.lower().endswith(".wav"):
                    continue
                name = os.path.basename(i.filename)
                if not name or ".." in name:
                    continue
                with z.open(i) as f, open(os.path.join(tmp, name), "wb") as o:
                    shutil.copyfileobj(f, o)
        src = tmp
    out = {}
    for fn in os.listdir(src):
        m = re.match(r"^(.+?)_#(\d+)-\d+\.wav$", fn)
        if m:
            out[(m.group(1), int(m.group(2)))] = os.path.join(src, fn)
    return out


def read_wav(path):
    sr, d = wavfile.read(path)
    if d.dtype != np.int16:
        raise SystemExit(f"16bit WAV만 지원: {path} {d.dtype}")
    x = d.astype(np.float64) / 32768.0
    if x.ndim == 1:
        x = np.stack([x, x], axis=1)
    return sr, x


# ───────── DSP ─────────
def db(v):
    return 20 * math.log10(max(v, 1e-9))


def rbj_peaking(f0, sr, gain_db, Q):
    A = 10 ** (gain_db / 40)
    w0 = 2 * math.pi * f0 / sr
    al = math.sin(w0) / (2 * Q)
    b = [1 + al * A, -2 * math.cos(w0), 1 - al * A]
    a = [1 + al / A, -2 * math.cos(w0), 1 - al / A]
    return np.array([[b[0] / a[0], b[1] / a[0], b[2] / a[0], 1, a[1] / a[0], a[2] / a[0]]])


def rbj_highshelf(f0, sr, gain_db, S=1.0):
    A = 10 ** (gain_db / 40)
    w0 = 2 * math.pi * f0 / sr
    c = math.cos(w0)
    al = math.sin(w0) / 2 * math.sqrt((A + 1 / A) * (1 / S - 1) + 2)
    sa = 2 * math.sqrt(A) * al
    b0 = A * ((A + 1) + (A - 1) * c + sa)
    b1 = -2 * A * ((A - 1) + (A + 1) * c)
    b2 = A * ((A + 1) + (A - 1) * c - sa)
    a0 = (A + 1) - (A - 1) * c + sa
    a1 = 2 * ((A - 1) - (A + 1) * c)
    a2 = (A + 1) - (A - 1) * c - sa
    return np.array([[b0 / a0, b1 / a0, b2 / a0, 1, a1 / a0, a2 / a0]])


def eq_chain(x, sr, kind):
    sos = [signal.butter(2, 26, btype="highpass", fs=sr, output="sos")]
    if kind == "sword":
        # [청음 반영 1차] 발주서의 4~7kHz +2.5dB('리니지 타격감')는 '깡깡' 금속성 피크로 들려(오너) 뺐다.
        #  대신 5kHz 위를 -5dB 셸프 · 7.5kHz 둘레 -4dB(강철 울림 자리). 220Hz 하이패스(저음 충돌 방지)는 그대로
        sos.append(signal.butter(2, 220, btype="highpass", fs=sr, output="sos"))
        sos.append(rbj_highshelf(5000, sr, -5.0))
        sos.append(rbj_peaking(7500, sr, -4.0, 1.0))
    elif kind == "katana":
        # [청음 반영 1차] 적 베임(날 소리가 주): 4kHz 위를 -8dB — 칼 밑에 작게 얹는 질감만 남긴다
        sos.append(signal.butter(2, 150, btype="highpass", fs=sr, output="sos"))
        sos.append(rbj_highshelf(4000, sr, -8.0))
    elif kind == "axe":
        sos.append(rbj_peaking(2300, sr, 2.0, 1.0))
    elif kind == "low":
        sos.append(rbj_peaking(78, sr, 2.0, 1.3))
        sos.append(rbj_highshelf(3000, sr, -1.5))
    for s in sos:
        x = signal.sosfilt(s, x, axis=0)
    return x


def env_db(x, sr, win=0.1, hop=0.01):
    """창 RMS(dB) 곡선. 모노 합으로 잰다."""
    m = x.mean(axis=1)
    w, h = max(1, int(sr * win)), max(1, int(sr * hop))
    if len(m) <= w:
        return np.array([db(math.sqrt(float(np.mean(m ** 2))))]), np.array([0.0])
    cs = np.concatenate([[0.0], np.cumsum(m ** 2)])
    st = np.arange(0, len(m) - w, h)
    e = np.sqrt((cs[st + w] - cs[st]) / w)
    return 20 * np.log10(np.maximum(e, 1e-9)), st / sr


def lead_index(x, sr):
    a = np.max(np.abs(x), axis=1)
    thr = max(a.max() * 10 ** (LEAD_REL_DB / 20), LEAD_ABS)
    above = np.nonzero(a > thr)[0]
    i = int(above[0]) if len(above) else 0
    return max(0, i - int(sr * LEAD_PRE_MS / 1000))


def tail_index(x, sr):
    a = np.max(np.abs(x), axis=1)
    above = np.nonzero(a > 10 ** (TAIL_DB / 20))[0]
    i = int(above[-1]) if len(above) else len(a) - 1
    return min(len(a), i + int(sr * TAIL_KEEP_MS / 1000))


def trim(x, sr):
    i0, i1 = lead_index(x, sr), tail_index(x, sr)
    return x[i0:i1], i0, len(x) - i1


def fade(x, sr, fin_ms=FADE_IN_MS, fout_ms=FADE_OUT_MS):
    x = x.copy()
    n = len(x)
    fi = min(n // 2, int(sr * fin_ms / 1000))
    fo = min(n // 2, int(sr * fout_ms / 1000))
    if fi > 0:
        x[:fi] *= np.linspace(0, 1, fi)[:, None]
    if fo > 0:
        x[n - fo:] *= np.linspace(1, 0, fo)[:, None]
    return x


def natural(x, sr, max_len, start_db=14, end_db=24, pre=0.12, post=0.3):
    """긴 소리: 가장 센 0.1초 창보다 start_db 아래를 처음 넘는 곳(pre 앞)에서, end_db 아래로 꺼진 뒤 post에서 끝(max_len 상한)."""
    e, t = env_db(x, sr)
    top = e.max()
    on = np.nonzero(e > top - start_db)[0]
    i0 = max(0, int((t[on[0]] - pre) * sr)) if len(on) else 0
    i0 = max(i0, lead_index(x, sr)) if t[on[0]] - pre > lead_index(x, sr) / sr else lead_index(x, sr)
    off = np.nonzero(e > top - end_db)[0]
    i1 = min(len(x), int((t[off[-1]] + 0.1 + post) * sr)) if len(off) else len(x)
    i1 = min(i1, tail_index(x, sr))
    cut = False
    if (i1 - i0) / sr > max_len:
        i1 = i0 + int(max_len * sr)
        cut = True
    return x[i0:i1], i0, len(x) - i1, cut


def dense(x, sr, L):
    """에너지가 가장 큰 L초 창(0.05초 걸음)."""
    m = x.mean(axis=1)
    n = int(L * sr)
    if len(m) <= n:
        return x, 0, 0
    cs = np.concatenate([[0.0], np.cumsum(m ** 2)])
    hop = int(sr * 0.05)
    st = np.arange(0, len(m) - n, hop)
    e = cs[st + n] - cs[st]
    i0 = int(st[int(e.argmax())])
    i0 = max(lead_index(x, sr), i0) if i0 < lead_index(x, sr) else i0
    i1 = min(len(x), i0 + n)
    return x[i0:i1], i0, len(x) - i1


def _acf_peak(x, sr, win, hop, lo, hi, height):
    """엔벨로프(창 win · 걸음 hop) 자기상관의 첫 뚜렷한 봉우리 → (주기 초, 세기)."""
    e, _ = env_db(x, sr, win=win, hop=hop)
    e = e - e.mean()
    if len(e) < 40:
        return None, 0.0
    ac = np.correlate(e, e, mode="full")[len(e) - 1:]
    ac = ac / max(ac[0], 1e-9)
    i_lo, i_hi = int(lo / hop), min(len(ac) - 1, int(hi / hop))
    if i_hi <= i_lo + 2:
        return None, 0.0
    seg = ac[i_lo:i_hi]
    peaks, _ = signal.find_peaks(seg, height=height, distance=max(1, int(0.15 / hop)))
    if len(peaks) == 0:
        return None, float(seg.max())
    p = peaks[0]
    return (i_lo + p) * hop, float(seg[p])


def rhythm_period(x, sr):
    """리듬 주기(초). 말발굽처럼 빠른 주기(0.25~1.5초)는 0.1초 창으로, 구호처럼 느린 주기(1.5~6초)는 0.5초 창으로 잰다
    (느린 주기는 가는 창에서는 개별 외침의 요동에 묻혀 보이지 않는다 — 1차 굽기에서 확인). 뚜렷하지 않으면 None."""
    fast = _acf_peak(x, sr, 0.1, 0.02, 0.25, 1.5, 0.45)
    slow = _acf_peak(x, sr, 0.5, 0.05, 1.5, 6.0, 0.25)
    cands = [c for c in (fast, slow) if c[0]]
    if not cands:
        return None, max(fast[1], slow[1])
    return max(cands, key=lambda c: c[1])


def make_loop(x, sr, L, xf, pad=0.1):
    """심리스 루프: 리듬 주기가 있으면 L을 그 배수로(±15% 안에서) · 가장 밀도 높은 L+xf 구간 → 등출력 크로스페이드 → 앞뒤 pad만큼 주기 연장."""
    per, strength = rhythm_period(x, sr)
    L_used = L
    if per:
        n = max(1, round(L / per))
        cand = n * per
        if abs(cand - L) / L <= 0.15:
            L_used = cand
    seg, i0, _ = dense(x, sr, L_used + xf)
    nL, nx = int(L_used * sr), int(xf * sr)
    if len(seg) < nL + nx:
        nx = max(0, len(seg) - nL)
    A = seg[:nL].copy()
    B = seg[nL:nL + nx]
    if nx > 0:
        th = np.linspace(0, math.pi / 2, nx)[:, None]
        A[:nx] = A[:nx] * np.sin(th) + B * np.cos(th)
    npad = int(pad * sr)
    F = np.concatenate([A[nL - npad:], A, A[:npad]])
    return F, pad, pad + nL / sr, L_used, per, strength, i0


def resample(x, sr_in, sr_out, speed=1.0):
    """폴리페이즈 리샘플. speed > 1 = 그만큼 빠르게(음높이 ↑ · 길이 ↓)."""
    fr = Fraction(sr_out, sr_in) / Fraction(speed).limit_denominator(1000)
    return signal.resample_poly(x, fr.numerator, fr.denominator, axis=0)


def body_rms_db(x, sr, win=0.4):
    m = x.mean(axis=1)
    w = int(sr * win)
    if len(m) <= w:
        return db(math.sqrt(float(np.mean(m ** 2))))
    cs = np.concatenate([[0.0], np.cumsum(m ** 2)])
    st = np.arange(0, len(m) - w, max(1, int(sr * 0.01)))
    return db(math.sqrt(float(np.max((cs[st + w] - cs[st]) / w))))


def limiter(x, sr, ceil_db=CEIL_DB, look_ms=3.0, rel_ms=60.0):
    """룩어헤드 피크 리미터. 돌려주는 값: (신호, 최대 게인 감소 dB)."""
    ceil = 10 ** (ceil_db / 20)
    a = np.max(np.abs(x), axis=1)
    need = np.minimum(1.0, ceil / np.maximum(a, 1e-9))
    W = max(1, int(sr * look_ms / 1000))
    g = minimum_filter1d(need, size=2 * W + 1, mode="nearest")
    g = uniform_filter1d(g, size=W + 1, mode="nearest")
    g = np.minimum(g, need)
    r = math.exp(-1 / (rel_ms / 1000 * sr))
    d_req = 1 - g
    d = np.empty_like(d_req)
    carry = 0.0
    CH = 16384
    for s in range(0, len(d_req), CH):
        seg = d_req[s:s + CH]
        k = np.arange(len(seg))
        m = np.maximum.accumulate(seg * r ** (-k))
        ds = np.maximum(m * r ** k, carry * r ** (k + 1))
        d[s:s + len(seg)] = ds
        carry = float(ds[-1])
    gain = 1 - d
    return x * gain[:, None], db(float(gain.min())) if gain.min() < 1 else 0.0


def normalize(x, sr, target_db, gr_cap_db, win=0.4):
    """목표 RMS(창 win초)로 올린 뒤 리미터. 리미터가 cap보다 많이 깎아야 하면 게인을 그만큼 낮춘다(목표 미달량은 로그에)."""
    cur = body_rms_db(x, sr, win)
    gain_db = target_db - cur
    y, gr = limiter(x * 10 ** (gain_db / 20), sr)
    if -gr > gr_cap_db:
        gain_db -= (-gr - gr_cap_db)
        y, gr = limiter(x * 10 ** (gain_db / 20), sr)
    return y, gain_db, gr, body_rms_db(y, sr, win), db(float(np.max(np.abs(y))))


def to_mono(x):
    return x.mean(axis=1, keepdims=True)


def soften(x, k):
    """봉우리 둥글리기(tanh 소프트 새추레이션): 몸통은 거의 그대로, 가장 센 봉우리만 눌러 '단단한 피크'를 줄인다. k 1.4 = 절반 크기 신호가 0.68로"""
    return np.tanh(k * x) / math.tanh(k)


# ───────── 파생 가공 ─────────
def obsidian_hit(xa, xb, sr):
    a = resample(trim(xa, sr)[0], sr, sr, speed=1.10)
    b = trim(xb, sr)[0][: int(sr * 0.08)].copy()
    b = fade(b, sr, 0, 10) * 0.3
    out = a.copy()
    n = min(len(out), len(b))
    out[:n] += b[:n]
    return out


def bow_tight(x, sr, gap_keep=0.25):
    """원테이크(당김 … 무음 … 발사)의 가운데 무음을 gap_keep초로 줄인다. 무음이 없으면 그대로."""
    x, _, _ = trim(x, sr)
    e, t = env_db(x, sr, win=0.05, hop=0.01)
    top = e.max()
    quiet = e < top - 30
    # 0.3초 뒤부터 0.5초 넘게 이어지는 조용한 구간
    i = int(0.3 / 0.01)
    gap = None
    while i < len(quiet):
        if quiet[i]:
            j = i
            while j < len(quiet) and quiet[j]:
                j += 1
            if (j - i) * 0.01 >= 0.5 and j < len(quiet):
                gap = (t[i], t[j])
                break
            i = j
        else:
            i += 1
    if not gap:
        return x, None
    g0, g1 = gap
    a = x[: int((g0 + gap_keep) * sr)]
    b = x[int((g1 - 0.06) * sr):]
    xf = int(0.04 * sr)
    out = np.concatenate([a[:-xf], a[-xf:] * np.linspace(1, 0, xf)[:, None] + b[:xf] * np.linspace(0, 1, xf)[:, None], b[xf:]])
    return out, (round(g0, 2), round(g1, 2))


def soldier_down(x, sr, after=1.2, L=0.35, within_db=8.0, dip_db=10.0):
    """비명이 지난 뒤(after초 뒤)에 '다시 커지는' 사건(갑옷 낙하)을 찾아 L초를 잘라 낸다.
    사건 = after초 뒤 30ms 창의 최대 봉우리로, ① 파일에서 가장 센 창보다 within_db 안이고 ② 그 앞 0.6초 안에 dip_db 넘는 골짜기가 있어야 한다
    (①은 꼬리 잡음을, ②는 비명이 그냥 줄어드는 꼬리를 사건으로 잡지 않게 — 1 · 2차 굽기에서 둘 다 겪었다). 없으면 (None, 이유)."""
    e, t = env_db(x, sr, win=0.03, hop=0.01)
    top = float(e.max())
    i_after = int(after / 0.01)
    if i_after >= len(e):
        return None, "너무 짧음"
    bi = i_after + int(np.argmax(e[i_after:]))
    peak = float(e[bi])
    if peak < top - within_db:
        return None, f"{after}s 뒤 봉우리 {peak:.0f}dB가 가장 센 창 {top:.0f}dB보다 {within_db:.0f}dB 넘게 낮음"
    pre = e[max(i_after, bi - 60): bi]
    dip = float(pre.min()) if len(pre) else peak
    if peak - dip < dip_db:
        return None, f"봉우리({t[bi]:.2f}s · {peak:.0f}dB) 앞에 골짜기가 없음(최저 {dip:.0f}dB)"
    # 시작: 골짜기에서 봉우리로 올라오는 자리(봉우리보다 12dB 아래를 마지막으로 지나는 곳) · 늦어도 봉우리 0.15초 앞
    j = bi
    while j > i_after and e[j] > peak - 12:
        j -= 1
    j = max(j, bi - 15)
    i0 = max(0, int((t[j] - 0.01) * sr))
    seg = x[i0: i0 + int(L * sr)]
    return fade(seg, sr, 8, 60), (round(float(t[j]), 2), round(peak, 1), round(dip, 1), round(top, 1))


# ───────── MP3 ─────────
def encode_mp3(x, sr, kbps, path):
    pcm = (np.clip(x, -1, 1) * 32767).round().astype("<i2").tobytes()
    ch = x.shape[1]
    try:
        import lameenc
        enc = lameenc.Encoder()
        enc.set_bit_rate(kbps)
        enc.set_in_sample_rate(sr)
        enc.set_channels(ch)
        enc.set_quality(2)
        data = enc.encode(pcm) + enc.flush()
        open(path, "wb").write(data)
        return "lameenc", (b"Info" in data[:4096] or b"Xing" in data[:4096])
    except ImportError:
        tmp = path + ".wav"
        wavfile.write(tmp, sr, (np.clip(x, -1, 1) * 32767).round().astype(np.int16))
        r = subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", tmp, "-codec:a", "libmp3lame", "-b:a", f"{kbps}k", "-ac", str(ch), "-ar", str(sr), path], capture_output=True, text=True)
        os.unlink(tmp)
        if r.returncode != 0:
            raise SystemExit("MP3 인코더 없음: pip install lameenc 또는 ffmpeg(libmp3lame) 필요\n" + r.stderr)
        return "ffmpeg", True


# ───────── 본 공정 ─────────
def process(spec, SRC):
    pre, take = spec["src"]
    sr, x0 = read_wav(SRC[(pre, take)])
    cat = CATS[spec["cat"]]
    p = spec["p"]
    x = eq_chain(x0, sr, p.get("eq", cat["eq"]))
    info = dict(key=spec["key"], src=f"{pre} #{take}", cat=spec["cat"], mode=spec["mode"], note=spec["note"], before_s=round(len(x0) / sr, 3))
    loop = None
    fout = FADE_OUT_MS
    mode = spec["mode"]
    if mode == "trim":
        y, i0, i1 = trim(x, sr)
        info.update(lead_cut_ms=round(i0 / sr * 1000, 1), tail_cut_ms=round(i1 / sr * 1000, 1))
    elif mode == "natural":
        y, i0, i1, cut = natural(x, sr, p["max_len"], start_db=p.get("start_db", 14), end_db=p.get("end_db", 24))
        info.update(lead_cut_ms=round(i0 / sr * 1000, 1), tail_cut_ms=round(i1 / sr * 1000, 1), cut_at_max=cut)
        fout = int(p.get("fade", 0.2 if cut else 0.15) * 1000)
    elif mode == "dense":
        y, i0, i1 = dense(x, sr, p["L"])
        info.update(start_s=round(i0 / sr, 2), end_s=round((len(x) - i1) / sr, 2), lead_cut_ms=round(i0 / sr * 1000, 1), tail_cut_ms=round(i1 / sr * 1000, 1))
        fout = 180
        y = fade(y, sr, 40, 0)
    elif mode == "loop":
        F, ls, le, Lu, per, strength, i0 = make_loop(x, sr, p["L"], p["xf"])
        y = F
        loop = (round(ls, 4), round(le, 4))
        info.update(loop_len_s=round(Lu, 3), loop_spec_s=p["L"], rhythm_period_s=round(per, 3) if per else None, rhythm_strength=round(strength, 2), start_s=round(i0 / sr, 2), lead_cut_ms=round(i0 / sr * 1000, 1), tail_cut_ms=round((len(x) - i0) / sr * 1000 - Lu * 1000, 1))
        fout = 0
    elif mode == "crop":
        y, i0, i1 = trim(x, sr)
        a, b = int(p["a"] * sr), min(len(y), int(p["b"] * sr))
        y = y[a:b]
        info.update(lead_cut_ms=round(i0 / sr * 1000, 1), tail_cut_ms=round((len(x) - i0 - b) / sr * 1000, 1))
        fout = int(p.get("fade", 0.12) * 1000)
    elif mode == "obsidian_hit":
        _, xb = read_wav(SRC[p["layer"]])
        xb = eq_chain(xb, sr, "axe")
        y = obsidian_hit(x, xb, sr)
        y, i0, i1 = trim(y, sr)
        info.update(lead_cut_ms=round(lead_index(x, sr) / sr * 1000, 1), tail_cut_ms=round(i1 / sr * 1000, 1), layer="heavy_rough_stone_ax #3 앞 80ms × 0.3", pitch=1.10)
    elif mode == "bow_tight":
        y, gap = bow_tight(x, sr)
        info.update(lead_cut_ms=round(lead_index(x, sr) / sr * 1000, 1), tail_cut_ms=round((len(x) - tail_index(x, sr)) / sr * 1000, 1), gap_removed_s=gap)
    elif mode == "pistol":
        y, i0, i1 = trim(x, sr)
        y = resample(y, sr, sr, speed=1.18)
        y = y[: int(0.55 * sr)]
        info.update(lead_cut_ms=round(i0 / sr * 1000, 1), tail_cut_ms=round(i1 / sr * 1000, 1), pitch=1.18)
        fout = 60
    elif mode == "soldier_down":
        y, found = soldier_down(x, sr)
        used = f"{pre} #{take}"
        why = None
        if y is None:
            why = f"{used}: {found}"
            apre, atake = p["alt"]
            _, xa = read_wav(SRC[(apre, atake)])
            xa = eq_chain(xa, sr, cat["eq"])
            y, found = soldier_down(xa, sr)
            used = f"{apre} #{atake}"
            if y is None:
                raise SystemExit("soldier_down: 갑옷 낙하 구간을 찾지 못함 — " + why + " / " + found)
        info.update(src_used=used, onset=found, fallback_reason=why, lead_cut_ms=None, tail_cut_ms=None)
        fout = 60
    else:
        raise SystemExit("unknown mode " + mode)
    if fout:
        y = fade(y, sr, FADE_IN_MS, fout)
    y = resample(y, sr, SR_OUT)
    if not cat["stereo"]:
        y = to_mono(y)
    if cat.get("soft"):
        y = soften(y / max(1e-9, float(np.max(np.abs(y)))), cat["soft"])
    y, gain_db, gr_db, rms, peak = normalize(y, SR_OUT, cat["rms"], cat["gr"], cat.get("win", 0.4))
    info.update(after_s=round(len(y) / SR_OUT, 3), gain_db=round(gain_db, 1), limit_db=round(gr_db, 1), rms_db=round(rms, 1), target_db=cat["rms"], peak_db=round(peak, 1), stereo=cat["stereo"], kbps=cat["kbps"], fade_out_ms=fout, loop=loop)
    return y, info


def main():
    if len(sys.argv) < 3:
        raise SystemExit(__doc__)
    SRC = gather(sys.argv[1])
    build = sys.argv[2]
    out_dir = os.path.join(build, "assets", "sfx")
    os.makedirs(out_dir, exist_ok=True)
    missing = [k["src"] for k in K if k["src"] not in SRC] + [k["p"]["layer"] for k in K if "layer" in k["p"] and k["p"]["layer"] not in SRC]
    if missing:
        raise SystemExit(f"원본에 없는 테이크: {missing}")
    # 이전 결과 정리(sfx_*.mp3 · sfx_manifest.json만)
    for fn in os.listdir(out_dir):
        if re.match(r"^sfx_.*\.mp3$", fn) or fn == "sfx_manifest.json":
            os.unlink(os.path.join(out_dir, fn))
    print(f"원본 {len(SRC)}개 가운데 {len({k['src'] for k in K} | {k['p']['layer'] for k in K if 'layer' in k['p']} | {k['p']['alt'] for k in K if 'alt' in k['p']})}개 테이크 선별 → 키 {len(K)}개")
    print(f"{'key':28s} {'src':26s} {'before':>6s} {'after':>6s} {'lead':>7s} {'tail':>7s} {'gain':>6s} {'lim':>5s} {'rms':>6s} {'peak':>5s} {'KB':>5s}")
    log, files, keys, total = [], {}, {}, 0
    enc_name, tag_ok = None, None
    for spec in K:
        y, info = process(spec, SRC)
        fn = spec["key"] + ".mp3"
        path = os.path.join(out_dir, fn)
        enc_name, ok = encode_mp3(y, SR_OUT, CATS[spec["cat"]]["kbps"], path)
        tag_ok = ok if tag_ok is None else (tag_ok and ok)
        size = os.path.getsize(path)
        total += size
        info["bytes"] = size
        info["file"] = fn
        log.append(info)
        lead = info.get("lead_cut_ms")
        tail = info.get("tail_cut_ms")
        print(f"{spec['key']:28s} {info.get('src_used', info['src']):26s} {info['before_s']:6.2f} {info['after_s']:6.2f} {'      -' if lead is None else f'{lead:7.0f}'} {'      -' if tail is None else f'{tail:7.0f}'} {info['gain_db']:+6.1f} {info['limit_db']:5.1f} {info['rms_db']:6.1f} {info['peak_db']:5.1f} {size / 1000:5.0f}")
        extra = {k: info[k] for k in ("loop_len_s", "rhythm_period_s", "rhythm_strength", "gap_removed_s", "onset", "fallback_reason", "cut_at_max", "pitch") if info.get(k) not in (None, False)}
        if extra:
            print(f"{'':28s} ↳ {extra}")
        files[fn] = {"bytes": size, "dur": info["after_s"], "src": info["src"], "rms": info["rms_db"], "peak": info["peak_db"], "stereo": info["stereo"], "kbps": info["kbps"]}
        base = re.sub(r"_\d\d$", "", spec["key"])
        e = keys.setdefault(base, {"files": [], "cat": spec["cat"], "stereo": info["stereo"]})
        e["files"].append(fn)
        if info["loop"]:
            e["loop"] = list(info["loop"])
    short = [i for i in log if i["rms_db"] < i["target_db"] - 1.0]
    print(f"\n인코더 {enc_name} · LAME/Xing 머리말 {'있음' if tag_ok else '없음(엔진이 디코딩 뒤 첫 소리 지점을 스스로 찾아 보정)'}")
    print(f"새 MP3 {len(log)}개 · {total / 1e6:.2f} MB")
    if short:
        print("목표 RMS에 1dB 넘게 못 미친 파일(리미터 허용량 때문에 게인을 줄임):")
        for i in short:
            print(f"  {i['key']:28s} 목표 {i['target_db']:.1f} → {i['rms_db']:.1f} dBFS")
    all_sfx = sum(os.path.getsize(os.path.join(out_dir, f)) for f in os.listdir(out_dir))
    print(f"assets/sfx 전체(기존 WAV 포함) {all_sfx / 1e6:.2f} MB  (상한 6.0MB → {'통과' if all_sfx <= 6.0e6 else '초과'})")
    man = {"r37": {"tool": "tools/r37/build_sfx.py", "source": "신시 효과음.zip — 48kHz 16bit stereo WAV 104개 · 33 prefixes", "count": len(log), "bytes": total,
                   "sample_rate": SR_OUT, "note": "키 → 파일(변주 _01~_03) · loop = [loopStart, loopEnd](초 · 파일 안쪽 지점). 게임 엔진(index.html의 createR37Sfx)이 읽는다."},
           "keys": keys, "files": files}
    json.dump(man, open(os.path.join(out_dir, "sfx_manifest.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    here = os.path.dirname(os.path.abspath(__file__))
    json.dump({"encoder": enc_name, "lame_tag": tag_ok, "total_bytes": total, "sfx_dir_bytes": all_sfx, "files": log}, open(os.path.join(here, "build_sfx_log.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("→", os.path.join(out_dir, "sfx_manifest.json"), "·", os.path.join(here, "build_sfx_log.json"))


if __name__ == "__main__":
    main()
