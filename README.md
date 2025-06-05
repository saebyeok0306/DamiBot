# 리듬게임 기록 관리 봇, 담이

현재는 DJMAX RESPECT V만 지원하며, 다른 리듬게임은 아직 예정에 없습니다.<br>
취미로 개발 중이며 봇의 기능은 계속해서 추가될 예정입니다.

## 기능

- [X] 결과창 이미지를 통한 기록 관리
- [X] 기록 갱신인 경우 이전 기록과 비교하여 성장률 표시
- [X] 기록 조회
- [ ] 기록 삭제
- [X] 성장 그래프 보기
- [X] 기록 공유 (아이디 기반)
- [X] 곡 추가 (관리자)
- [X] 썸네일, 세부난이도 표기
- [ ] 레코드 정보 기반 난이도 및 곡 추천

## 개선필요

- [ ] AI 이미지 인식률 개선 필요 (세부판정과 짧은 곡제목 인식률이 상대적으로 떨어짐)
- [X] 검색 기능 개선 필요 (코사인 유사도 방식의 한계가 있어서 임베딩 방식으로 추가 개선 필요)
- [ ] 파일 분리 개선 필요
- [ ] FREESTYLE 결과창 이외에 LADDER, ONLINE 결과창 인식 가능하게? (이미지 분류 기능 필요)

## 라이브러리

- discord.py
- openai
- sqlalchemy (oracle db)
- scikit-learn (cosine similarity)

## 이미지

![result](https://github.com/westreed/DamiBot/blob/main/docs/img/1-1.png?raw=true)
![record](https://github.com/westreed/DamiBot/blob/main/docs/img/1-2.png?raw=true)
