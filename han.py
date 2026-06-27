#!/usr/local/bin/python3
import os
import sys
import unicodedata
import tkinter as tk
from tkinter import filedialog, messagebox

def normalize_string(text: str) -> str:
    # 맥(Mac) 방식의 자소 분리(NFD)를 윈도우/리눅스 방식의 결합(NFC)으로 변환
    return unicodedata.normalize('NFC', text)

def has_hangul(text: str) -> bool:
    # 한글 자모 및 음절 범위 확인
    for char in text:
        cp = ord(char)
        if (0xAC00 <= cp <= 0xD7A3) or (0x1100 <= cp <= 0x11FF) or (0x3130 <= cp <= 0x318F):
            return True
    return False

def process_path(path: str, recursive: bool = True):
    if not os.path.exists(path):
        return

    # 폴더인 경우
    if os.path.isdir(path):
        if recursive:
            # 하위 모든 파일 및 폴더 탐색 (아래에서 위로 탐색해야 하위 경로가 변경되지 않음)
            for root, dirs, files in os.walk(path, topdown=False):
                # 1. 파일 이름 변경
                for file_name in files:
                    if file_name == '.DS_Store':
                        continue
                    new_name = normalize_string(file_name)
                    if new_name != file_name and has_hangul(file_name):
                        old_file_path = os.path.join(root, file_name)
                        new_file_path = os.path.join(root, new_name)
                        print(f"파일 이름 변경: {old_file_path} -> {new_file_path}")
                        try:
                            os.rename(old_file_path, new_file_path)
                        except Exception as e:
                            print(f"실패: {old_file_path} -> {e}")

                # 2. 하위 폴더 이름 변경
                for dir_name in dirs:
                    if dir_name.endswith('.app'):
                        continue # 앱 패키지 내부 변경 방지
                    new_name = normalize_string(dir_name)
                    if new_name != dir_name and has_hangul(dir_name):
                        old_dir_path = os.path.join(root, dir_name)
                        new_dir_path = os.path.join(root, new_name)
                        print(f"폴더 이름 변경: {old_dir_path} -> {new_dir_path}")
                        try:
                            os.rename(old_dir_path, new_dir_path)
                        except Exception as e:
                            print(f"실패: {old_dir_path} -> {e}")

            # 3. 최상위(선택한) 폴더 자체의 이름도 변경
            root_dir_name = os.path.basename(path)
            new_root_dir_name = normalize_string(root_dir_name)
            if new_root_dir_name != root_dir_name and has_hangul(root_dir_name):
                new_path = os.path.join(os.path.dirname(path), new_root_dir_name)
                print(f"최상위 폴더 이름 변경: {path} -> {new_path}")
                try:
                    os.rename(path, new_path)
                except Exception as e:
                    print(f"실패: {path} -> {e}")
        else:
            # 하위 제외: 직속 파일 및 폴더 탐색
            for file_name in os.listdir(path):
                if file_name == '.DS_Store':
                    continue
                file_path = os.path.join(path, file_name)
                new_name = normalize_string(file_name)
                if new_name != file_name and has_hangul(file_name):
                    new_file_path = os.path.join(path, new_name)
                    print(f"이름 변경: {file_path} -> {new_file_path}")
                    try:
                        os.rename(file_path, new_file_path)
                    except Exception as e:
                        print(f"실패: {file_path} -> {e}")

    # 파일인 경우
    elif os.path.isfile(path):
        file_name = os.path.basename(path)
        new_name = normalize_string(file_name)
        if new_name != file_name and has_hangul(file_name):
            new_path = os.path.join(os.path.dirname(path), new_name)
            print(f"파일 이름 변경: {path} -> {new_path}")
            try:
                os.rename(path, new_path)
            except Exception as e:
                print(f"실패: {path} -> {e}")

def select_and_process(parent):
    # 파일 여러 개 선택
    paths = filedialog.askopenfilenames(title="파일 선택", parent=parent)
    if paths:
        for path in paths:
            process_path(path)
        messagebox.showinfo("완료", "파일 이름 변환이 완료되었습니다.", parent=parent)

def select_dir_and_process(parent):
    # 폴더 선택 (하위 파일 일괄 처리)
    path = filedialog.askdirectory(title="폴더 선택 (하위 포함)", parent=parent)
    if path:
        process_path(path, recursive=True)
        messagebox.showinfo("완료", "폴더 및 하위 모든 파일 이름 변환이 완료되었습니다.", parent=parent)

def select_single_dir_and_process(parent):
    # 폴더 선택 (하위 제외, 직속 파일만 처리)
    path = filedialog.askdirectory(title="폴더 선택 (하위 제외)", parent=parent)
    if path:
        process_path(path, recursive=False)
        messagebox.showinfo("완료", "선택한 폴더 내 파일 이름 변환이 완료되었습니다.", parent=parent)

def create_grid_button(parent, text, command, bg, hover_bg, fg="#ffffff"):
    # macOS system Tk 백그라운드 렌더링 버그 및 크기 붕괴 버그 우회를 위해 Frame + Label 조합 사용
    frame = tk.Frame(parent, bg=bg, cursor="hand2")

    lbl = tk.Label(
        frame,
        text=text,
        font=("Helvetica Neue", 12, "bold"),
        bg=bg,
        fg=fg,
        justify="center"
    )
    lbl.pack(expand=True, fill="both")

    # 호버 효과 정의
    def on_enter(e):
        frame.configure(bg=hover_bg)
        lbl.configure(bg=hover_bg)

    def on_leave(e):
        frame.configure(bg=bg)
        lbl.configure(bg=bg)

    def on_click(e):
        command()

    # 프레임과 라벨 모두에 호버/클릭 이벤트 바인딩
    frame.bind("<Enter>", on_enter)
    frame.bind("<Leave>", on_leave)
    frame.bind("<Button-1>", on_click)

    lbl.bind("<Enter>", on_enter)
    lbl.bind("<Leave>", on_leave)
    lbl.bind("<Button-1>", on_click)

    return frame

def main():
    # GUI 설정
    root = tk.Tk()
    root.title("Mac 한글 자소 분리 해결기")

    # 최상위 창 설정 및 포커스
    root.attributes("-topmost", True)
    root.lift()
    root.focus_force()

    # Grid 배경색
    root.configure(bg="#121212")

    # ESC 키 누르면 종료
    root.bind('<Escape>', lambda event: root.destroy())

    # 화면 중앙에 배치
    window_width = 300
    window_height = 240
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 2
    root.geometry(f"{window_width}x{window_height}+{x}+{y}")

    # 2x2 그리드 열/행 비율 고정 (정확한 4분할)
    root.grid_rowconfigure(0, weight=1)
    root.grid_rowconfigure(1, weight=1)
    root.grid_columnconfigure(0, weight=1)
    root.grid_columnconfigure(1, weight=1)

    # 4분할 버튼 생성 (색상 테마: 파일선택-하늘색, 닫기-빨간색, 폴더한개-초록색, 폴더전체-보라색)
    btn_file = create_grid_button(
        root,
        "📄\n\n파일선택",
        lambda: select_and_process(root),
        "#4a90e2",
        "#357abd"
    )
    btn_file.grid(row=0, column=0, sticky="nsew", padx=1, pady=1)

    btn_close = create_grid_button(
        root,
        "❌\n\n닫기\n(ESC)",
        lambda: root.destroy(),
        "#f55a5a",
        "#e04545"
    )
    btn_close.grid(row=0, column=1, sticky="nsew", padx=1, pady=1)

    btn_single_dir = create_grid_button(
        root,
        "📁\n\n폴더한개\n(하위 제외)",
        lambda: select_single_dir_and_process(root),
        "#47c189",
        "#36a371"
    )
    btn_single_dir.grid(row=1, column=0, sticky="nsew", padx=1, pady=1)

    btn_dir = create_grid_button(
        root,
        "📂\n\n폴더전체\n(하위 포함)",
        lambda: select_dir_and_process(root),
        "#9b5de5",
        "#833ab4"
    )
    btn_dir.grid(row=1, column=1, sticky="nsew", padx=1, pady=1)

    # macOS Tk 강제 리프레시 및 강제 포커스 (흰 화면 방지)
    root.update_idletasks()
    root.update()

    # 윈도우 창 표시
    root.mainloop()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # CLI Mode
        for path in sys.argv[1:]:
            if os.path.exists(path):
                print(f"변환 시작: {path}")
                process_path(path)
                print(f"변환 완료: {path}")
            else:
                print(f"존재하지 않는 경로입니다: {path}")
    else:
        # GUI Mode
        main()
      
