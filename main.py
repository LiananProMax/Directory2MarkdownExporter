import os
import argparse
import fnmatch
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()  # 加载.env文件中的环境变量

def generate_directory_tree(root_dir, exclude_dirs, exclude_files, exclude_exts):
    """
    使用 pathlib 生成目录结构
    """
    root_path = Path(root_dir)
    tree_str = ".\n"
    dir_count = 0
    file_count = 0
    def should_include(path):
        name = path.name
        if path.is_dir():
            return not any(fnmatch.fnmatch(name, pattern) for pattern in exclude_dirs)
        else:
            if any(fnmatch.fnmatch(name, pattern) for pattern in exclude_files):
                return False
            return path.suffix not in exclude_exts
    def build_tree(path, prefix=""):
        nonlocal dir_count, file_count
        entries = sorted([p for p in path.iterdir() if should_include(p)])
        
        for i, entry in enumerate(entries):
            is_last = i == len(entries) - 1
            connector = "└── " if is_last else "├── "
            tree_str = prefix + connector + entry.name + "\n"
            
            if entry.is_dir():
                dir_count += 1
                new_prefix = prefix + ("    " if is_last else "│   ")
                yield tree_str
                yield from build_tree(entry, new_prefix)
            else:
                file_count += 1
                yield tree_str
    tree_lines = list(build_tree(root_path))
    return "".join(tree_lines), dir_count, file_count

def process_directory(input_dir, output_file, exclude_dirs, exclude_files, exclude_exts):
    # 生成目录树
    tree_str, dir_count, file_count = generate_directory_tree(input_dir, exclude_dirs, exclude_files, exclude_exts)

    with open(output_file, 'w', encoding='utf-8') as md:
        # 写入目录树
        md.write("目录结构\n```\n")
        md.write(tree_str)
        md.write(f"\n{dir_count} directories, {file_count} files\n")
        md.write("```\n\n")

        # 处理文件内容
        file_entries = []
        for root, dirs, files in os.walk(input_dir):
            # 应用目录排除规则（支持通配符）
            dirs[:] = [d for d in dirs if not any(fnmatch.fnmatch(d, pattern) for pattern in exclude_dirs)]
    
            for filename in files:
                # 应用文件和扩展名排除规则（支持通配符）
                if any(fnmatch.fnmatch(filename, pattern) for pattern in exclude_files):
                    continue
                ext = os.path.splitext(filename)[1]
                if ext in exclude_exts:
                    continue
                abs_path = os.path.join(root, filename)
                rel_path = os.path.relpath(abs_path, input_dir).replace(os.sep, '/')
                file_entries.append((rel_path, abs_path))

        file_entries.sort(key=lambda x: x[0])

        for rel_path, abs_path in file_entries:
            try:
                with open(abs_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except UnicodeDecodeError:
                print(f"⚠️ 跳过二进制文件: {rel_path}")
                continue
            except Exception as e:
                print(f"⛔ 读取文件失败 {rel_path}: {e}")
                continue

            md.write(f"{rel_path}\n```\n")
            md.write(content)
            if not content.endswith('\n'):
                md.write('\n')
            md.write("```\n\n")

if __name__ == "__main__":
    # 解析命令行参数（支持从.env获取默认值）
    parser = argparse.ArgumentParser(description="将目录内容导出为Markdown文件")
    parser.add_argument("input_dir", nargs='?', 
                        default=os.getenv('INPUT_DIR'), 
                        help="要遍历的目录路径（可在.env中设置INPUT_DIR）")
    parser.add_argument("output_file", nargs='?', 
                        default=os.getenv('OUTPUT_FILE'), 
                        help="输出的Markdown文件路径（可在.env中设置OUTPUT_FILE）")

    # 解析排除规则（支持通配符）
    exclude_dirs = [d.strip() for d in os.getenv('EXCLUDE_DIRS', '').split(',') if d.strip()]
    exclude_files = [f.strip() for f in os.getenv('EXCLUDE_FILES', '').split(',') if f.strip()]
    exclude_exts = [e.strip() for e in os.getenv('EXCLUDE_EXTENSIONS', '').split(',') if e.strip()]

    args = parser.parse_args()

    # 参数校验
    if not args.input_dir or not args.output_file:
        parser.error("必须提供输入目录和输出文件（可通过.env或命令行参数设置）")

    if not os.path.isdir(args.input_dir):
        print("错误：输入的路径不是有效目录")
        exit(1)

    process_directory(args.input_dir, args.output_file, exclude_dirs, exclude_files, exclude_exts)
    print(f"✅ 文件已成功导出至 {args.output_file}")
