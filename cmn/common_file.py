import os # for mkdir
import imghdr # for file type check for png or else

# common & configuration
from cfg.config_path import IMG_COMMON_DIR


def check_dir(path=IMG_COMMON_DIR):
    if not os.path.exists(path):
        os.makedirs(path)


def check_file(file_full_path):
    file_exists = os.path.isfile(file_full_path)
    if file_exists == True:
        return "Y"
    elif file_exists == False:
        return "N"


def check_image(file_full_path):
    file_type = imghdr.what(file_full_path)
    # timeout retry용
    if file_type != "png": # jpg도 png로 뜨지만 내용물이 text가 있을 경우 None으로 뜸
        return "N"
    else :
        return "Y"