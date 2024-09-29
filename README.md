## ursina2024
ursina 모듈을 사용한 던전형 fps 파이썬게임입니다.
ursina 모듈에 대한 설명은 https://www.ursinaengine.org/ 에서 확인가능합니다

# 게임

- **1인칭 컨트롤러**: 1인칭시점 컨트롤러 fristplayercontroler()을 사용함
- **맵**: 간단한방
- **전투 시스템**: 플레이어는 몬스터를 쏘거나 스킬을 사용할 수 있습니다.
- **적들**: 플레이어를 따라오고 2초간격으로 공격합니다.
- **조명과 그림자**: 우르시나 내장 쉐이더사용.

## 조작법

- **W/A/S/D**: 플레이어 캐릭터 이동.
- **마우스**: 시점 이동.
- **왼쪽 마우스 버튼**: 발사.
- **E**: 스킬 1 사용.
- **Tab**: 게임 일시정지/재개.

### 사용시 유의사항

- Python 3.6 이상
- Ursina 엔진 설치:

  ```bash
  pip install ursina
