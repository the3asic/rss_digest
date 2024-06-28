import os
import shutil
import zipfile
from datetime import datetime

def zip_files_and_folders(zip_filename, items_to_zip):
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for item in items_to_zip:
            if os.path.isdir(item):
                for root, _, files in os.walk(item):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, start=os.path.dirname(item))
                        zipf.write(file_path, arcname)
            elif os.path.isfile(item):
                zipf.write(item, os.path.basename(item))

def remove_items(items_to_remove):
    for item in items_to_remove:
        if os.path.isdir(item):
            shutil.rmtree(item)
        elif os.path.isfile(item):
            os.remove(item)

def update_gitignore():
    gitignore_content = "\n# Archive folder\narchives/"
    with open('.gitignore', 'a+') as gitignore_file:
        gitignore_file.seek(0)
        existing_content = gitignore_file.read()
        if "archives/" not in existing_content:
            gitignore_file.write(gitignore_content)

def copy_to_output_folder(output_folder, items_to_copy):
    os.makedirs(output_folder, exist_ok=True)
    for item in items_to_copy:
        if os.path.isdir(item):
            shutil.copytree(item, os.path.join(output_folder, os.path.basename(item)))
        elif os.path.isfile(item):
            shutil.copy2(item, output_folder)

def main():
    # List of items to zip and remove
    items = [
        "article_summaries",
        "articles_text",
        "high_rated_articles",
        "thumbnails",
        "article_ratings.json",
        "article_summaries.json",
        "articles.csv",
        "newsletter.html",
        "titles_and_links.txt",
        "newsletter.png"  # Added newsletter.png to the list
    ]

    # Create archives directory
    archives_dir = "archives"
    os.makedirs(archives_dir, exist_ok=True)

    # Create zip filename with current date and time
    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_filename = os.path.join(archives_dir, f"archive_{current_time}.zip")

    # Create output folder with current date and time
    output_folder = os.path.join("output", current_time)
    items_to_copy = ["newsletter.html", "thumbnails", "titles_and_links.txt", "newsletter.png"]
    copy_to_output_folder(output_folder, items_to_copy)

    # Zip files and folders
    print(f"Creating zip file: {zip_filename}")
    zip_files_and_folders(zip_filename, items)

    # Remove original files and folders
    print("Removing original files and folders")
    remove_items(items)

    # Update .gitignore
    update_gitignore()

    print(f"Cleanup complete. Archive created: {zip_filename}")

if __name__ == "__main__":
    main()