# 설정 가이드

## 1. Notion 데이터베이스 요구사항

"날짜 / 과목 / 제목" 구조 그대로 사용하면 됩니다. 속성별 타입:

- **제목**: 타입이 `title`인 속성은 이름 상관없이 스크립트가 자동으로 찾습니다. 별도 설정 불필요.
- **날짜** (`date` 타입): 기본값은 `Date` 인데, `날짜`처럼 이름이 다르면 3-3 단계에서 지정.
- **과목** (`select`, 단일 선택 타입): 기본값은 `과목`. 이름이 다르면 3-3 단계에서 지정.
- (선택) **Tags** (`multi_select` 타입, 여러 개 선택): 사용 중이면 이름을 지정, 없으면 무시됩니다.

> 과목은 select(알약 하나), Tags는 multi_select(알약 여러 개)로 서로 다른 타입입니다. 지금 쓰시는 "과목"은 select 타입이라 `NOTION_SUBJECT_PROPERTY` 로 매핑됩니다.

## 2. Notion Integration 만들기

1. https://www.notion.so/my-integrations 접속 → **New integration** 클릭
2. 이름 지정 (예: `TIL Sync`), 워크스페이스 선택 후 생성
3. **Internal Integration Secret** 값을 복사해둠 (이게 `NOTION_TOKEN`)
4. TIL 데이터베이스 페이지로 이동 → 우측 상단 `…` 메뉴 → **연결(Connections)** → 방금 만든 `TIL Sync` 통합 추가
   - 이 단계를 빼먹으면 API가 "찾을 수 없음" 오류를 냅니다.
5. 데이터베이스 URL에서 32자리 ID를 복사 (이게 `NOTION_DATABASE_ID`)
   - 예: `https://www.notion.so/myworkspace/1a2b3c4d5e6f...?v=...` → `1a2b3c4d5e6f...` 부분

## 3. GitHub 저장소 설정

### 3-1. 기존 레포 초기화

기존 레포를 밀고 새로 시작하고 싶다고 하셨으니, 둘 중 편한 방법으로 하세요.

**A) GitHub에서 레포 삭제 후 재생성**
- Settings → 맨 아래 Delete this repository
- 새로 같은 이름으로 생성 후, 이 폴더의 내용을 push

**B) 로컬 히스토리만 초기화 (레포는 유지)**
```bash
cd your-repo
rm -rf .git
git init
git add .
git commit -m "chore: TIL 자동화 초기 설정"
git branch -M main
git remote add origin git@github.com:{사용자명}/{저장소명}.git
git push -f origin main
```

### 3-2. Secrets 등록

레포 → **Settings → Secrets and variables → Actions → New repository secret**

| Name | Value |
|---|---|
| `NOTION_TOKEN` | 2단계에서 복사한 Integration Secret |
| `NOTION_DATABASE_ID` | 2단계에서 복사한 Database ID |

### 3-3. Variables 등록

같은 화면의 **Variables** 탭에서 등록 (실제 DB 속성 이름과 다르면 반드시 등록):

| Name | Value 예시 |
|---|---|
| `NOTION_DATE_PROPERTY` | `날짜` (기본값은 `Date`) — 이미 등록하신 값 |
| `NOTION_SUBJECT_PROPERTY` | `과목` (select 타입, 기본값도 `과목`이라 스크린샷 구조면 안 넣어도 동작하지만 명시해두면 안전) |
| `NOTION_TAGS_PROPERTY` | 안 쓰시면 등록 불필요 (기본값 `Tags`, 없는 속성이면 그냥 무시됨) |

### 3-4. Actions 쓰기 권한 확인

**Settings → Actions → General → Workflow permissions** 에서
**"Read and write permissions"** 를 선택하고 저장하세요. (자동 커밋/푸시에 필요)

## 4. 테스트

1. 위 설정을 마친 뒤 레포의 **Actions** 탭 → `TIL Notion Sync` 워크플로 선택
2. **Run workflow** 버튼으로 수동 실행 (workflow_dispatch)
3. `TIL/{연도}/{월}/` 아래 파일이 생기고 README가 갱신되는지 확인

정상 동작을 확인한 뒤에는 매일 KST 00:05 (UTC 15:05)에 자동으로 실행됩니다.

## 5. 알려진 제한사항

- Notion **표(table)** 블록, **컬럼(column) 레이아웃**은 아직 변환하지 않습니다 (필요하면 추가 구현 가능).
- 이미지가 많은 페이지는 다운로드 시간이 조금 걸릴 수 있습니다.
- 크론 스케줄은 GitHub Actions 인프라 상황에 따라 몇 분 정도 늦게 실행될 수 있습니다.
