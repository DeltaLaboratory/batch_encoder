import os
import time
import multiprocessing
import argparse

import chardet
from pycaption import SAMIReader, SRTWriter

parser = argparse.ArgumentParser(description="Caption Encoder")

parser.add_argument("original_dir", type=str, help="original dir")
parser.add_argument("result_dir", type=str, help="result dir")

arg = parser.parse_args()

ORIGIN_DIR = arg.original_dir
RES_DIR = arg.result_dir


def get_paths(dir_name: str) -> tuple[os.DirEntry]:
    return tuple(os.scandir(path=dir_name))


def convert(index: int, path: list):
    print(f"Processing : {path[1]} ({index + 1})", flush=True)
    res = 0
    if path[2]:
        print("pass : it is dir", flush=True)
        print("======================", flush=True)
        return res
    with open(path[0], "rb") as file:
        encoding = chardet.detect(file.read())
    print(f"detected encoding : {encoding['encoding']}, confidence : {encoding['confidence']}", flush=True)
    try:
        with open(path[0], "rt", encoding=encoding["encoding"]) as file:
            caption = file.read()
    except UnicodeDecodeError:
        print("Critical Error : Cannot Detect Encoding: Pass", flush=True)
        return 3
    if path[0].endswith("smi"):
        try:
            caption = SRTWriter().write(SAMIReader().read(caption))
            path[1] += ".srt"
        except Exception as e:
            print(f"[Error] {e} was occurred on convert : pass", flush=True)
            res = 1
    print("saving...", flush=True)
    with open(f"./{RES_DIR}/{path[1]}", "wt", encoding="utf-8") as file:
        file.write(caption)
    print("complete!", flush=True)
    print("======================", flush=True)
    return res


def main():
    start_time = time.perf_counter()
    errors = 0
    critical_error = 0
    caption_path = get_paths(ORIGIN_DIR)
    args_list = enumerate([[i.path, i.name, i.is_dir()] for i in caption_path])
    with multiprocessing.Pool() as pool:
        result = pool.starmap(convert, args_list)
    for score in result:
        if score == 1:
            errors += 1
        elif score == 3:
            critical_error += 1
    print(f"Total {len(caption_path)}, warn {errors} times, error {critical_error} times.")
    print(f"Total took {time.perf_counter() - start_time}s")


if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()
