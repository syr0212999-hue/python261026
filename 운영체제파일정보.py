from pathlib import Path
import shutil


download_folder = Path(r"C:\Users\student\Downloads")
categories = {
    ".jpg": "images",
    ".jpeg": "images",
    ".csv": "data",
    ".xlsx": "data",
    ".txt": "docs",
    ".doc": "docs",
    ".pdf": "docs",
    ".zip": "archive",
    ".exe": "archive",
}


def available_destination(destination: Path) -> Path:
    """Return a path that does not overwrite an existing file."""
    if not destination.exists():
        return destination

    stem, suffix = destination.stem, destination.suffix
    number = 1
    while True:
        candidate = destination.with_name(f"{stem}_{number}{suffix}")
        if not candidate.exists():
            return candidate
        number += 1


def sort_downloads() -> None:
    for folder_name in set(categories.values()):
        (download_folder / folder_name).mkdir(parents=True, exist_ok=True)

    for file_path in download_folder.iterdir():
        if not file_path.is_file():
            continue

        folder_name = categories.get(file_path.suffix.lower())
        if folder_name is None:
            continue

        destination = available_destination(
            download_folder / folder_name / file_path.name
        )
        shutil.move(str(file_path), str(destination))
        print(f"이동 완료: {file_path.name} -> {destination.parent.name}")


if __name__ == "__main__":
    sort_downloads()
