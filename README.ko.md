# GrowSpace UWB Q1 — 예제 코드

**GrowSpace UWB 크리에이터 키트 Q1**(UWB 실내 위치측위 개발키트, 정확도 10~30cm, 시리얼·MQTT 출력)용 예제 코드입니다.

- 키트·가격: https://grow-space.io/uwb-kit/
- 공식 가이드: https://grow-space.io/docs/q1/

## 출력 형식

시리얼(115200bps)로 `lep`을 보내면 좌표가 텍스트로 나옵니다.

| 장치 | 형식 | 예시 |
|---|---|---|
| 개발자 태그 | `POS,x,y,z,qf` | `POS,-3.41,9.54,-1.53,74` |
| 리스너 | `POS,idx,태그ID,x,y,z,qf` | `POS,0,365D,-3.41,9.54,-1.53,74` |
| 게이트웨이(MQTT) | `uwb/gateway/...` 아래 `tags` 배열 JSON | `{"gatewayID":"GR21BA","tags":[{"id":"GR2c3c","x":-3.95,"y":0.23,"z":-2.48}]}` |

좌표 단위는 미터, `qf`는 0~100 품질지수(60 이상이면 대체로 안정)입니다.

## 예제

| 파일 | 내용 |
|---|---|
| `python/serial_reader.py` | 태그·리스너 좌표 실시간 출력(QF 필터) |
| `python/heading_two_tags.py` | 태그 2개(앞·뒤)로 로봇 방향각 계산 |
| `python/geofence.py` | 다각형 구역 진입·이탈 알림(경계 깜빡임 방지) |
| `python/mqtt_subscriber.py` | 게이트웨이 MQTT 좌표 구독 |
| `arduino/uno_altsoftserial` | 아두이노 우노(AltSoftSerial, D8/D9) |
| `arduino/mega_serial1` | 아두이노 메가(하드웨어 Serial1) |

## 배선 주의

개발자 태그 커넥터는 **우측 5V(아두이노)**, **좌측 3.3V(라즈베리파이·ESP32)**입니다. 라즈베리파이에 5V 쪽을 연결하면 UART가 손상될 수 있습니다. TX↔RX는 교차 연결합니다.

## 관련 글

- UWB 개발키트 Q1으로 만드는 프로젝트 4가지: https://grow-space.io/blog/uwb-q1-project-ideas/

문의: https://grow-space.io/uwb-kit/
