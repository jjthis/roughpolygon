import json
import os
import subprocess
import sys

def compile_cpp(source_file, output_file):
    """C++ 파일을 컴파일합니다."""
    result = subprocess.run(
        ["g++", "-std=c++17", "-O2", source_file, "-o", output_file],
        capture_output=True,
        text=True
    )
    return result.returncode == 0, result.stdout, result.stderr

def main():
    # 최상위 option.json에서 problem_name 읽기
    with open("./option.json", "r") as f:
        root_options = json.load(f)
    problem_name = root_options["problem_name"]
    
    # option.json 읽기
    option_path = f"./problem/{problem_name}/option.json"
    with open(option_path, "r") as f:
        options = json.load(f)
    
    test_count = options["testCount"]
    problem_dir = f"./problem/{problem_name}"
    tests_dir = f"{problem_dir}/tests"
    
    # tests 디렉토리 생성
    os.makedirs(tests_dir, exist_ok=True)
    
    # 임시 파일 목록
    temp_files = []
    
    try:
        # generator.cpp 컴파일
        generator_exe = f"{problem_dir}/generator.exe"
        temp_files.append(generator_exe)
        success, stdout, stderr = compile_cpp(f"{problem_dir}/generator.cpp", generator_exe)
        if not success:
            print(f"generator.cpp 컴파일 실패:")
            print(stderr)
            sys.exit(1)
        
        # validate.cpp 컴파일
        validate_exe = f"{problem_dir}/validate.exe"
        temp_files.append(validate_exe)
        success, stdout, stderr = compile_cpp(f"{problem_dir}/validate.cpp", validate_exe)
        if not success:
            print(f"validate.cpp 컴파일 실패:")
            print(stderr)
            sys.exit(1)
        
        # 테스트케이스 생성 및 검증
        for i in range(1, test_count + 1):
            test_file = f"{tests_dir}/{i:02d}"
            
            # generator 실행하여 테스트케이스 생성
            result = subprocess.run(
                [generator_exe, str(i)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            if result.returncode != 0:
                print(f"테스트케이스 {i} 생성 실패:")
                print(result.stderr)
                sys.exit(1)
            
            # 생성된 출력을 파일에 저장
            with open(test_file, "w") as f:
                f.write(result.stdout)
            
            # validate.cpp 실행
            with open(test_file, "r") as f:
                validate_result = subprocess.run(
                    [validate_exe],
                    stdin=f,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
            
            # validate 실패 체크 (return code != 0 또는 stderr 출력)
            if validate_result.returncode != 0 or validate_result.stderr:
                print(f"테스트케이스 {i} 검증 실패:")
                if validate_result.stderr:
                    print(validate_result.stderr)
                else:
                    print(f"return code: {validate_result.returncode}")
                sys.exit(1)
        
        print(f"모든 테스트케이스({test_count}개) 검증 완료")
    finally:
        # 임시 파일 삭제
        for temp_file in temp_files:
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except:
                    pass

if __name__ == "__main__":
    main()
