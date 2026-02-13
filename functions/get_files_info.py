import os
from google import genai
from google.genai import types

schema_get_files_info = types.FunctionDeclaration(
    name="get_files_info",
    description="Lists files in a specified directory relative to the working directory, providing file size and directory status",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "directory": types.Schema(
                type=types.Type.STRING,
                description="Directory path to list files from, relative to the working directory (default is the working directory itself)",
            ),
        },
    ),
)

def get_files_info(working_directory, directory="."):
    try:
        working_dir_abs = os.path.abspath(working_directory)
        target_dir = os.path.normpath(os.path.join(working_dir_abs, directory))

        valid_target_dir = os.path.commonpath([working_dir_abs, target_dir]) == working_dir_abs

        if not valid_target_dir:
            return f'Error: Cannot list "{directory}" as it is outside the permitted working directory'
        if not os.path.isdir(target_dir):
            return f'Error: "{directory}" is not a directory'
        dirlist = os.listdir(target_dir)

        lines = []
        for item in dirlist:
            # iterate over the items in the target directory. For each of them, record the name, file size, and whether it's a directory itself. Use this data to build and return a string representing the contents of the target directory. It should be in the following format:
            # - README.md: file_size=1032 bytes, is_dir=False
            # - src: file_size=128 bytes, is_dir=True
            # - package.json: file_size=1234 bytes, is_dir=False
            full_path = os.path.join(target_dir, item)
            file_size = os.path.getsize(full_path)
            is_dir = os.path.isdir(full_path)
            lines.append(f"- {item}: file_size={file_size} bytes, is_dir={is_dir}")
        return "\n".join(lines)
    except Exception as e:
        return f"Error: {e}"

         
