#!/usr/bin/env python3
# debug_paths.py - A script to troubleshoot file paths

import os

def check_paths():
    """Check various paths and file access."""
    current_dir = os.getcwd()
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(current_dir, "output")
    abs_output_dir = os.path.abspath(output_dir)
    
    print("\n===== Path Information =====")
    print(f"Current working directory: {current_dir}")
    print(f"Script directory: {script_dir}")
    print(f"Relative output directory path: {output_dir}")
    print(f"Absolute output directory path: {abs_output_dir}")
    
    # Check if output directory exists
    if os.path.exists(output_dir):
        print(f"\nOutput directory exists: {output_dir}")
        try:
            # List contents of output directory
            contents = os.listdir(output_dir)
            print(f"Contents of output directory ({len(contents)} items):")
            for item in contents:
                item_path = os.path.join(output_dir, item)
                item_size = os.path.getsize(item_path) if os.path.isfile(item_path) else "N/A"
                print(f"  - {item} (size: {item_size} bytes)")
        except Exception as e:
            print(f"Error listing output directory: {str(e)}")
    else:
        print(f"\nOutput directory does not exist: {output_dir}")
        
        # Try to create the directory
        try:
            os.makedirs(output_dir, exist_ok=True)
            print(f"Created output directory: {output_dir}")
        except Exception as e:
            print(f"Error creating output directory: {str(e)}")
    
    # Check write permissions
    print("\n===== Permission Checks =====")
    try:
        # Try to create a test file
        test_file = os.path.join(output_dir, "test_write.txt")
        with open(test_file, "w") as f:
            f.write("Test write permission")
        print(f"Successfully wrote to test file: {test_file}")
        
        # Try to read the test file
        with open(test_file, "r") as f:
            content = f.read()
        print(f"Successfully read from test file: {test_file}")
        
        # Clean up test file
        os.remove(test_file)
        print(f"Successfully deleted test file: {test_file}")
    except Exception as e:
        print(f"Error with file operations: {str(e)}")
    
    # Try to find resume files in the parent directories
    print("\n===== Searching for resume files =====")
    search_dirs = [
        current_dir,
        os.path.dirname(current_dir),
        os.path.join(current_dir, "data"),
        os.path.join(current_dir, "data", "resume"),
        os.path.join(script_dir, "data"),
        os.path.join(script_dir, "data", "resume")
    ]
    
    for search_dir in search_dirs:
        if os.path.exists(search_dir):
            print(f"Checking directory: {search_dir}")
            try:
                for root, dirs, files in os.walk(search_dir):
                    pdf_files = [f for f in files if f.lower().endswith(".pdf")]
                    if pdf_files:
                        print(f"  Found {len(pdf_files)} PDF files in {root}:")
                        for pdf in pdf_files:
                            print(f"    - {pdf}")
            except Exception as e:
                print(f"  Error searching directory: {str(e)}")
        else:
            print(f"Directory does not exist: {search_dir}")

if __name__ == "__main__":
    print("File Path Debugging Tool")
    print("=======================")
    check_paths()
    print("\nDone!")