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
    # 최상위 option.json에서 problem_name과 stress_limit 읽기
    with open("./option.json", "r") as f:
        root_options = json.load(f)
    problem_name = root_options["problem_name"]
    stress_limit = root_options["stress_limit"]
    
    # 문제별 option.json 읽기
    option_path = f"./problem/{problem_name}/option.json"
    with open(option_path, "r") as f:
        options = json.load(f)
    
    checker_enabled = options.get("checker", False)
    problem_dir = f"./problem/{problem_name}"
    
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
        
        # naive.cpp 컴파일
        naive_exe = f"{problem_dir}/naive.exe"
        temp_files.append(naive_exe)
        success, stdout, stderr = compile_cpp(f"{problem_dir}/naive.cpp", naive_exe)
        if not success:
            print(f"naive.cpp 컴파일 실패:")
            print(stderr)
            sys.exit(1)
        
        # mcs.cpp 컴파일
        mcs_exe = f"{problem_dir}/mcs.exe"
        temp_files.append(mcs_exe)
        success, stdout, stderr = compile_cpp(f"{problem_dir}/mcs.cpp", mcs_exe)
        if not success:
            print(f"mcs.cpp 컴파일 실패:")
            print(stderr)
            sys.exit(1)
        
        if checker_enabled:
            checker_exe = f"{problem_dir}/checker.exe"
            temp_files.append(checker_exe)
            success, stdout, stderr = compile_cpp(f"{problem_dir}/checker.cpp", checker_exe)
            if not success:
                print(f"checker.cpp 컴파일 실패:")
                print(stderr)
                sys.exit(1)
            # 임시 파일 경로 추가
            answer_file = f"{problem_dir}/answer.tmp"
            output_file = f"{problem_dir}/output.tmp"
            temp_files.extend([answer_file, output_file])
            input_file = f"{problem_dir}/input.tmp"
            temp_files.append(input_file)
        
        # stress_limit 횟수만큼 랜덤 테스트
        for i in range(1, stress_limit + 1):
            # generator 실행하여 테스트케이스 생성
            result = subprocess.run(
                [generator_exe, str(i)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            if result.returncode != 0:
                print(f"랜덤 테스트 {i}: generator 실행 실패")
                print(result.stderr)
                sys.exit(1)
            
            test_input = result.stdout
            
            if checker_enabled:
                # checker 사용 (Polygon 방식)
                # 입력을 임시 파일에 저장
                with open(input_file, "w") as f:
                    f.write(test_input)
                
                # naive.cpp 실행 -> answer 파일 생성
                with open(input_file, "r") as inf, open(answer_file, "w") as outf:
                    result = subprocess.run(
                        [naive_exe],
                        stdin=inf,
                        stdout=outf,
                        stderr=subprocess.PIPE,
                        text=True
                    )
                
                if result.returncode != 0:
                    print(f"랜덤 테스트 {i}: naive.cpp 런타임 에러")
                    print(result.stderr)
                    print("입력:")
                    print(test_input)
                    sys.exit(1)
                
                # mcs.cpp 실행 -> output 파일 생성
                with open(input_file, "r") as inf, open(output_file, "w") as outf:
                    result = subprocess.run(
                        [mcs_exe],
                        stdin=inf,
                        stdout=outf,
                        stderr=subprocess.PIPE,
                        text=True
                    )
                
                if result.returncode != 0:
                    print(f"랜덤 테스트 {i}: mcs.cpp 런타임 에러")
                    print(result.stderr)
                    print("입력:")
                    print(test_input)
                    sys.exit(1)
                
                # checker 실행
                result = subprocess.run(
                    [checker_exe, input_file, answer_file, output_file],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                
                # checker 결과 확인 (return code != 0이면 실패)
                if result.returncode != 0:
                    print(f"랜덤 테스트 {i}: checker 실패")
                    if result.stderr:
                        print(result.stderr)
                    if result.stdout:
                        print(result.stdout)
                    print("입력:")
                    print(test_input)
                    sys.exit(1)
            
            else:
                # checker 없음: naive vs mcs 출력 직접 비교
                # naive.cpp 실행
                naive_result = subprocess.run(
                    [naive_exe],
                    input=test_input,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                
                if naive_result.returncode != 0:
                    print(f"랜덤 테스트 {i}: naive.cpp 런타임 에러")
                    print(naive_result.stderr)
                    print("입력:")
                    print(test_input)
                    sys.exit(1)
                
                # mcs.cpp 실행
                mcs_result = subprocess.run(
                    [mcs_exe],
                    input=test_input,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                
                if mcs_result.returncode != 0:
                    print(f"랜덤 테스트 {i}: mcs.cpp 런타임 에러")
                    print(mcs_result.stderr)
                    print("입력:")
                    print(test_input)
                    sys.exit(1)
                
                # 출력 비교
                if naive_result.stdout != mcs_result.stdout:
                    print(f"랜덤 테스트 {i}: 출력 불일치")
                    print("입력:")
                    print(test_input)
                    print("naive 출력:")
                    print(naive_result.stdout)
                    print("mcs 출력:")
                    print(mcs_result.stdout)
                    sys.exit(1)
        
        print(f"모든 랜덤 테스트({stress_limit}개) 통과")
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
