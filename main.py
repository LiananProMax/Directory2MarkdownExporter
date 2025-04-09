import os
import argparse
from collections import deque

def generate_directory_tree(root_dir):
    """
    生成类tree命令的目录结构，返回元组（树形字符串，目录数，文件数）
    """
    tree_str = ".\n"
    dir_count = 0
    file_count = 0

    # 使用队列进行广度优先遍历
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
        if relative_path != ".":  # 跳过根目录显示
            tree_str += f"{line_prefix}{connector}{display_name}\n"

        # 统计计数
        if os.path.isdir(current_path):
            if relative_path != ".":  # 根目录不计入统计
                dir_count += 1
            entries = sorted(os.listdir(current_path))
            entries = [e for e in entries if not e.startswith('.')]  # 过滤隐藏文件
            
            # 准备子项前缀
            for i, entry in enumerate(entries):
                entry_path = os.path.join(current_path, entry)
                new_prefixes = prefixes.copy()
                new_prefixes.append(not is_last)  # 是否继续垂直线
                is_last_child = (i == len(entries) - 1)
                queue.append((entry_path, new_prefixes, is_last_child))
        else:
            file_count += 1

    return tree_str, dir_count, file_count

def process_directory(input_dir, output_file):
    # 生成目录树
    tree_str, dir_count, file_count = generate_directory_tree(input_dir)
    
    with open(output_file, 'w', encoding='utf-8') as md:
        # 写入目录树
        md.write("目录结构\n```\n")
        md.write(tree_str)
        md.write(f"\n{dir_count} directories, {file_count} files\n")
        md.write("```\n\n")

        # 原始文件内容处理（保持原逻辑）
        file_entries = []
        for root, dirs, files in os.walk(input_dir):
            for filename in files:
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

# 保持原有命令行参数和主逻辑...
# （此处与之前的主函数部分相同，保持不变）

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="将目录内容导出为Markdown文件")
    parser.add_argument("input_dir", help="要遍历的目录路径")
    parser.add_argument("output_file", help="输出的Markdown文件路径")
    args = parser.parse_args()

    if not os.path.isdir(args.input_dir):
        print("错误：输入的路径不是有效目录")
        exit(1)

    process_directory(args.input_dir, args.output_file)
    print(f"✅ 文件已成功导出至 {args.output_file}")