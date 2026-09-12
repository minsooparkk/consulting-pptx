# consulting-pptx

**원고를 논리적인 슬라이드로 정리하고, PowerPoint에서 직접 편집할 수 있는 컨설팅 보고서를 만드는 AI 스킬입니다.**

Pretendard 글꼴과 네이비·블루 기본 양식을 바탕으로 새 PPTX 제작, 기존 자료 재구성, 글꼴·테마 통일을 지원합니다. Codex와 Claude Code에서 사용할 수 있도록 `SKILL.md`, 네이티브 PPTX 템플릿, 디자인 규격, 설치·검수 도구를 함께 제공합니다.

> 독립 실행형 PPT 자동 생성 앱이 아닙니다. AI 에이전트가 이 스킬의 지침과 리소스를 읽고, 사용 가능한 파일 도구로 PPTX를 제작하는 방식입니다.

## 주요 기능

| 기능 | 설명 |
| --- | --- |
| 메시지 중심 구성 | 한 슬라이드에 하나의 중심 메시지를 두고, 주제 제목·결론형 Header·본문 근거를 구분합니다. |
| 일관된 보고서 양식 | 16:9 화면, Pretendard, 네이비 제목 밴드, 블루 강조색, 공통 Footer를 적용합니다. |
| 편집 가능한 결과물 | 텍스트·표·도형·연결선·편집형 차트를 사용하며, 슬라이드 전체를 이미지로 대체하지 않습니다. |
| 기존 PPTX 스타일 수정 | 내용·슬라이드 순서·발표자 노트·도식 관계를 보존하면서 요청한 서식을 수정하도록 안내합니다. |
| 근거와 출처 관리 | 주요 주장과 수치를 원자료에 대응시키고, 상세 출처와 조건을 발표자 노트에 남깁니다. |
| 구조 검수 | ZIP/XML 무결성, 내부 관계, 도형 ID, 슬라이드 경계와 기본 양식의 일부 항목을 검사합니다. |

## 빠른 시작

### 1. 준비 사항

- **Codex 또는 Claude Code**: 로컬 스킬을 읽고 파일을 생성·수정할 수 있는 환경
- **Python 3.9 이상**: 제공되는 설치·구조 검수 스크립트 실행용. 두 스크립트는 표준 라이브러리만 사용합니다.
- **Git 및 저장소 접근 권한**: 아래 복제 방식으로 설치할 때 필요
- **Pretendard Regular/Bold**: 기본 디자인으로 제작·렌더링하는 환경에 별도 설치 필요
- **PPTX 제작 도구**: 호스트의 문서 도구 또는 `python-pptx` 같은 OOXML 라이브러리
- **PowerPoint 또는 신뢰할 수 있는 렌더러**: 실제 화면 검수용

Pretendard 글꼴 파일, PPTX 생성 라이브러리, 렌더러는 이 저장소에 포함되지 않으며 설치 스크립트가 자동으로 설치하지 않습니다.

### 2. 저장소 복제

```sh
git clone https://github.com/minsooparkk/consulting-pptx.git
cd consulting-pptx
```

폴더 이름을 `consulting-pptx`로 유지하고, `SKILL.md`·`assets`·`references`·`scripts`를 함께 보관하세요. ZIP으로 내려받았다면 압축 해제한 폴더 이름을 `consulting-pptx`로 바꾼 뒤 실행합니다.

### 3. 설치

먼저 설치 경로와 계획을 확인한 뒤 설치합니다.

```sh
python scripts/install.py --target all --dry-run
python scripts/install.py --target all
```

환경에 따라 `python` 대신 `python3` 또는 `py -3`를 사용하세요.

| 옵션 | 설치 위치 |
| --- | --- |
| `--target codex` | `~/.agents/skills/consulting-pptx` |
| `--target claude` | `~/.claude/skills/consulting-pptx` |
| `--target all` | 위 두 경로. 기본값입니다. |

한 도구에만 설치하려면 다음 중 하나를 실행합니다.

```sh
python scripts/install.py --target codex
python scripts/install.py --target claude
```

설치 후 Codex 또는 Claude Code를 열어 `consulting-pptx`가 스킬 목록에서 인식되는지 확인하세요. 설치 파일 복사 성공과 실제 앱에서의 스킬 로딩 확인은 별개입니다.

### 4. 업데이트

복제한 원본 저장소에서 최신 내용을 받은 뒤, 변경된 설치본을 교체합니다.

```sh
git pull --ff-only
python scripts/install.py --target all --replace --dry-run
python scripts/install.py --target all --replace
```

- 동일한 설치본은 다시 복사하지 않습니다.
- 다른 내용의 설치본이 있으면 `--replace` 없이는 중단합니다.
- 교체 시 기존 파일은 `~/.skill-backups/consulting-pptx/<target>/<timestamp>/`에 백업합니다.
- 심볼릭 링크인 설치 경로는 자동 교체하지 않습니다.
- 다른 사용자 홈을 대상으로 하려면 `--home <경로>`를 지정할 수 있습니다.

## 사용 예시

스킬 설치 후 AI 에이전트에 원고나 수정할 파일을 제공하고, 스킬 이름과 원하는 결과를 함께 요청합니다. 다음은 예시 프롬프트입니다.

### 새 보고서 제작

```text
consulting-pptx 스킬로 첨부한 원고를 컨설팅 보고용 PPTX로 만들어줘.
먼저 슬라이드별 주제 제목, 결론형 Header, 본문 근거, 표현 방식을 정리해줘.
Pretendard·네이비/블루 기본 양식을 사용하고, 표와 도식은 편집 가능하게 만들어줘.
주요 주장과 수치의 출처는 발표자 노트에 남겨줘.
```

### 기존 자료 재구성

```text
consulting-pptx 스킬로 이 자료의 흐름을 재구성해줘.
한 슬라이드에 하나의 중심 메시지를 두고 Header만 읽어도 논리가 이어지게 해줘.
제공한 원자료에 없는 수치나 사례는 추가하지 말고, 미확정 사항을 구분해줘.
```

### 서식만 통일

```text
consulting-pptx 스킬로 첨부 PPTX의 글꼴과 테마만 기본 양식으로 통일해줘.
내용, 슬라이드 개수와 순서, 발표자 노트, 표·도식 관계는 보존해줘.
원본을 덮어쓰지 말고 새 PPTX로 저장한 뒤 변경 전후를 비교해줘.
```

## 기본 디자인

| 항목 | 기본값 |
| --- | --- |
| 화면 비율 | 16:9, 약 13.333 × 7.5인치 |
| 글꼴 | Pretendard Regular / Bold |
| 주제 제목 | 네이비 밴드 안의 짧은 명사형 제목, 흰색 30pt Bold |
| Header | 제목 아래 흰 영역의 결론·권고·시사점, 18pt Bold |
| 본문 | 15~16pt, 표 기본 14.5pt. 본문 글자는 14pt 미만으로 축소하지 않음 |
| 주 강조색 | `#1C3F7D` |
| 보조 블루 | `#2F5AA8` |
| Footer | 왼쪽 발표 전체 제목, 오른쪽 실제 페이지 번호 |

Header는 화면상 2줄을 우선하고 최대 3줄로 제한합니다. 내용이 많으면 글자를 자동 축소하기보다 문장을 압축하거나 슬라이드를 나눕니다. 본문은 정보 관계에 맞춰 표, 프로세스, 스윔레인, 트리, 타임라인 등으로 구성합니다.

사용자가 지정한 양식이나 승인된 기존 양식이 있으면 기본 디자인보다 우선합니다. 상세 규격은 [디자인 가이드](references/design-spec.md)와 [디자인 토큰](assets/design-tokens.json)을 참고하세요.

## 제작과 검수 흐름

1. **자료 확인**: 내용자료, 디자인 참고자료, 수정 대상 파일을 구분합니다.
2. **메시지 설계**: 슬라이드별 제목·Header·근거·표현 방식·출처·미확정 사항을 정리합니다.
3. **PPTX 제작**: [기본 템플릿](assets/consulting-template.pptx)을 재사용하고 네이티브 개체로 구성합니다.
4. **사실 확인**: 원자료와 주장·수치를 대조하고, 상세 조건과 출처를 노트에 남깁니다.
5. **구조 검사**: 제공 스크립트로 오류와 경고를 확인합니다.
6. **시각 검수**: PowerPoint 또는 렌더러로 모든 슬라이드의 잘림·겹침·글꼴을 확인합니다.
7. **전달**: 편집 가능한 PPTX와 실제 검수 범위, 남은 확인사항을 제공합니다.

템플릿의 예시 문구와 도식 항목은 실제 내용으로 교체하고, 사용하지 않은 예시 슬라이드는 삭제해야 합니다. 예시는 검증된 사실이나 실제 보고서의 근거가 아닙니다.

### 검수 명령

저장소 또는 설치된 스킬 폴더를 기준으로 실행합니다. `output.pptx`는 실제 산출물 경로로 바꾸세요.

```sh
# 기본 네이비·Pretendard 양식과 구조 검사
python scripts/validate_deck.py output.pptx

# 검사 결과를 JSON 파일로 저장
python scripts/validate_deck.py output.pptx --json qa.json

# 사용자 지정 양식: 기본 디자인 규격 검사를 제외하고 구조 검사
python scripts/validate_deck.py output.pptx --structure-only
```

오류가 있으면 종료 코드 `1`, 오류가 없으면 `0`을 반환합니다. `errors`를 수정하고 `warnings`도 검토하세요.

> **구조 검사 통과는 완성도 보증이 아닙니다.** 이 스크립트는 렌더링, 텍스트 넘침·겹침, 사실·출처 검증을 수행하지 않으며, 완전한 OOXML 스키마 검증기도 아닙니다. 결과의 `visual_check`는 `NOT_PERFORMED`로 표시됩니다. 그룹 내부 좌표와 전체 스타일 상속 등은 별도 확인이 필요합니다.

## 저장소 구성

```text
consulting-pptx/
├── README.md
├── SKILL.md                         # 에이전트가 읽는 실행 지침
├── assets/
│   ├── consulting-template.pptx     # 네이티브 기본 템플릿과 본문 예시
│   └── design-tokens.json           # 좌표·색상·글꼴 등 기계 판독 규격
├── references/
│   ├── design-spec.md              # 공통 디자인 규격
│   ├── content-and-qa.md           # 내용 설계와 검수 기준
│   └── pptx-implementation.md      # PPTX 구현·이식성·OOXML 주의사항
└── scripts/
    ├── install.py                  # Codex / Claude Code 설치·백업
    └── validate_deck.py            # 읽기 전용 구조 검사
```

## 사용 시 유의사항

- 스킬은 기본 슬라이드 장수를 강제하지 않습니다. 자료와 요청 범위에 맞춰 구성합니다.
- 스타일 수정만 요청했다면 내용을 새로 쓰거나 임의로 페이지를 추가하지 않습니다.
- 글꼴 지정과 실제 글꼴 설치·임베딩은 다릅니다. Pretendard가 없으면 설치 또는 대체 글꼴 승인이 필요합니다.
- 이미지형 PPTX는 원래부터 편집 가능한 자료와 다릅니다. 이미지 분석만으로 정확한 글꼴이나 원래 개체 구조를 확인했다고 볼 수 없습니다.
- 생성 품질과 실행 가능 범위는 사용하는 에이전트, 문서 도구, 글꼴, 렌더러 환경에 따라 달라집니다.
- 현재 저장소에는 별도 `LICENSE` 파일이 없습니다. 이용·재배포 허용 범위는 저장소 소유자에게 확인하세요.

## 상세 문서

- [스킬 실행 지침](SKILL.md)
- [디자인 규격](references/design-spec.md)
- [내용 설계와 QA](references/content-and-qa.md)
- [PPTX 구현과 이식성](references/pptx-implementation.md)

