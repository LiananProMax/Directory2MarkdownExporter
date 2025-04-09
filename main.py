import os
import argparse
from collections import deque
from dotenv import load_dotenv

load_dotenv()  # 加载.env文件中的环境变量

def generate_directory_tree(root_dir, exclude_dirs, exclude_files, exclude_exts):
    """
    生成类tree命令的目录结构，返回元组（树形字符串，目录数，文件数）
    """
    tree_str = ".\n"
    dir_count = 0
    file_count = 0

    queue = deque()
    queue.append((root_dir, [], True))  # (路径, 前缀组件，是否是最后项)

    while queue:
        current_path, prefixes, is_last = queue.popleft()
        relative_path = os.path.relpath(current_path, root_dir)
        
        if relative_path == ".":
            display_name = ""
        else:
            display_name = os.path.basename(current_path)

        # 生成连接线
        if prefixes:
            connector = "└── " if is_last else "├── "
        else:
            connector = ""

        # 生成前缀线条
        line_prefix = ""
        for prefix in prefixes:
            line_prefix += "│   " if prefix else "    "

        # 拼接完整行
        if relative_path != ".":
            tree_str += f"{line_prefix}{connector}{display_name}\n"

        # 统计计数
        if os.path.isdir(current_path):
            if relative_path != ".":
                dir_count += 1
            entries = sorted(os.listdir(current_path))
            filtered_entries = []
            for e in entries:
                if e.startswith('.'):
                    continue
                entry_path = os.path.join(current_path, e)
                is_dir = os.path.isdir(entry_path)
                # 排除目录
                if is_dir and e in exclude_dirs:
                    continue
                # 排除文件和扩展名
                if not is_dir:
                    if e in exclude_files:
                        continue
                    ext = os.path.splitext(e)[1]
                    if ext in exclude_exts:
                        continue
                filtered_entries.append(e)
            entries = filtered_entries
            
            # 准备子项前缀
            for i, entry in enumerate(entries):
                entry_path = os.path.join(current_path, entry)
                new_prefixes = prefixes.copy()
                new_prefixes.append(not is_last)
                is_last_child = (i == len(entries) - 1)
                queue.append((entry_path, new_prefixes, is_last_child))
        else:
            file_count += 1

    return tree_str, dir_count, file_count

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
            # 应用目录排除规则
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            for filename in files:
                # 应用文件和扩展名排除规则
                if filename in exclude_files:
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
    
    # 解析排除规则
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
