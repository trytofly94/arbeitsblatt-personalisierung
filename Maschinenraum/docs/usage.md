# Usage Guide

This guide provides detailed instructions on how to use the Worksheet Personalizer CLI tool.

## Table of Contents

- [Installation](#installation)
- [Basic Usage](#basic-usage)
- [Command-Line Options](#command-line-options)
- [Input Requirements](#input-requirements)
- [Examples](#examples)
- [Troubleshooting](#troubleshooting)

## Installation

### From Source (Development)

```bash
# Clone the repository
git clone https://github.com/yourusername/arbeitsblatt-personalisierung.git
cd arbeitsblatt-personalisierung

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"
```

### Using pip (After Publishing)

```bash
pip install worksheet-personalizer
```

## Basic Usage

The basic command structure is:

```bash
worksheet-personalizer --worksheet <WORKSHEET_FILE> --students-folder <STUDENTS_FOLDER> --output-folder <OUTPUT_FOLDER>
```

Or using the short options:

```bash
worksheet-personalizer -w <WORKSHEET_FILE> -s <STUDENTS_FOLDER> -o <OUTPUT_FOLDER>
```

## Command-Line Options

### Required Options

- `--worksheet, -w PATH`
  Path to the worksheet file (PDF or image format: PNG, JPG, JPEG)

- `--students-folder, -s PATH`
  Path to the folder containing student photos

- `--output-folder, -o PATH`
  Path to the folder where personalized worksheets will be saved

### Optional Flags

- `--add-name, -n`
  Add the student's name next to their photo on the worksheet

- `--verbose, -v`
  Enable verbose logging for debugging purposes

### Getting Help

```bash
worksheet-personalizer --help
```

## Input Requirements

### Worksheet File

The worksheet can be in one of the following formats:

- **PDF**: `.pdf`
- **Images**: `.png`, `.jpg`, `.jpeg`

The worksheet should be a standard-sized document (e.g., A4, Letter). The student photo will be placed in the top-right corner.

### Student Photos

Student photos must:

- Be in a supported format: `.jpg`, `.jpeg`, or `.png`
- Have the student's name as the filename (without extension)
- Be placed in a single folder

**Filename Convention:**

The student's name is extracted from the photo filename:
- Underscores (`_`) are converted to spaces
- The file extension is removed

Examples:
- `max_mustermann.jpg` → "max mustermann"
- `anna_schmidt.png` → "anna schmidt"
- `tom_mueller.jpeg` → "tom mueller"

### Output Folder

The output folder:
- Will be created automatically if it doesn't exist
- Will contain personalized worksheets with filenames in the format:
  `<original_worksheet_name>_<student_name>.<extension>`

Example:
- Original: `math_test.pdf`
- Student: `max mustermann`
- Output: `math_test_max_mustermann.pdf`

## Examples

### Example 1: PDF Worksheet Without Names

Personalize a PDF worksheet for multiple students without adding their names:

```bash
worksheet-personalizer \
  --worksheet math_test.pdf \
  --students-folder ./class_photos \
  --output-folder ./personalized_tests
```

### Example 2: Image Worksheet With Names

Personalize an image worksheet and include student names:

```bash
worksheet-personalizer \
  --worksheet worksheet.png \
  --students-folder ./students \
  --output-folder ./output \
  --add-name
```

### Example 3: Using Short Options

Use short option flags for a more concise command:

```bash
worksheet-personalizer -w test.pdf -s ./photos -o ./results -n
```

### Example 4: Verbose Mode for Debugging

Enable verbose logging to see detailed processing information:

```bash
worksheet-personalizer \
  --worksheet worksheet.pdf \
  --students-folder ./students \
  --output-folder ./output \
  --verbose
```

### Example 5: Complete Workflow

Here's a complete example from start to finish:

```bash
# 1. Prepare your directory structure
mkdir my_project
cd my_project

# 2. Place your worksheet
# (Copy your math_test.pdf to this folder)

# 3. Create a folder for student photos
mkdir student_photos
# (Copy student photos: max_mustermann.jpg, anna_schmidt.jpg, etc.)

# 4. Run the personalizer
worksheet-personalizer \
  --worksheet math_test.pdf \
  --students-folder student_photos \
  --output-folder personalized_worksheets \
  --add-name

# 5. Check the results
ls personalized_worksheets/
# Output:
# math_test_anna_schmidt.pdf
# math_test_max_mustermann.pdf
```

## Troubleshooting

### Problem: "No valid student photos found"

**Solution:**
- Ensure student photos are in the correct format (`.jpg`, `.jpeg`, or `.png`)
- Check that the photos are directly in the specified folder (not in subfolders)
- Verify the folder path is correct

### Problem: "Worksheet file not found"

**Solution:**
- Check that the worksheet file path is correct
- Use absolute paths if relative paths aren't working
- Ensure the file has the correct extension (`.pdf`, `.png`, `.jpg`, or `.jpeg`)

### Problem: Output images/PDFs are too small or too large

**Solution:**
The photo size is set to 2.5 cm (long side) for A4 print. The size is calculated based on A4 dimensions regardless of PDF resolution. If you need different sizes, you can:
1. Set environment variable: `export WORKSHEET_PHOTO_SIZE=3.0` (for 3 cm)
2. Edit the configuration file (see Configuration section in README.md)

### Problem: Student names not appearing correctly

**Solution:**
- If using `--add-name`, ensure there's enough space to the left of where the photo will be placed
- The name is extracted from the filename - check your photo filenames
- Use underscores in filenames to represent spaces in names

### Problem: Permission denied when creating output folder

**Solution:**
- Ensure you have write permissions in the parent directory
- Try using a different output folder location
- On Unix systems, check folder permissions with `ls -l`

### Getting More Help

For additional debugging information, run the command with the `--verbose` flag:

```bash
worksheet-personalizer -w worksheet.pdf -s ./students -o ./output --verbose
```

This will show detailed logs including:
- Student discovery process
- Image processing steps
- File creation operations
- Any warnings or errors

## Environment Variables

You can set the following environment variables to customize behavior:

```bash
# Set default output directory
export WORKSHEET_OUTPUT_DIR=./output

# Set photo size (in cm) - default is 2.5 for A4 print
export WORKSHEET_PHOTO_SIZE=2.5

# Set photo margin (in cm)
export WORKSHEET_PHOTO_MARGIN=0.5

# Set log level (DEBUG, INFO, WARNING, ERROR)
export WORKSHEET_LOG_LEVEL=INFO

# Set default for adding names
export WORKSHEET_ADD_NAME_DEFAULT=false
```

## Advanced Usage

### Using as a Python Library

You can also use the worksheet personalizer as a Python library:

```python
from pathlib import Path
from worksheet_personalizer import WorksheetPersonalizer

# Create personalizer
personalizer = WorksheetPersonalizer(
    worksheet_path=Path("worksheet.pdf"),
    students_folder=Path("./students"),
    output_folder=Path("./output"),
    add_name=True
)

# Process all students
created_files = personalizer.process_all()

print(f"Created {len(created_files)} personalized worksheets")
for file_path in created_files:
    print(f"  - {file_path.name}")
```

### Processing a Single Student

```python
from pathlib import Path
from worksheet_personalizer import WorksheetPersonalizer, Student

# Create personalizer
personalizer = WorksheetPersonalizer(
    worksheet_path=Path("worksheet.pdf"),
    students_folder=Path("./students"),
    output_folder=Path("./output")
)

# Create a student manually
student = Student.from_photo_path(Path("./students/max_mustermann.jpg"))

# Process just this student
output_path = personalizer.process_single(student)
print(f"Created: {output_path}")
```
