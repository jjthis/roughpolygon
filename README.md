# RoughPolygon

Polygon 스타일의 문제 검증 및 스트레스 테스트 시스템

## 프로젝트 구조

```
roughpolygon/
├── option.json              # 최상위 설정 파일 (problem_name 정의)
├── judge.py                 # 테스트케이스 생성 및 검증 스크립트
├── stress.py                # 스트레스 테스트 스크립트
├── random_stress.py         # 랜덤 스트레스 테스트 스크립트
├── judge.bat                # judge.py 실행용 배치 파일
├── stress.bat               # stress.py 실행용 배치 파일
├── random_stress.bat        # random_stress.py 실행용 배치 파일
└── problem/
    └── {problem_name}/
        ├── option.json      # 문제별 설정 파일
        ├── generator.cpp    # 테스트케이스 생성기 (testlib.h 사용)
        ├── validate.cpp     # 입력 검증기 (testlib.h 사용)
        ├── naive.cpp        # 정답 솔루션
        ├── mcs.cpp          # 테스트할 솔루션
        ├── checker.cpp      # 채점기 (선택, testlib.h 사용)
        ├── testlib.h        # Polygon testlib 헤더 파일
        ├── statement.md     # 문제 설명
        └── tests/           # 생성된 테스트케이스 저장 폴더
            ├── 01
            ├── 02
            └── ...
```

## 설정 파일

### 최상위 option.json

```json
{
    "problem_name": "폴더이름",
    "stress_limit": 30
}
```

- `problem_name`: 테스트할 문제의 이름 (problem/ 폴더 내의 디렉토리명)
- `stress_limit`: 랜덤 스트레스 테스트 실행 횟수 (random_stress.py에서 사용)

### 문제별 option.json

```json
{
    "testCount": 10,
    "checker": false
}
```

- `testCount`: 생성/테스트할 테스트케이스 개수
- `checker`: 채점기 사용 여부 (true/false)

## 사용 방법

### 1. judge.py - 테스트케이스 생성 및 검증

`generator.cpp`를 사용하여 테스트케이스를 생성하고, `validate.cpp`로 각 테스트케이스를 검증합니다.

**실행 방법:**
```bash
# Windows
judge.bat

# 또는 직접 실행
python judge.py
```

**동작:**
1. 최상위 `option.json`에서 `problem_name`을 읽습니다
2. `./problem/{problem_name}/option.json`에서 `testCount`를 읽습니다
3. `generator.cpp`를 컴파일합니다
4. `validate.cpp`를 컴파일합니다
5. `testCount` 개수만큼 테스트케이스를 생성합니다 (01, 02, ... 형식으로 `tests/` 폴더에 저장)
6. 각 테스트케이스에 대해 `validate.cpp`를 실행하여 검증합니다
7. 검증 실패 시 즉시 중단하고 에러 메시지를 출력합니다
8. 모든 테스트케이스가 통과하면 성공 메시지를 출력합니다
9. 실행 후 임시 파일(generator.exe, validate.exe)을 자동으로 삭제합니다

### 2. stress.py - 스트레스 테스트

생성된 테스트케이스에 대해 `naive.cpp`와 `mcs.cpp`의 출력을 비교합니다.

**실행 방법:**
```bash
# Windows
stress.bat

# 또는 직접 실행
python stress.py
```

**동작:**
1. 최상위 `option.json`에서 `problem_name`을 읽습니다
2. `./problem/{problem_name}/option.json`에서 `testCount`와 `checker`를 읽습니다
3. 필요한 파일들을 컴파일합니다 (`naive.cpp`, `mcs.cpp`, `checker.cpp`(있는 경우))
4. `tests/` 폴더의 테스트케이스를 1번부터 `testCount`번까지 순회합니다

**checker == false 인 경우:**
- `naive.cpp`와 `mcs.cpp`의 출력을 직접 문자열 비교
- 출력이 다르면 즉시 중단하고 두 출력을 함께 출력

**checker == true 인 경우:**
- `naive.cpp` 실행 → `answer.tmp` 파일 생성
- `mcs.cpp` 실행 → `output.tmp` 파일 생성
- `checker.cpp` 실행 (인자: `input.txt answer.tmp output.tmp`)
- `checker` 결과가 실패(_wa, _fail)면 즉시 중단
5. 실행 후 임시 파일들을 자동으로 삭제합니다

### 3. random_stress.py - 랜덤 스트레스 테스트

`generator.cpp`를 실행하여 매번 새로운 테스트케이스를 생성하고, `naive.cpp`와 `mcs.cpp`의 출력을 비교합니다. `tests/` 폴더에 저장하지 않고 메모리에서 바로 테스트합니다.

**실행 방법:**
```bash
# Windows
random_stress.bat

# 또는 직접 실행
python random_stress.py
```

**동작:**
1. 최상위 `option.json`에서 `problem_name`과 `stress_limit`을 읽습니다
2. `./problem/{problem_name}/option.json`에서 `checker`를 읽습니다
3. 필요한 파일들을 컴파일합니다 (`generator.cpp`, `naive.cpp`, `mcs.cpp`, `checker.cpp`(있는 경우))
4. `stress_limit` 횟수만큼 반복합니다:
   - `generator.cpp`를 실행하여 새로운 테스트케이스를 생성합니다
   - 생성된 테스트케이스로 `naive.cpp`와 `mcs.cpp`의 출력을 비교합니다

**checker == false 인 경우:**
- `naive.cpp`와 `mcs.cpp`의 출력을 직접 문자열 비교
- 출력이 다르면 즉시 중단하고 입력과 두 출력을 함께 출력

**checker == true 인 경우:**
- 입력을 `input.tmp` 파일에 저장
- `naive.cpp` 실행 → `answer.tmp` 파일 생성
- `mcs.cpp` 실행 → `output.tmp` 파일 생성
- `checker.cpp` 실행 (인자: `input.tmp answer.tmp output.tmp`)
- `checker` 결과가 실패(_wa, _fail)면 즉시 중단하고 입력을 함께 출력
5. 실행 후 임시 파일들을 자동으로 삭제합니다

## 요구사항

- Python 3.x
- g++ (C++17 지원)
- testlib.h (Polygon 스타일)

## 파일 설명

### generator.cpp
- `testlib.h`의 `registerGen` 사용
- 테스트케이스 번호를 인자로 받을 수 있음
- stdout으로 테스트 입력을 출력

### validate.cpp
- `testlib.h`의 `registerValidation` 사용
- 입력이 잘못되면 `quitf(_fail, ...)`로 종료
- 정상 입력이면 아무 출력 없이 종료 (return code 0)

### checker.cpp (선택)
- `testlib.h`의 `registerChecker` 사용
- 입력 파일, 정답 파일, 출력 파일을 인자로 받음
- `quitf(_wa / _ok / _fail, ...)` 사용

### naive.cpp
- 정답 솔루션
- stdin에서 입력을 받아 stdout으로 출력

### mcs.cpp
- 테스트할 솔루션
- stdin에서 입력을 받아 stdout으로 출력

## 에러 처리

다음 상황들이 구분되어 명확히 출력됩니다:
- 컴파일 에러
- 런타임 에러
- validate 실패
- checker WA / FAIL
- 출력 불일치

실패 시:
- 실패한 테스트케이스 번호
- 에러 메시지 또는 출력 내용
을 출력하고 즉시 종료합니다.
