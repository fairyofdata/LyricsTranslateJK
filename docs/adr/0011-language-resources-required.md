# 0011. (D11) 언어 자원과 신경망 모델은 모두 필수 의존성

- 상태: 채택

SudachiPy·Kiwi·sentence-transformers·torch·transformers. 성분을 빼고 돌아가는 모드를 두지 않고, 자원이 없으면 즉시 실패한다. `ltjk doctor`가 설치와 모델 캐시를 점검하고 **리비전 해시를 기록**한다.

선택 의존성은 선택 층(SVS·ASR·보컬 분리·F0)과 IPA 교차 검증용 G2P뿐이다.
