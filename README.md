이 앱은 주로 맥(Mac) 환경에서 발생하는 **한글 파일명 자소 분리 현상(자음과 모음이 분리되는 현상)**을 해결해 주는 macOS용 유틸리티 애플리케이션입니다.

코드(ViewController.swift 및 ScriptGenerator.swift)를 분석해 본 결과, 이 앱의 주요 기능과 동작 방식은 다음과 같습니다.

주요 기능
파일명 인코딩 변환 (NFD -> NFC)

맥OS는 파일명을 저장할 때 한글 자소(자음과 모음)를 분리하는 NFD(정준 분해) 방식을 사용합니다. 이로 인해 맥에서 만든 파일을 윈도우 등 다른 운영체제로 복사하면 파일명이 ㅇㅣㄹㅡㅁ처럼 풀려서 보이는 현상이 발생합니다.
이 앱은 precomposedStringWithCanonicalMapping 속성을 사용하여 분리된 글자를 원래의 합쳐진 형태인 NFC(정준 결합) 방식으로 변환합니다.
드래그 앤 드롭 지원

변환이 필요한 파일이나 폴더를 앱 창에 그대로 드래그 앤 드롭하여 쉽게 처리할 수 있습니다.
폴더 내 파일 일괄 변환

폴더를 입력하면 내부를 탐색하여 하위 폴더 및 파일들의 이름까지 모두 일괄적으로 변환해 줍니다. (단, 패키지가 손상되는 것을 막기 위해 .app 확장자를 가진 앱 파일 내부로는 들어가지 않습니다.)
동작 원리
파일이나 폴더가 입력되면 앱은 즉시 파일명을 변경하지 않고, 다음과 같은 과정을 거칩니다.

각 파일의 원래 이름과 합쳐진 새 이름을 매칭하여 mv (이름 변경) 명령어를 담은 임시 쉘 스크립트(.sh) 파일을 생성합니다.
생성된 쉘 스크립트에 실행 권한을 부여하고 실행하여 파일명 변경을 일괄 처리합니다.
작업이 완료되면 임시 스크립트 파일을 삭제하고 "Done!" 메시지를 띄워줍니다.
간단히 말해, 윈도우나 리눅스 사용자에게 파일을 공유하기 전에 파일명이 깨지지 않도록 한글 이름을 정상적으로 합쳐주는 앱입니다. 앱 내에 도움말 링크(namocom.tistory.com/907)가 연결되어 있는 것을 보면 해당 블로그 작성자분이 제작하신 툴로 보입니다.


** 파이썬으로 동일하게 동작하는 어플 **
```
import os
import unicodedata
import tkinter as tk
from tkinter import filedialog, messagebox

def normalize_string(text: str) -> str:
    # 맥(Mac) 방식의 자소 분리(NFD)를 윈도우/리눅스 방식의 결합(NFC)으로 변환
    return unicodedata.normalize('NFC', text)

def process_path(path: str):
    if not os.path.exists(path):
        return

    # 폴더인 경우 하위 파일 및 폴더 탐색 (아래에서 위로 탐색해야 상위 폴더 이름이 나중에 바뀜)
    if os.path.isdir(path):
        for root, dirs, files in os.walk(path, topdown=False):
            # 1. 파일 이름 변경
            for file_name in files:
                if file_name == '.DS_Store':
                    continue
                new_name = normalize_string(file_name)
                if new_name != file_name:
                    old_file_path = os.path.join(root, file_name)
                    new_file_path = os.path.join(root, new_name)
                    os.rename(old_file_path, new_file_path)
            
            # 2. 폴더 이름 변경
            for dir_name in dirs:
                if dir_name.endswith('.app'):
                    continue # 앱 패키지 내부 변경 방지
                new_name = normalize_string(dir_name)
                if new_name != dir_name:
                    old_dir_path = os.path.join(root, dir_name)
                    new_dir_path = os.path.join(root, new_name)
                    os.rename(old_dir_path, new_dir_path)
                    
        # 3. 최상위(선택한) 폴더 자체의 이름도 변경
        root_dir_name = os.path.basename(path)
        new_root_dir_name = normalize_string(root_dir_name)
        if new_root_dir_name != root_dir_name:
            new_path = os.path.join(os.path.dirname(path), new_root_dir_name)
            os.rename(path, new_path)
            
    # 파일인 경우
    elif os.path.isfile(path):
        file_name = os.path.basename(path)
        new_name = normalize_string(file_name)
        if new_name != file_name:
            new_path = os.path.join(os.path.dirname(path), new_name)
            os.rename(path, new_path)

def select_and_process():
    # 파일 여러 개 선택
    paths = filedialog.askopenfilenames(title="파일 선택")
    if paths:
        for path in paths:
            process_path(path)
        messagebox.showinfo("완료", "파일 이름 변환이 완료되었습니다.")
        
def select_dir_and_process():
    # 폴더 선택 (하위 파일 일괄 처리)
    path = filedialog.askdirectory(title="폴더 선택")
    if path:
        process_path(path)
        messagebox.showinfo("완료", "폴더 내 파일/폴더 이름 변환이 완료되었습니다.")

def main():
    # GUI 설정
    root = tk.Tk()
    root.title("Mac 한글 자소 분리 해결기")
    root.geometry("300x150")
    
    label = tk.Label(root, text="NFD -> NFC 변환기\n변환할 항목을 선택하세요.", pady=10)
    label.pack()
    
    btn_file = tk.Button(root, text="파일 선택", command=select_and_process, width=20)
    btn_file.pack(pady=5)
    
    btn_dir = tk.Button(root, text="폴더 선택", command=select_dir_and_process, width=20)
    btn_dir.pack(pady=5)
    
    # 윈도우 창 표시
    root.mainloop()

if __name__ == "__main__":
    main()

```
