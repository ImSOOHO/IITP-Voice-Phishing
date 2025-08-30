# IITP-Voice-Phishing

## 프로젝트 목표
* 금융 감독원의 게시글(본문 및 첨부파일)을 활용하여 보이스피싱 탐지를 위한 Vector DB를 구축하는 것


## 데이터 수집
* 금융감독원 홈페이지(<https://www.fss.or.kr/fss/bbs/B0000059/list.do?menuNo=200359>)에 있는 피해사례, 보이스피싱 체험관에서 데이터를 수집
* 피해사례: 첨부파일 있는 게시물과 없는 게시물로 나누어짐(첨부파일의 종류는 pdf,hwp,hpwx)
* 데이터 내용: 대부분 사기수법과 피해 사례를 기술하고 있음
<img width="500" height="500" alt="image" src="https://github.com/user-attachments/assets/e95cf81b-f510-4ad5-9f26-944b334ae587" />

* 보이스피싱 체험관: 게시물 마다 mp4 비디오 파일이 있음
* 데이터 내용: 가해자와 피해자 간의 보이스피싱 음성 대화 기록이 담겨있음
<img width="500" height="500" alt="image" src="https://github.com/user-attachments/assets/83645b4a-9c22-49fd-9593-396f9abb458a" />

* Selenium 기반으로 크롤링하여 첨부파일(hwp,hwpx,pdf,mp4) 및 본문 텍스트를 수집
* pdf, hwp, hwpx, 본문 텍스트: 각 자료형에서 텍스트 객체만 불러온 뒤, 수작업으로 라벨링

* mp4 파일
1. 데이터 수가 적어 직접 검증 데이터셋 구축(mp4 파일을 들으며 수작업으로 라벨링)
2. 인트로/아웃트로를 제거한 mp4 파일(trim) vs 인트로/아웃트로 + 삐처리음을 제거한 mp4 파일(trim_nobeep)에 대해 각각 whisper 전사
3. 각 결과값들과 검증 데이터간 WER(Word Error Rate), CER(Character Error Rate) 값 비교
4. 두 지표에서 인트로/아웃트로만 제거한 mp4 파일이 좋은 성능을 보여주었음
5. 인트로/아웃트로만 제거한 전사 결과를 mp4 파일에 대한 전사 결과로 사용
<img width="600" height="500" alt="image" src="https://github.com/user-attachments/assets/d4d6bc8f-5d7a-4175-9160-9da04c6c79b2" />

## 임베딩 및 Vector DB 구축
* 자료형 별로 적재된 내용이 달라서 두개의 임베딩 데이터셋을 구축하기로 결정
> 1. 사기수법 + 사례 데이터(hwp,hwpx,pdf,본문 텍스트)에 대한 vector DB
> 2. 피해자 가해자 간 보이스피싱 음성 데이터(mp4)에 대한 vector DB
* 온디바이스 환경을 고려하여 경량 임베딩 모델 사용(sentence-transformers/all-MiniLM-L6-v2)
* max_length 256 토큰을 고려하여 수집한 텍스트 중 240 토큰을 넘어가는 데이터들은 청크로 분할 후 20토큰씩 오버랩
* 각 청크를 임베딩 한 후 Faiss 기반 vector DB 구축 및 메타 데이터 저장
* hwp,hwpx,pdf,본문 텍스트에 대한 임베딩 데이터(159개 사례, 387청크 -> 약 사례 하나당 2청크)
<img width="1972" height="527" alt="image" src="https://github.com/user-attachments/assets/663db4c2-19bf-46f1-b4e1-8eba2cb20900" />
* mp4 파일에 대한 임베딩 데이터(286개 사례, 1008청크 -> 약 사례 하나당 4청크)
<img width="1956" height="679" alt="image" src="https://github.com/user-attachments/assets/ac4bd722-6694-4de0-93f8-cd46d93bf57c" />



