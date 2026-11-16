"""에코시스템 샷용 화면 이미지 만들기: desktop/·mobile/ 캡처 → screens/screen_eco_*.png
폰 화면은 기존 screen_phone1.png의 둥근 모서리 알파를 그대로 입힌다."""
import os
from PIL import Image
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WEB = os.path.join(ROOT, "desktop", "04_change.png")       # 변화(볼 붉은기 그래프)
PHONE = os.path.join(ROOT, "mobile", "05_capture.png")     # 오늘의 얼굴 날씨 찍기(스캔 화면)
Image.open(WEB).convert("RGB").save(os.path.join(ROOT, "screens", "screen_eco_web.png"))
ref = Image.open(os.path.join(ROOT, "screens", "screen_phone1.png"))
ph = Image.open(PHONE).convert("RGB").resize(ref.size, Image.LANCZOS)
ph.putalpha(ref.getchannel("A"))
ph.save(os.path.join(ROOT, "screens", "screen_eco_phone.png"))
print("saved", ref.size)
