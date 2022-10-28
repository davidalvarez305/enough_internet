import os

def delete_files(dir_path):

    if not dir:
        raise Exception("Directory not passed.")
    else:
        del_files = os.listdir(dir_path)
        for df in del_files:
            if ".txt" in df or ".mp4" in df or ".png" in df or ".jpg" in df or "conv_" in df:
                os.remove(dir_path + df)