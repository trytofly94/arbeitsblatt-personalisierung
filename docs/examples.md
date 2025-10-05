# Examples

This document provides practical examples of using the Worksheet Personalizer in various scenarios.

## Example 1: Elementary School Math Test

### Scenario
A teacher has a PDF math test and wants to personalize it for 25 students in her class.

### Setup
```
classroom/
├── math_test.pdf
└── student_photos/
    ├── alice_johnson.jpg
    ├── bob_smith.jpg
    ├── charlie_brown.jpg
    └── ... (22 more photos)
```

### Command
```bash
worksheet-personalizer \
  --worksheet math_test.pdf \
  --students-folder student_photos \
  --output-folder personalized_tests
```

### Result
```
personalized_tests/
├── math_test_alice_johnson.pdf
├── math_test_bob_smith.pdf
├── math_test_charlie_brown.pdf
└── ... (22 more files)
```

### Output
```
Worksheet Personalizer
==================================================
Worksheet: math_test.pdf
Students: student_photos
Output: personalized_tests
Add Names: False
==================================================

Processing students...

✓ Success!
Created 25 personalized worksheet(s) in personalized_tests

Created files:
  • math_test_alice_johnson.pdf
  • math_test_bob_smith.pdf
  • math_test_charlie_brown.pdf
  ...
```

---

## Example 2: Kindergarten Activity Sheet with Names

### Scenario
A kindergarten teacher wants to add both photos and names to help young students identify their worksheets.

### Setup
```
kindergarten/
├── coloring_sheet.png
└── kids/
    ├── emma.jpg
    ├── liam.jpg
    └── noah.jpg
```

### Command
```bash
worksheet-personalizer \
  --worksheet coloring_sheet.png \
  --students-folder kids \
  --output-folder personalized_coloring \
  --add-name
```

### Key Feature
The `--add-name` flag adds the student's name next to their photo.

---

## Example 3: High School Exam

### Scenario
A high school teacher needs to personalize exams for 3 different classes. Each class is processed separately.

### Setup
```
exams/
├── biology_exam.pdf
├── class_10a/
│   ├── student01.jpg
│   └── student02.jpg
├── class_10b/
│   ├── student03.jpg
│   └── student04.jpg
└── class_10c/
    ├── student05.jpg
    └── student06.jpg
```

### Commands
```bash
# Process Class 10A
worksheet-personalizer \
  -w biology_exam.pdf \
  -s class_10a \
  -o exams_10a

# Process Class 10B
worksheet-personalizer \
  -w biology_exam.pdf \
  -s class_10b \
  -o exams_10b

# Process Class 10C
worksheet-personalizer \
  -w biology_exam.pdf \
  -s class_10c \
  -o exams_10c
```

---

## Example 4: Mixed Photo Formats

### Scenario
A teacher has student photos in different formats (JPG and PNG).

### Setup
```
mixed_formats/
├── worksheet.pdf
└── photos/
    ├── student1.jpg
    ├── student2.jpeg
    ├── student3.png
    └── student4.PNG
```

### Command
```bash
worksheet-personalizer \
  -w worksheet.pdf \
  -s photos \
  -o output
```

### Notes
- The tool automatically handles `.jpg`, `.jpeg`, and `.png` formats
- File extensions are case-insensitive (`.PNG` and `.png` both work)

---

## Example 5: Debugging Issues

### Scenario
Some worksheets aren't being created and you need to see what's going wrong.

### Command with Verbose Mode
```bash
worksheet-personalizer \
  --worksheet test.pdf \
  --students-folder ./students \
  --output-folder ./output \
  --verbose
```

### Sample Verbose Output
```
[INFO] 2025-10-05 14:30:15 - worksheet_personalizer.core.personalizer - Initialized WorksheetPersonalizer: format=pdf, add_name=False
[INFO] 2025-10-05 14:30:15 - worksheet_personalizer.utils.file_handler - Discovered 3 student(s) in ./students
[DEBUG] 2025-10-05 14:30:15 - worksheet_personalizer.utils.file_handler - Discovered student: anna schmidt (anna_schmidt.jpg)
[DEBUG] 2025-10-05 14:30:15 - worksheet_personalizer.utils.file_handler - Discovered student: max mustermann (max_mustermann.jpg)
[INFO] 2025-10-05 14:30:15 - worksheet_personalizer.core.pdf_processor - Initialized PDF processor for: test.pdf
[INFO] 2025-10-05 14:30:16 - worksheet_personalizer.core.personalizer - Processing 1/3: anna schmidt
[DEBUG] 2025-10-05 14:30:16 - worksheet_personalizer.core.pdf_processor - PDF page dimensions: 612.0x792.0 points
...
```

---

## Example 6: Batch Processing Multiple Worksheets

### Scenario
You have multiple worksheets to personalize for the same group of students.

### Setup
```
batch_process/
├── worksheet1.pdf
├── worksheet2.pdf
├── worksheet3.pdf
└── students/
    ├── alice.jpg
    ├── bob.jpg
    └── charlie.jpg
```

### Bash Script
```bash
#!/bin/bash

# List of worksheets
WORKSHEETS=("worksheet1.pdf" "worksheet2.pdf" "worksheet3.pdf")

# Process each worksheet
for worksheet in "${WORKSHEETS[@]}"; do
    echo "Processing $worksheet..."

    # Create output folder based on worksheet name
    output_name="${worksheet%.pdf}_personalized"

    worksheet-personalizer \
      --worksheet "$worksheet" \
      --students-folder students \
      --output-folder "$output_name"
done

echo "All worksheets processed!"
```

### Results
```
worksheet1.pdf_personalized/
├── worksheet1_alice.pdf
├── worksheet1_bob.pdf
└── worksheet1_charlie.pdf

worksheet2.pdf_personalized/
├── worksheet2_alice.pdf
├── worksheet2_bob.pdf
└── worksheet2_charlie.pdf

worksheet3.pdf_personalized/
├── worksheet3_alice.pdf
├── worksheet3_bob.pdf
└── worksheet3_charlie.pdf
```

---

## Example 7: Using Environment Variables

### Scenario
You want to set default configurations without typing them every time.

### Setup Environment
```bash
# Set defaults
export WORKSHEET_OUTPUT_DIR=./personalized
export WORKSHEET_PHOTO_SIZE=2.0  # 2 cm photos
export WORKSHEET_LOG_LEVEL=DEBUG
```

### Command
```bash
# These settings will use the environment variables
worksheet-personalizer \
  --worksheet test.pdf \
  --students-folder ./students \
  --output-folder $WORKSHEET_OUTPUT_DIR
```

---

## Example 8: Python Library Usage

### Scenario
You want to integrate worksheet personalization into a larger Python application.

### Python Script
```python
from pathlib import Path
from worksheet_personalizer import WorksheetPersonalizer

def personalize_worksheets(worksheet_dir: Path, students_dir: Path, output_dir: Path):
    """Personalize all worksheets in a directory."""

    # Find all PDF and image worksheets
    worksheets = list(worksheet_dir.glob("*.pdf")) + \
                 list(worksheet_dir.glob("*.png")) + \
                 list(worksheet_dir.glob("*.jpg"))

    print(f"Found {len(worksheets)} worksheet(s)")

    for worksheet in worksheets:
        print(f"\nProcessing: {worksheet.name}")

        # Create output folder for this worksheet
        output_folder = output_dir / worksheet.stem

        try:
            # Create personalizer
            personalizer = WorksheetPersonalizer(
                worksheet_path=worksheet,
                students_folder=students_dir,
                output_folder=output_folder,
                add_name=True
            )

            # Process all students
            created_files = personalizer.process_all()

            print(f"  ✓ Created {len(created_files)} personalized worksheets")

        except Exception as e:
            print(f"  ✗ Error: {e}")

# Run the function
if __name__ == "__main__":
    personalize_worksheets(
        worksheet_dir=Path("./worksheets"),
        students_dir=Path("./students"),
        output_dir=Path("./output")
    )
```

---

## Example 9: Error Handling

### Common Issues and Solutions

#### Issue 1: Some photos not recognized
```
Error: No valid student photos found in ./photos
```

**Solution:**
```bash
# Check what's in the folder
ls -la ./photos

# Ensure photos have correct extensions
# Rename if needed:
mv photo1.JPEG photo1.jpg
mv photo2.heic photo2.jpg  # Convert HEIC first
```

#### Issue 2: Output folder permission denied
```
Error: Cannot create output directory ./output: Permission denied
```

**Solution:**
```bash
# Use a different output location
worksheet-personalizer \
  -w test.pdf \
  -s ./students \
  -o ~/Documents/personalized_worksheets
```

#### Issue 3: Worksheet file corrupted
```
Error: Error reading PDF dimensions: ...
```

**Solution:**
```bash
# Verify the PDF
pdfinfo worksheet.pdf

# If corrupted, try to repair or re-export
```

---

## Tips and Best Practices

### 1. Photo Quality
- Use clear, well-lit photos of students
- Recommended minimum resolution: 300x400 pixels
- Photos will be scaled to 1.5 cm (long side)

### 2. File Naming
- Use descriptive names: `firstname_lastname.jpg`
- Avoid special characters: use underscores instead of spaces
- Be consistent with naming conventions across your class

### 3. Batch Processing
- Process one worksheet at a time for better error tracking
- Use scripts (Bash/Python) for multiple worksheets
- Keep original worksheets as backups

### 4. Testing
- Test with 2-3 students first before processing entire class
- Review output quality before distributing to students
- Check that photos are positioned correctly

### 5. Organization
```
recommended_structure/
├── original_worksheets/
│   ├── math_test.pdf
│   └── science_quiz.pdf
├── student_photos/
│   └── ... (all student photos)
└── personalized/
    ├── math_test/
    └── science_quiz/
```
