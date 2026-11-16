# 낯씨 목업 (Blender)

## 들어 있는 것

- `natssi_mockup.py` — 씬 생성 스크립트 (Blender 4.2 이상, 5.x에서 테스트)
- `screens/` — 폰·웹에 들어가는 화면 이미지 3장 (김서연 가상 데이터)
- `src/` — 화면 원본 HTML (문구를 바꾸려면 여기서 고친 뒤 `python3 shot.py`로 다시 캡처)
- `renders/` — 미리 렌더한 결과 (hero, phone, web, device, dock, dock_empty, ecosystem)

## 실행

**명령줄 (전부 렌더):** `natssi_mockup.py`와 `screens/`를 같은 폴더에 두고 실행

```
blender -b -P natssi_mockup.py
```

`renders/` 폴더에 PNG 4장이 생깁니다. 특정 컷만 뽑으려면 `NATSSI_SHOTS=hero,device`를, 샘플 수를 바꾸려면 `NATSSI_SAMPLES=128`을 앞에 붙이세요.

**Blender MCP / 스크립팅 탭:** 파일 위쪽의 `ASSET_DIR`를 이 폴더 경로로 바꾼 뒤 실행하세요. 이때는 씬만 만들고 렌더는 하지 않습니다. 카메라는 `Cam_hero`, `Cam_phone`, `Cam_web`, `Cam_device` 네 개예요.

주의: 스크립트가 처음에 현재 씬의 오브젝트를 모두 지웁니다. 새 파일에서 실행하세요.

## 디바이스

"낯씨 LED 케어 디바이스"는 확장 방향을 보여주기 위한 가상 제품입니다. 발표 자료에는 "확장 예시(콘셉트)"라고 표시해 주세요.

## 거치대 (v2)

- 221×104×12mm, 윗면에 디바이스 머리·손잡이 모양의 **깊이 2mm 곡면 안착 홈**(여유 0.6mm)
- 앞쪽 측면에 **길이 8mm × 두께 1mm 흰색 LED 인디케이터 바**(홈 안쪽에 매립)
- `dock`(클로즈업)·`dock_empty`(디바이스를 숨긴 빈 거치대) 컷 추가
- 검증: `python3 tools/verify_dock.py`
- 이어서 할 작업은 `CLAUDE.md` 참고

## 에코시스템 샷 (`ecosystem`)

- 노트북(웹 `desktop/04_change.png` 변화 그래프) + 폰(스캔 앱 화면 `mobile/05_capture.png`) + 데스크 스캐너(거치대 위 디바이스)를 한 화면에 담은 풀 샷
- 화면 이미지는 `python3 tools/make_eco_screens.py`로 `screens/screen_eco_web.png`, `screens/screen_eco_phone.png`를 만들어 이 컷에서만 바꿔 넣음(`SCREEN_SWAP`). 다른 화면을 쓰려면 이 스크립트의 파일 경로를 바꾸고 다시 실행
- 왼쪽 앞 대각선 위에서 내려다보는 카메라 `Cam_ecosystem`(44mm). 이 컷에서만 두 번째 폰(`Phone_today`)을 숨김
- 배경은 집 안 책상(`make_home()`): 원목 책상, 벽, 왼쪽 창으로 들어오는 아침 햇살, 화분·책·머그·액자 소품. 다른 컷은 기존 스튜디오 배경 그대로(`HOME_SHOTS`, `use_set()`로 컷별 전환)
- 렌더: `NATSSI_SHOTS=ecosystem python3 natssi_mockup.py` → `renders/natssi_ecosystem.png`
