# 낯씨 Blender 목업 — Claude Code 작업 메모

낯씨(natssi) 웹앱의 발표용 목업. 노트북(웹 대시보드) + 폰 2대(앱 화면) + "낯씨 LED 케어 디바이스"(가상 제품, 확장 방향 예시) + 충전 거치대. 디바이스는 반드시 **"확장 예시(콘셉트)"**로 표기해서 쓴다.

## 환경·실행
- Python 3.11+ 에서 `pip install bpy` (Blender 5.3 모듈). Blender 앱이 있으면 `blender -b -P natssi_mockup.py`도 된다.
- 전부 렌더: `python3 natssi_mockup.py` → `renders/natssi_<컷>.png`
- 일부만 / 빠르게: `NATSSI_SHOTS=dock,device NATSSI_SAMPLES=48 NATSSI_SCALE=60 python3 natssi_mockup.py`
- 컷 이름: hero(전체), phone, web, device, dock(거치대 클로즈업), dock_empty(디바이스를 숨긴 빈 거치대), ecosystem(노트북+스캔 폰+스캐너 풀 샷)
- CPU 렌더라 풀 해상도 컷 하나에 2~5분. 모양 잡을 때는 SCALE=60, SAMPLES=48로 돌리고 마지막에만 풀 해상도.
- 폰/웹 화면 이미지는 `src/*.html`을 `python3 src/shot.py`로 다시 캡처해서 `screens/`에 만든다(Pretendard 폰트 필요).

## 구조 (`natssi_mockup.py`)
- 단위는 미터. 디바이스·거치대 치수 상수가 `make_device` 위쪽에 있다: `HEAD_R/HEAD_T/HEAD_X`, `HAND_*`, `DOCK_H`, `RECESS`, `CLEAR`, `LED_LEN/LED_T`
- `make_dock()` 거치대: 윗면에 머리·손잡이 모양의 홈을 Boolean으로 판다(깊이 2mm), 앞쪽 측면에 8×1mm 흰색 LED 바(+작은 영역광)
- `make_device()` 디바이스: 손잡이(타원 단면 캡슐), 머리(원반), 렌즈 유리, 주황 LED 링, 12개 도트, 주황 띠, 전원 버튼, `natssi` 로고
- `make_laptop()`, `make_phone()`, 조명(`area(...)` 3개: Key/Fill/Rim), 카메라(`camera(...)`, 컷별), 렌더 설정 `render_setup()`
- 거치대·디바이스 좌표는 `Device` 루트(회전 -24°) 기준. 카메라는 `_dw((x,y,z))`로 디바이스 좌표를 월드로 바꿔 잡는다.
- 재질은 `MAT` 딕셔너리(`principled`, `emissive`, `screen_mat` 헬퍼)

## 검증 도구 (`tools/`)
- `python3 tools/verify_dock.py` — 레이캐스트로 홈 깊이(2.0mm)·LED 바 크기(8×1mm)·거치대 치수를 숫자로 확인
- `python3 tools/frame_check.py` — 지정한 점들이 각 카메라 화면 어디에 들어오는지(0~1) 출력. 구도를 잡을 때 먼저 이걸로 맞추고 렌더한다.
- 렌더 결과는 이미지를 직접 열어 확인한다(음영, 반사, 깨진 면, 초점).

## 지금까지 한 것
- 거치대: 221×104×12mm, 윗면 2mm 곡면 안착 홈(머리+손잡이 모양, 0.6mm 여유, 가장자리 0.8mm 라운딩), 앞쪽 측면 8×1mm 흰색 LED 바(홈 안쪽에 매립). 웜그레이 재질(흰 디바이스와 대비).
- 디바이스를 홈에 맞게 재배치: 머리·손잡이 바닥을 같은 면(홈 바닥 위 0.4mm)에 맞춤.
- 렌더 `dock`, `dock_empty`, `device`, `hero` 갱신.
- **A 완료(스캐너 렌즈 구조)**: `Device_lens` → `Device_sensor_base`(r=28mm 어두운 받침, 윗면 top+0.4mm)로 바꾸고 그 위에 `Device_LED`(링 굵기 2mm로 줄임)·`Device_LEDdot*`(라운딩)·`Device_scan_lens`(지름 12mm, 높이 1.6mm, 라운딩, 청흑 코팅 재질 `scan_lens_mat`)를 얹음. 그 위를 `Device_cover_glass`(r=29mm, 두께 1.2mm, Glass BSDF IOR 1.5/Rough 0.01, 밑면 top+3.0mm)가 덮고, 세라믹 칼라 `Device_sensor_collar`가 커버를 받침. 치수 상수 `SENSOR_*`, `SCAN_LENS_*`, `COVER_*`. LED 발광 6/8 → 2.2/2.8(커버 아래 클로즈업에서 하얗게 날아가서). Cycles 바운스 transmission/transparent 16.
  - 검증: `python3 tools/verify_scanner.py`(렌즈 12.0mm, 커버 1.2mm, 렌즈 윗면은 커버 밑면보다 1.0mm, LED 링은 0.6mm 낮음)
  - 남은 문제: 지금 조명에서는 앞(-y)쪽 카메라 각도로 보면 커버 유리에 `Rim` 조명과 흰 배경벽이 거울처럼 비쳐 센서가 가려짐 → B(카메라)·D(조명)에서 반사 방향을 피해야 함. `renders/`의 기존 PNG는 아직 옛 렌즈로 렌더된 상태(마무리 단계에서 다시 렌더).
- **에코시스템 샷 추가**: 컷 `ecosystem`(`Cam_ecosystem`, 40mm, 왼쪽 앞 대각선 위). 컷별 숨김 목록 `HIDE`로 이 컷에서만 `Phone_today`를 숨김. 화면은 이 컷에서만 `SCREEN_SWAP`으로 교체: 노트북 `desktop/04_change.png`, 폰 `mobile/05_capture.png`(`tools/make_eco_screens.py`가 `screens/screen_eco_*.png`로 변환, 폰은 둥근 모서리 알파 입힘). 조명은 아직 기존 3점 조명 그대로(D 이후 다시 렌더 필요). 로고 `natssi`는 이 각도에서 뒤집혀 보임.

## 다음 작업 (사용자 요청 원문 요약 — 이 순서로 진행)
### A. 스캐너 렌즈 구조 (디바이스 머리 윗면)
1. 유지: 바깥쪽 따뜻한 오렌지 LED 링(`Device_LED`), 안쪽 12개 도트(`Device_LEDdot*`)
2. 추가: 정중앙 **지름 12mm 고광택 광학 스캔 렌즈**, 다크 블루-블랙 코팅 유리 재질(반사 선명, 아주 어두운 청흑색, 코팅 반사 약간의 청색 기운)
3. 추가: 센서부 전체를 덮는 **두께 1.2mm 투명 강화유리 커버**(IOR 1.5, Roughness 0.01). LED와 렌즈가 유리 아래에 **매립된 깊이감**이 나야 한다(LED·렌즈를 유리 밑면보다 낮게, 가장자리 둥근 라운딩).
   - 현재 `Device_lens`(r=28mm, 깊이 2mm 검은 유리)가 있으니 이것을 "센서 베이스(어두운 받침)"로 바꾸고 그 위에 렌즈·커버를 쌓는 구조로 정리한다.
   - 투명 유리는 Cycles에서 `Glass BSDF`(IOR 1.5, Roughness 0.01)나 Principled의 Transmission=1을 쓴다. 투과 때문에 노이즈가 늘면 `Max Bounces(transmission/transparent)`를 올리고 샘플을 늘린다. 유리 안쪽 면이 서로 겹치지 않게 두께(1.2mm)를 지켜 모델링한다.
   - 렌즈 지름 12mm, 커버 두께 1.2mm가 실제로 맞는지 `tools/verify_dock.py`처럼 `dimensions`를 찍어서 확인한다.
### B. 카메라: 45도 얼짱 각도(Three-quarter view) 클로즈업
- 새 컷(예: `scanner`)을 추가하고 `bpy.context.scene.camera`로 쓴다. 디바이스 좌표계 기준으로 머리 정면 대각선 45° 위에서 내려다보는 구도, 스캐너 머리부터 손잡이 끝 `natssi` 로고까지 한 화면에 들어오게.
- **피사계 심도 F-stop = 8.0** (`cam.data.dof.aperture_fstop = 8.0`). 초점 거리는 머리 중심~로고 사이(대략 제품 길이의 1/3 지점)로 맞춘다. F8로 머리와 로고가 모두 또렷한지 렌더를 확대해서 확인하고, 부족하면 사용자에게 보고한다(F값을 임의로 바꾸지 말 것).
### C. 배경 노트북
- 화면에 **'낯씨' 대시보드 그래프**가 은은하게 보이도록 화면 각도를 살짝 세운다(`make_laptop`의 `open_deg`를 키우거나 베이스 기울기 조정). 화면 이미지는 `screens/screen_web.png`. 글자 철자는 **'낯씨'**(‘낮씨’ 아님).
- 배경이므로 디바이스보다 덜 선명해도 되지만 그래프 윤곽은 알아볼 수 있어야 한다. 화면 반사가 그래프를 가리지 않게 각도·조명을 조정.
### D. 조명: 아침 햇살이 창가로 들어오는 따뜻하고 부드러운 데스크 스튜디오
- 지금 3점 조명(`Key`, `Fill`, `Rim`)을 교체/조정: 한쪽 창가 쪽에서 오는 큰 소프트 키라이트(따뜻한 색, 약 3500~4500K 느낌), 낮은 각도의 햇살 느낌, 반대편에 은은한 필, 월드 배경은 따뜻한 밝은 톤. 그림자는 부드럽게.
- 과노출 주의: 흰 세라믹 디바이스가 하얗게 날아가지 않게 노출(`Key` 파워, `view_transform`)을 맞춘다.
### 마무리
- `tools/verify_dock.py`, `tools/frame_check.py` 통과 → 작은 해상도로 구도 확인 → 풀 해상도 렌더 → `README.md`에 새 컷·치수 반영 → 사용자에게 결과 이미지와 "확인한 것/못 한 것" 보고.

## 원칙
- 디바이스 치수는 실제 제품처럼 유지(머리 지름 72mm, 손잡이 길이 120mm). 바꿀 때는 이유를 적는다.
- 상표·실존 제품 디자인을 베끼지 않는다(낯씨 오리지널 디자인).
- 렌더 확인 없이 "됐다"고 말하지 않는다.
