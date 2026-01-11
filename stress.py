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
    checker_enabled = options.get("checker", False)
    problem_dir = f"./problem/{problem_name}"
    tests_dir = f"{problem_dir}/tests"
    
    # 임시 파일 목록
    temp_files = []
    
    try:
        # 컴파일
        naive_exe = f"{problem_dir}/naive.exe"
        temp_files.append(naive_exe)
        success, stdout, stderr = compile_cpp(f"{problem_dir}/naive.cpp", naive_exe)
        if not success:
            print(f"naive.cpp 컴파일 실패:")
            print(stderr)
            sys.exit(1)
        
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
        
        # 테스트케이스 순회
        for i in range(1, test_count + 1):
            test_file = f"{tests_dir}/{i:02d}"
            
            if not os.path.exists(test_file):
                print(f"테스트케이스 {i} 파일이 존재하지 않습니다: {test_file}")
                sys.exit(1)
            
            if checker_enabled:
                # checker 사용 (Polygon 방식)
                
                # naive.cpp 실행 -> answer 파일 생성
                with open(test_file, "r") as inf, open(answer_file, "w") as outf:
                    result = subprocess.run(
                        [naive_exe],
                        stdin=inf,
                        stdout=outf,
                        stderr=subprocess.PIPE,
                        text=True
                    )
                
                if result.returncode != 0:
                    print(f"테스트케이스 {i}: naive.cpp 런타임 에러")
                    print(result.stderr)
                    sys.exit(1)
                
                # mcs.cpp 실행 -> output 파일 생성
                with open(test_file, "r") as inf, open(output_file, "w") as outf:
                    result = subprocess.run(
                        [mcs_exe],
                        stdin=inf,
                        stdout=outf,
                        stderr=subprocess.PIPE,
                        text=True
                    )
                
                if result.returncode != 0:
                    print(f"테스트케이스 {i}: mcs.cpp 런타임 에러")
                    print(result.stderr)
                    sys.exit(1)
                
                # checker 실행
                result = subprocess.run(
                    [checker_exe, test_file, answer_file, output_file],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                
                # checker 결과 확인 (return code != 0이면 실패)
                if result.returncode != 0:
                    print(f"테스트케이스 {i}: checker 실패")
                    if result.stderr:
                        print(result.stderr)
                    if result.stdout:
                        print(result.stdout)
                    sys.exit(1)
            
            else:
                # checker 없음: naive vs mcs 출력 직접 비교
                # naive.cpp 실행
                with open(test_file, "r") as f:
                    naive_result = subprocess.run(
                        [naive_exe],
                        stdin=f,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True
                    )
                
                if naive_result.returncode != 0:
                    print(f"테스트케이스 {i}: naive.cpp 런타임 에러")
                    print(naive_result.stderr)
                    sys.exit(1)
                
                # mcs.cpp 실행
                with open(test_file, "r") as f:
                    mcs_result = subprocess.run(
                        [mcs_exe],
                        stdin=f,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True
                    )
                
                if mcs_result.returncode != 0:
                    print(f"테스트케이스 {i}: mcs.cpp 런타임 에러")
                    print(mcs_result.stderr)
                    sys.exit(1)

                # print("naive 출력:")
                # print(naive_result.stdout)
                # print("mcs 출력:")
                # print(mcs_result.stdout)
                
                # 출력 비교
                if naive_result.stdout != mcs_result.stdout:
                    print(f"테스트케이스 {i}: 출력 불일치")
                    print("naive 출력:")
                    print(naive_result.stdout)
                    print("mcs 출력:")
                    print(mcs_result.stdout)
                    sys.exit(1)
        
        print(f"모든 테스트케이스({test_count}개) 통과")
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
