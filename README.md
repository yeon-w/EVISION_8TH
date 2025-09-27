# EVISION_8TH

week 1:
flask로 reflected XSS, Stored XSS 취약점이 있는 방명록 시스템 구현
메인페이지('/'): 검색 폼 + 방명록 작성 폼
검색 기능('/search'):검색 결과 출력
방명록 기능('write'):이름과 메시지 입력 후 저장 -> 모든 방명록 출력

week 2:
SQL injection 발생하는 부분 아이디 입력시 주석처리후 잘못 된 비밀번호 입력 후에도 로그인 되는 부분을 prepared statement 사용해서 방지 후 주석 처리 해도 올바른 비밀번호 입력후 로그인 되게끔 패치.
