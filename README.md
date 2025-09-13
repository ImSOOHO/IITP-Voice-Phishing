# IITP-Voice-Phishing(진행중)

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

## 참고사항
* Discussion Point
> 1. wav 파일 하나에 여러 가지 보이스피싱 사례가 담겨있고 무음으로 구간이 나누어져 있습니다. 이를 무음 구간으로 스플릿(혹은 사례 별로 스플릿) 해서 전사를 따로 따로 하고, WER 값을 확인해보면 좋을 것 같습니다(기존 WER 약 29~30%)
> 2. 현재 MiniLM으로 임베딩 하기 위해 텍스트들을 240토큰 단위로 청크 분할한 상태입니다. 그러다 보니 마지막 청크에는 텍스트가 적게 담기는 경우가 있습니다. 이렇게 단어 토큰이 적게 들어간 청크에 대해서 어떻게 처리할지 고민해보면 좋을 것 같습니다.

* 데이터에 수작업이 많이 들어갔다 보니, 코드 상에 드러나지 않은 부분들이 꽤 있습니다. 그래서 각 데이터 프레임이 무엇을 의미하는지 그리고 어떻게 해서 만들었는지를 간략하게 설명해보겠습니다.
1. Crawling: 크롤링 한 코드들을 모아놓은 폴더입니다
> 생성파일: text_to_text.json(첨부파일이 없고, 게시글에 보이스피싱 사례가 담겨있는 형태는 바로 json으로 만들었습니다.)
2. TO_text: 수집한 첨부파일에서 텍스트를 추출하는 코드들을 모아두었습니다.
> 생성파일: hwp_to_text.json, hwpx_to_text.json, pdf_to_text.json
3. MP4: MP4 파일의 경우 세개의 파일이 존재 합니다. 
> 생성파일: wav_to_text_real.json, trim_nobeep_text.json, trim_nobeep_text.json
>
> wav_to_text_real.json: wav 파일에 whisper를 전사한 결과입니다.
> 
> trim_nobeep_test.json: wav 파일에 있는 인트로, 아웃트로 부분을 제거하고 삐소리를 무음 처리한 후 whisper를 전사한 결과입니다.
> 
> trim_test.json: wav 파일에 있는 인트로, 아웃트로 부분만 제거하고 전사한 결과입니다.

4. Merge: text로 변환한 json 파일들을 병합하는 작업을 진행한 코드입니다. 해당 부분에는 수작업이 많았습니다.
> 생성파일: wav_to_text_real.csv, merged_output.csv, preprocessed_merged_output.csv, preprocessed_merged_output_V2.csv, preprocessed_merged_output_V3.csv, json_final.json
> wav_to_text_real.csv: wav_to_text_real.json 파일을 csv 형태로 변환한 파일입니다.
> 
> merged_output.csv: text로 변환한 pdf,hwp,hwpx,본문 텍스트들을 csv 형태로 병합했습니다.
>
> preprocessed_merged_output.csv: rule base로 위의 파일을 전처리 하기가 어려워 수작업으로 merged_output.csv 에서 사기수법 및 사례를 추출한 데이터입니다.
>
> preprocessed_merged_output_V2.csv: preprocessed_merged_output.csv 와 wav_to_text_real.csv 파일을 병합했습니다. 이후 wav 전사 결과가 좋지 않아, 실제 mp4 파일을 들으며 사례 분할 및 오타 수정 처리를 진행했습니다.
>
> preprocessed_merged_output_V3.csv: preprocessed_merged_output_V2.csv 에서 의미없는 데이터들을 삭제했습니다.
>
> json_final.json: preprocessed_merged_output_V3.csv 파일을 json 형태로 만들어 최종 데이터셋을 구축했습니다.
>> wav 파일에 대한 전사 결과에 손수 라벨링한 데이터는 검증 용도로만 사용했습니다. 실제 보이스피싱 상황에서 들어오는 음성데이터는 손수 라벨링 된 정확한 데이터와 다르기 때문입니다. 따라서 vectorDB를 구축하는 과정에서 사용한 MP4 변환 결과는 라벨링한 데이터가 아닌 trim_test.json 결과에 전처리를 가해서 사용했습니다. trim_test.json, trim_nobeep_test.json 에 대해서 WER, CER 값을 비교해본 결과, trim_test.json의 결과값이 근소하게나마 더 좋았기 때문입니다.

>> 정리하자면, preprocessed_merged_output_V3.csv, json_final.json 파일에 들어있는 mp4 파일에 대한 text변환 결과는 검증용 라벨링 데이터로만 사용하고, 실제 vectorDB를 구축하는데는 사용하지 않았다는 것입니다!
5. Embedding: hwp,hwpx,pdf,본문 텍스트에 대한 임베딩 하나, mp4 파일 전사 결과에 대한 임베딩 하나, 총 두개의 vectorDB를 구축하는 코드입니다.(MP4와 나머지 파일들간 데이터의 내용이 달라, 따로 구축했습니다)
> 생성파일: df_scored, df_scored_fixed.csv, mp4_to_chunk.csv, others_to_chunk.csv, mp4_vector_db_metadata.parquet, mp4_vector_db.index, others_vector_db_metadata.parquet, others_vector_db.index
>
> df_scored: trim_nobeep_test.json, trim_test.json 간의 WER 값과 CER 값을 비교하는 과정 중에 생성했던 데이터입니다.
>
> df_scored_fixed.csv: df_scored.csv 에서 라벨링 된 mp4 결과와 trim_test.json 전사 결과만 가져왔습니다.(raw 와 trim 칼럼) 라벨링 결과와 인트로/아웃트로 제거 후 전사 결과는 trim_test.json 에서 충분히 가져올 수 있기 때문에 굳이 df_scored 에서 추출할 필요는 없습니다.
>> 라벨링 데이터는 각 사례에 대해 사례1, 사례2 이런식으로 사례 구분이 되어 있지만, 인트로/아웃트로를 제거한 wav 파일의 전사 결과에는 사례 구분이 되어 있지 않습니다. 따라서 라벨링 된 데이터를 보며 수작업으로 사례 구분을 해주었습니다.

> mp4_to_chunk.csv: df_scored_fixed.csv 에서 사례 구분이 된 전사 결과(trim 칼럼)를 가져와 청크 분할을 진행한 결과입니다.
> 
> others_to_chunk.csv: preprocessed_merged_output_V3 에서 mp4를 제외한 나머지 파일들에 대해 청크 분할을 진행한 결과입니다.
> 
> mp4_vector_db_metadata.parquet, mp4_vector_db.index: Faiss를 통해 mp4_to_chunk.csv 파일을 메타 데이터 및 vectorDB 형태로 저장한 결과입니다.
>
> others_vector_db_metadata.parquet, others_vector_db.index: Faiss를 통해 others_to_chunk.csv 파일을 메타 데이터 및 vertorDB 형태로 저장한 결과입니다.
