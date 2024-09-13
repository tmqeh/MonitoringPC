import inspect

def get_cur_func_nm():
    func_nm = None

    if len(inspect.stack()) > 2:
        # 호출한 함수명 확인하기
        func_nm = inspect.stack()[1].function

    else: # 2보다 작으면 파일명 추출 (오기재로 인한 오류 회피)
        # 호출한 파일명 확인하기
        func_nm = inspect.stack()[1].filename
    
    return func_nm


def get_cur_file_nm():
    file_nm = None
    
    if len(inspect.stack()) >= 2:
        # 호출한 파일명 확인하기
        file_nm = inspect.stack()[1].filename.replace(".py","").split("\\")[-1]
    
    else:
        # 확인 불가
        file_nm = "Unknown"
    
    return file_nm


def get_parent_func_nm():
    func_nm = None

    if len(inspect.stack()) > 3:
        # 호출한 함수명 확인하기
        func_nm = inspect.stack()[2].function

    else: # 3보다 작으면 파일명 추출 (오기재로 인한 오류 회피)
        # 호출한 파일명 확인하기
        func_nm = inspect.stack()[1].filename # "There is no parent function"
    
    return func_nm


def get_func_tree():
    # func_nm = ""
    # for i, row in enumerate(reversed(inspect.stack()[1:])): # 자기자신 제외
    #     if row.function == "<module>":
    #         func_nm = func_nm + row.filename.replace(".py","").split("\\")[-1]
    #     else:
    #         func_nm = func_nm + " -> " + row.function
    func_nm = " -> ".join([frame.function if frame.function != "<module>" \
                                          else frame.filename.replace(".py","").split("\\")[-1] \
                                          for frame in reversed(inspect.stack()[1:])])  # 자기자신 제외
    
    return func_nm