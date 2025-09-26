import os
import shutil
import logging
from datetime import datetime
import markdown_split as ms

PROJECT_ROOT = "/".join(os.path.dirname(__file__).split("/")[0:-1])
STATIC_PATH = os.path.join(PROJECT_ROOT, "static")
PUBLIC_PATH = os.path.join(PROJECT_ROOT, "public")
LOG_DIR = os.path.join(PROJECT_ROOT, "log")

# Create log directory if it doesn't exist
os.makedirs(LOG_DIR, exist_ok=True)

# Create timestamp for log filename
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
log_filename = f"file_operations_{timestamp}.log"
log_filepath = os.path.join(LOG_DIR, log_filename)

# Configure logging to write to file
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_filepath),
        logging.StreamHandler()  # Also log to console
    ]
)

logger = logging.getLogger(__name__)


def main():
    if os.path.exists(PUBLIC_PATH):
        shutil.rmtree(PUBLIC_PATH)
    os.makedirs(PUBLIC_PATH, exist_ok=True)
    logger.info(f"Ensured public directory exists: {PUBLIC_PATH}")

    copy_all_files_recursive(STATIC_PATH, PUBLIC_PATH)
    generate_page("content/index.md", "template.html", "public/index.html")


def copy_all_files_recursive(source_dir, dest_dir):

    """Helper function for recursive copying with proper destination paths"""
    for item in os.listdir(source_dir):
        source_path = os.path.join(source_dir, item)
        dest_path = os.path.join(dest_dir, item)

        if os.path.isfile(source_path):
            try:
                shutil.copy2(source_path, dest_path)
                logger.info(f"Copied file: {source_path} -> {dest_path}")
            except Exception as e:
                logger.error(f"Failed to copy file {source_path}: {str(e)}")

        elif os.path.isdir(source_path):
            try:
                if not os.path.exists(dest_path):
                    os.makedirs(dest_path)
                    logger.info(f"Created directory: {dest_path}")
                copy_all_files_recursive(source_path, dest_path)
            except Exception as e:
                logger.error(f"Failed to process directory {source_path}: {str(e)}")


def read_file_contents(filename):
    with open(filename, "r") as f:
        return f.read()


def generate_page(from_path, template_path, dest_path):
    logger.info(f"Generating page from {from_path} to {dest_path} using {template_path}")
    markdown = read_file_contents(from_path)
    template = read_file_contents(template_path)
    html_string = ms.markdown_to_html_node(markdown).to_html()
    title = ms.extract_title(markdown)
    template = template.replace("{{ Title }}", title).replace("{{ Content }}", html_string)
    pathdir = os.path.dirname(dest_path)
    print(pathdir)
    os.makedirs(pathdir, exist_ok=True)
    with open(dest_path, "w") as f:
        f.write(template)

if __name__ == "__main__":
    logger.info("=== Starting File Copy Operation ===")
    main()
    logger.info("=== File Copy Operation Completed ===")
    print(f"Log file created: {log_filepath}")