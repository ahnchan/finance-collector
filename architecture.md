# FinanceCollector
Finance 정보를 수집하는 Python Application 이다. 

## Hitoric 가격 정보
매일 수행되는 것으로 이전일자의 정보를 수집하여 JSON으로 정리하여 반환한다.

## 할일
- 프로프트의 요청한 내용을 처리한다.
- Framework/Libraris에 정의된 모듈을 위주로 사용한다. 만약 추가가 필요하면, 사용자에게 물어보고 진행한다.
- Test Case를 만들어준다. 만약 API의 서비스면, .http 파일로도 만들어준다. 

## 하지말아야 할일
- 프로프트에서 요청하지 않은 작업이나 개선작업은 하지 않는다.

## Libries/Framework
FastAPI
YahooFinance

## 인증
client credential 로 API에 접근할 수 있게 한다. credential 정보는 시스템 환경설정에서 가져오고 만약없다면, .env 파일을 참조한다.

