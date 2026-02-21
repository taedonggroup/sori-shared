# SORI-shared — 협업 공유 저장소

> 이 저장소는 협업자가 파일을 공유하는 전용 공간입니다.
> 실제 개발 코드는 [taedonggroup/sori](https://github.com/taedonggroup/sori)에서 관리됩니다.

## 폴더 구조

| 폴더 | 용도 |
|------|------|
| `01_requirements/` | 요구사항 정의서, 기능 명세 |
| `02_design/` | 화면 설계, 와이어프레임, UI 레퍼런스 |
| `03_assets/` | 이미지, 아이콘, 폰트 등 리소스 |
| `04_feedback/` | 검증 결과, 피드백 리포트 |
| `05_reference/` | 참고 자료, 경쟁사 분석 등 |

## 파일 등록 방법

**반드시 `SHARED_RULES.md`를 읽고 형식에 맞게 파일을 올려주세요.**
Claude Code가 파일 형식을 기반으로 개발에 반영합니다.

## 작업 흐름

```
협업자 파일 업로드 → SUMMARY.md 업데이트 → 스타크에게 알림
       ↓
Claude Code가 sori-shared 읽기 → sori 프로젝트에 반영
```
