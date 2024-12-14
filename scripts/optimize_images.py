import subprocess
import tempfile
import os
import glob
import shutil


def convert(src, dest):
    if dest.endswith("webm"):
        subprocess.run(["ffmpeg", "-y", "-i", src, dest])
    else:
        subprocess.run(["magick", src, dest])
    return dest


def resize(src, dest, width):
    if src.endswith("webm"):
        shutil.copy(src, dest)
    else:
        subprocess.run(["magick", src, "-resize", str(width), dest])


trial_exts = {
    ".png": [".webp"],
    ".jpg": [".webp", ".avif"],
    ".jpeg": [".webp", ".avif"],
    ".gif": [".webm"],
}


def convert_to_smallest(src, dest, tmpdir):
    basename = os.path.basename(src)
    root, ext = os.path.splitext(basename)

    if any(
        os.path.isfile(dest + root + target_ext)
        for target_ext in trial_exts[ext.lower()]
    ):
        print(f"target for {src} already exists, skipping...")
        return
    trial_files = [
        convert(src, tmpdir + root + target_ext)
        for target_ext in trial_exts[ext.lower()]
    ]
    trial_files += [src]

    trial_sizes = [os.path.getsize(file) for file in trial_files]

    best_file = min(zip(trial_files, trial_sizes), key=lambda p: p[1])[0]

    shutil.move(best_file, dest)

    print(f"{src} -> {os.path.basename(best_file)}")


def optimize_directory(src, dest_prefix):
    with tempfile.TemporaryDirectory() as tmp:
        for file in glob.iglob(src + "/**/*.*", recursive=True):
            os.makedirs(dest_prefix + os.path.dirname(file), exist_ok=True)
            convert_to_smallest(
                file, dest_prefix + os.path.dirname(file) + "/", tmp + "/"
            )


def resize_directory(src, dest):
    for file in glob.iglob(src + "/**/*.*", recursive=True):
        os.makedirs(os.path.dirname(dest + file.removeprefix(src)), exist_ok=True)
        resize(file, dest + file.removeprefix(src), 700)


optimize_directory("images", "static/")
resize_directory("static/images", "static/thumbnails/")
