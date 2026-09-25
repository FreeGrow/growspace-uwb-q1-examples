# 퀵스타트: 라즈베리파이로 UWB 실내 위치 데이터 받기

**GrowSpace UWB 크리에이터 키트 Q1** 개발자 태그를 라즈베리파이에 UART로 연결해 실시간 실내
위치 데이터를 받아보는 가이드. 약 10분이면 끝난다. UWB 사전 지식은 필요 없다.

English version: [quickstart-raspberry-pi.md](quickstart-raspberry-pi.md)

## 준비물

- 라즈베리파이 (GPIO가 있는 모델이면 다 됨 — 3, 4, 5, Zero 2 W 모두 가능)
- GrowSpace UWB Q1 개발자 태그 ([키트 정보](https://grow-space.io/uwb-kit-2/))
- 점퍼선 3개 (GND, TX, RX)

## 1. 3.3V 헤더에 태그 연결

개발자 태그에는 **커넥터가 두 개** 있다 — 반드시 **왼쪽 3.3V 커넥터**를 쓴다. 5V 커넥터를
라즈베리파이에 연결하면 안 된다. 파이의 GPIO UART는 3.3V 로직이라 5V 쪽을 연결하면 손상될
수 있다.

| 태그 핀 | 라즈베리파이 GPIO 핀 |
|---|---|
| GND | 6번 핀 (GND) |
| TX  | 10번 핀 (GPIO15 / RXD) |
| RX  | 8번 핀 (GPIO14 / TXD) |

태그의 TX는 파이의 RX로, 태그의 RX는 파이의 TX로 — 데이터 선 두 개는 항상 교차 연결한다.

## 2. 파이의 UART를 비운다

라즈베리파이 OS는 기본적으로 1차 UART를 로그인 콘솔로 쓰기 때문에, 그대로 두면 스크립트와
포트를 두고 충돌한다.

```bash
sudo raspi-config
# Interface Options → Serial Port
#   "시리얼 포트로 로그인 셸을 쓸까요?" → No
#   "시리얼 포트 하드웨어를 활성화할까요?" → Yes
sudo reboot
```

## 3. 설치하고 실행

```bash
git clone https://github.com/FreeGrow/growspace-uwb-q1-examples.git
cd growspace-uwb-q1-examples/python
pip install -r requirements.txt

python serial_reader.py --port /dev/serial0
```

이런 위치 데이터 스트림이 보이면 성공이다.

```
POS,-3.41,9.54,-1.53,74
```

미터 단위 `x, y, z` 좌표와 0~100 사이 품질 지수(`qf`)다. 60 이상이면 대체로 바로 써도
안정적이다.

아무것도 안 뜨면 [문제 해결 가이드](troubleshooting.ko.md#라즈베리파이-uart가-응답이-없거나-파이가-리셋된다)를 확인한다.

## 4. 실시간 지도로 보기

이 저장소에는 태그를 평면도 위에 실시간으로 표시하는 작은 웹 대시보드가 포함돼 있다.
지오펜스 존과 태그별 라벨도 지원한다.

```bash
cd visualizer
pip install -r requirements.txt
python server.py --source serial --port /dev/serial0
```

같은 네트워크의 브라우저에서 `http://<파이 IP>:8000`으로 접속한다.

## 다음 단계

- 태그 여러 개 동시에: `serial_reader.py`를 여러 포트에 각각 띄우거나, 개발자 태그 대신
  **리스너** 모듈을 쓴다 — 리스너는 감지한 모든 태그에 대해 `POS,idx,tagId,x,y,z,qf`를
  보고하므로, 파이 하나로 시리얼 연결 하나만으로 여러 태그를 추적할 수 있다.
- 구역 알림: `python/geofence.py`에 진입/이탈 히스테리시스가 있는 점-다각형 판정 예제가
  있다. 태그가 경계를 넘을 때 동작을 트리거하는 데 쓸 수 있다.
- 라즈베리파이 전체 가이드(전원, 케이스, 멀티 태그 구성): https://grow-space.io/docs/q1/raspberry-pi/
