
# Noton Telegram Bot

Telegram bot api를 사용해 구현한 텔레그램 봇 입니다.


## 사용 언어 및 라이브러리

* Python 3
* sqlite3
* threading
* datetime
* BeautifulSoup

## 사용법
텔레그램에서 @noton_bot 을 초대 한 후, 대화창에 명령어를 입력하여 사용합니다.

### 명령어 목록

#### -주사위 돌리기
```Python
/dice
```
* 1~999 사이의 랜덤 수를 가져옵니다.

#### -선택하기

```python
/select 항목1 항목2 항목3...
```

* 각 항목 별로 공백(" ")을 두어 구분합니다

#### -날씨
```Python
/weather
```
네이버 서울 날씨를 파싱해서, 현재 온도, 미세/초미세먼지 수치를 가져옵니다.

#### -로그
```Python
/log
```
*(어드민 전용 명령어 입니다.)*

* 명령어를 사용하기 직전의 최근 로그 10개를 가져옵니다.


### 추가 예정
* 스케쥴 관리 시스템
* 추가 로그 데이터 및 해당 데이터 분석

## 라이선스

None

## 기타
* 프로젝트에 관한 질문은 [메일](notonalcyone@gmail.com)로 부탁드립니다.
