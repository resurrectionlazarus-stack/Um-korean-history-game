신시(神市): 시공의 수호자들 — R23 배포 패키지 (액션 · 시인성 · 일반 몹 원화 로더 개편)
==========================================================
구성
  index.html            게임 전체 (React는 cdnjs에서 불러옴 · 인터넷 연결 필요)
  assets/MANIFEST.json  원화 목록 (1~6차 + 보행 패치 · 리터치 + R22 패치 + R23 1차 원화 누적 172종, 해상도 1920×1080 · 지평선 Y=670)
  assets/bg/            1~6시대 배경 원화 (far · mid · ground · arena_z4 — 1시대 mid는 webp) · 5시대 2막 설원 (era5_act2_far · mid · ground)
                        6시대 광복 여명 (era6_liberation_dawn.webp · 1945 경성 · 최종 보스 격파 후 광복 엔딩 하늘)
  assets/boss/          1시대 거대 산군 (idle · swipe · leap · hit) · 동굴 곰 지배자 (idle · swipe · charge · hit · walk1 · walk2 — R23 지터 수정본)
                        2시대 아사달 청동 거신병 (idle · smash · thunder · hit) · 위만 철기 선봉장 (idle · walk1 · walk2 · cone · lunge · hit)
                        3시대 계백 (idle · dash · stand · hit) · 연개소문 (idle · storm · slash · hit) · 소정방 (idle · charge · arrowfan · hit)
                        4시대 몽골 천호장 (idle · charge · volley · hit) · 침략군 철갑 공성 사령관 (idle · flame · smash · hit)
                        5시대 임진 왜장 (idle · walk1 · walk2 · cone · volley · hit) · 청 팔기군 대장 용골대 (idle · walk1 · walk2 · charge · arrowfan · hit)
                        6시대 병인양요 프랑스 원정군 지휘관 (idle · walk1 · walk2 · cone · volley · hit)
                              신미양요 미군 상륙 지휘관 (idle · walk1 · walk2 · cone · bombard · hit)
                              일본제국 깃발 기갑 대장군 (idle · walk1 · walk2 · charge · smash · laser360 · hit)
  assets/hero/          1시대 석장리 대사냥꾼 (idle · run ~ run8 · atk1 · atk2 · hit — R23 run3~run8 추가)
                        2시대 고조선 주인공 · 3시대 신라 대장군 김유신 · 4시대 고려 무신 척준경 (idle · run · run2 · atk1 · atk2 · hit)
                        5시대 조선 도원수 권율 · 6시대 한국광복군 특무대장(독립군 장교 원화) (idle · run ~ run8 · atk1 · atk2 · hit)
  assets/mob/           [R23 신규] 일반 몹 원화 (idle · walk · atk, 512×512 · groundY 470)
                        1시대 늑대(wolf) · 동굴 곰 일반 몹(bear_mob) · 2시대 고조선 청동 창병(pike) · 궁수(archer)
                        3시대 당나라 철갑 보병(tang_inf) · 당 기마 궁수(cav_archer)
  assets/fx/            4시대 황금 부처님 강림 (era4_buddha_descent.png · 철벽 결계 → 기원 통과 시 하늘에서 하강하는 컷신)

R23에서 바뀐 것
  · 공격 모션(전 시대 주인공 공통): 선딜 0~22% 뒤로 젖혀 기 모으기(rot −0.14 · dx −8 · sx 0.94 · sy 1.05) →
    타격 22~65% 전방 돌진 스윙(rot +0.16 · dx +24~30 · sx 1.12 · sy 0.91) → 잔심 65~100% 자연 복귀.
    무기 끝단 궤적에 맞춘 HD 다층 참격 아크(번짐 · 중간 · 백열 심 + 속도선 + 끝단 섬광), 창은 직선 찌르기 궤적.
    미술팀이 atk_prep · atk1_prep · atk1_2 ~ atk1_4(atk2도 같음)를 넣으면 MANIFEST만으로 3~4프레임 스윙으로 자동 확장.
  · 히트스톱: 강타(콤보 3 · 4타 · 스킬 · 보스 타격) 적중 시 공격자 · 피격자 약 62ms(60Hz 4프레임) 정지 + 공격 방향 4~6px 카메라 쉐이크,
    일반 타격 33ms(2프레임). 화면 주사율과 무관하게 실제 시간 기준. 1시대 도끼 헛스윙 정지(117~150ms) 제거.
  · 보행: 1시대 사냥꾼 8프레임 4틱 질주. 2프레임 구간(2~4시대)은 전방 대시 기울기 0.035rad · 스텝 사인 곡선 ·
    걸음마다 좌우 무게 이동 · 발 구름 잔상 · 앞/뒷발 교대 먼지로 '한발 깡총' 완화.
  · 동굴 곰 지터 수정: 새 walk1/walk2(머리 높이 차 44px → 1px) + walk 몸통 중심을 idle에 맞춰 굽기(좌우 3.5px 흔들림 → 0) + 이동 판정 히스테리시스.
  · 배경 Dim: far · mid · ground · Z4 arena · 5시대 2막 배경을 굽는 순간 14% 먹빛 딤(실행 비용 0) — 주인공 · 적이 배경 먹선에 묻히지 않게.
  · 일반 몹 원화 로더(MOB_SPEC): assets/mob/era{N}_{mobKey}_{idle|walk|atk}.png가 MANIFEST에 있으면 코드 도형 대신 원화로 그림.
    피격 = 백색 플래시 + 넉백 기울기, 이동 = walk ↔ idle 교차 + 보행 기울기. 원화가 없거나 실패하면 그 몹만 코드 스프라이트로 폴백.
  · 원화 몹이 여럿이어도 60fps 유지: 저해상도 층 합성을 몹 주변 사각형으로 한정(부분 합성).

올리는 법
  · Netlify Drop: https://app.netlify.com/drop 에 이 폴더(shinsi-R23)를 통째로 끌어다 놓기
  · GitHub Pages: 이 폴더 내용을 저장소 루트(또는 docs/)에 올리고 Settings → Pages 에서 브랜치 지정
  · 내 컴퓨터: 폴더 안에서 `python3 -m http.server` 를 켠 뒤 http://localhost:8000 접속
    (index.html을 더블클릭해 file://로 열어도 동작하지만, 브라우저가 MANIFEST.json 읽기를 막으면 내장 목록으로 같은 원화를 불러옵니다)

1~6시대 모두 원화로 그립니다. 원화가 없거나 불러오기에 실패한 항목(배경 · 캐릭터 · 일반 몹 각각)은 자동으로 기존 코드 렌더링으로 그려집니다.
다음 시대 원화는 앞 시대 보스를 쓰러뜨리는 동안 미리 내려받습니다.
보행: 주인공은 이동 중 idle 없이 질주 원화를 차례로 재생합니다 — 2~4시대 run ↔ run2 9틱 교차 · 1 · 5 · 6시대 run → run2 → … → run8 4틱씩. 멈추면 idle.
      보스 · 중간보스는 walk1 / walk2 원화가 있으면 걸을 때 번갈아 그립니다. 없으면 몸을 앞뒤로 기울이며 걷습니다.
Z4 보스 아레나: 아레나 원화는 지평선(화면 335px) 위만, 아래 바닥은 ground 원화 100% 한 장 — 경계는 8px 소프트 다크 페더(이중 겹침 0%).
6시대 최종 보스: 1페이즈 기갑 돌격 · 강철 해머 → 2페이즈 서치라이트 기총 · 포격 → 3페이즈 전방위 광선. 격파하면 하늘이 광복 여명 원화로 바뀝니다.
URL 옵션: ?assets=0 (원화 끄기) · ?hold=0 (보류 원화도 사용) · ?layout=wide|classic (가로/세로 레이아웃 강제) · ?fx=hd|lite
          ?dim=0 (배경 딤 끄기 — 전후 비교용) · ?dim=0.12 (딤 세기 0~0.3)
