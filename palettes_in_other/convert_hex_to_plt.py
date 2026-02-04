#!/usr/bin/env python
"""
Convert hex color palette files to .plt format

hex file format:
- One hex color per line (e.g., #FF0000)
- Optional comment lines starting with #

.plt file format:
- Line 1: Palette name
- Line 2: Palette source (leave blank if not provided)
- Line 3+: Hex colors (#RRGGBB format)
"""

import os
import re
from pathlib import Path

def validate_hex_color(color):
    """Check if a string is a valid hex color (with or without #)"""
    # Remove # if present
    color = color.lstrip('#')
    # Check if it's a valid 3 or 6 digit hex color
    pattern = r'^(?:[0-9a-fA-F]{3}){1,2}$'
    return re.search(pattern, color) is not None

def normalize_hex_color(color):
    """Normalize hex color to #RRGGBB format"""
    color = color.strip().lstrip('#')
    # Handle 3-digit hex (e.g., "abc" -> "aabbcc")
    if len(color) == 3:
        color = ''.join([c*2 for c in color])
    return f"#{color.upper()}"

def extract_palette_name(filename):
    """Extract palette name from filename (remove extension)"""
    return Path(filename).stem

def convert_hex_to_plt(hex_file_path, plt_output_dir, palette_name=None, palette_source=""):
    """Convert a hex color file to .plt format"""
    
    # Read hex file
    try:
        with open(hex_file_path, 'r', encoding='utf-8') as f:
            lines = f.read().splitlines()
    except Exception as e:
        print(f"Error reading {hex_file_path}: {e}")
        return False
    
    # Extract colors (skip empty lines and comments)
    colors = []
    for line in lines:
        line = line.strip()
        # Skip empty lines
        if not line:
            continue
        # Skip comment lines (lines starting with # that are not colors)
        if line.startswith('#') and not validate_hex_color(line):
            continue
        # Validate hex color
        if validate_hex_color(line):
            colors.append(normalize_hex_color(line))
    
    if not colors:
        print(f"No valid hex colors found in {hex_file_path}")
        return False
    
    # Generate palette name if not provided
    if palette_name is None:
        palette_name = extract_palette_name(hex_file_path)
    
    # Write .plt file
    plt_filename = f"{palette_name}.plt"
    plt_file_path = os.path.join(plt_output_dir, plt_filename)
    
    try:
        with open(plt_file_path, 'w', encoding='utf-8') as f:
            f.write(f"{palette_name}\n")
            f.write(f"{palette_source}\n")
            for color in colors:
                f.write(f"{color}\n")
        print(f"✓ Created: {plt_file_path} ({len(colors)} colors)")
        return True
    except Exception as e:
        print(f"Error writing {plt_file_path}: {e}")
        return False

def main():
    """Main conversion function"""
    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    hex_dir = os.path.join(script_dir, "hex_files")
    plt_dir = os.path.join(script_dir, "plt_files")
    
    # Check if hex_files directory exists
    if not os.path.exists(hex_dir):
        print(f"Error: {hex_dir} directory not found")
        return
    
    # Create plt_files directory if it doesn't exist
    os.makedirs(plt_dir, exist_ok=True)
    
    # Find all .hex files
    hex_files = [f for f in os.listdir(hex_dir) if f.endswith('.hex') or f.endswith('.txt')]
    
    if not hex_files:
        print(f"No .hex or .txt files found in {hex_dir}")
        return
    
    print(f"Found {len(hex_files)} hex file(s) to convert\n")
    
    # Convert each file
    success_count = 0
    for hex_file in sorted(hex_files):
        hex_path = os.path.join(hex_dir, hex_file)
        if convert_hex_to_plt(hex_path, plt_dir):
            success_count += 1
    
    print(f"\n{'='*50}")
    print(f"Conversion complete: {success_count}/{len(hex_files)} files converted successfully")

if __name__ == "__main__":
    main()
