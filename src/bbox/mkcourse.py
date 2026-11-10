#!/usr/bin/env python

import os
import json
import glob
import subprocess
import fire
from pathlib import Path


def mkcourse(directory, name, introduction, author):
    """
    扫描指定目录下的mp3文件，执行转录命令，生成课程JSON文件

    Args:
        directory: 包含mp3文件的目录路径
        name: 课程名称
        introduction: 课程介绍
        author: 作者名称
    """
    # 确保目录存在
    directory = Path(directory)
    if not directory.exists():
        print(f"错误: 目录 {directory} 不存在")
        return

    # 扫描mp3文件
    mp3_files = list(directory.glob("*.mp3"))
    if not mp3_files:
        print(f"警告: 目录 {directory} 中没有找到mp3文件")
        return

    # 按文件名排序
    mp3_files.sort(key=lambda x: x.name)

    print(f"找到 {len(mp3_files)} 个mp3文件")

    chapters = []

    # 处理每个mp3文件
    for mp3_file in mp3_files:
        print(f"处理文件: {mp3_file.name}")

        # 生成转录文件路径
        transcript_file = mp3_file.with_suffix('.json')

        # 如果转录文件不存在，执行转录命令
        if not transcript_file.exists():
            print(f"  转录文件不存在，开始转录...")
            try:
                cmd = [
                    "uvx",
                    "whisperx",
                    "--highlight_words", "True",
                    "--compute_type", "int8",
                    "--output_format", "json",
                    "--output_dir", str(directory),
                    str(mp3_file),
                ]

                print(f"  执行命令: {' '.join(cmd)}")
                print(f"  正在转录音频文件，请稍候...")

                # 使用实时输出的方式执行命令
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1,
                    universal_newlines=True
                )

                # 实时显示输出
                output_lines = []
                for line in process.stdout:
                    line = line.rstrip()
                    if line:
                        print(f"    {line}")
                        output_lines.append(line)

                # 等待进程完成
                return_code = process.wait()

                if return_code != 0:
                    print(f"  转录失败，退出码: {return_code}")
                    print(f"  完整输出:")
                    for line in output_lines:
                        print(f"    {line}")
                    continue
                else:
                    print(f"  ✅ 转录完成!")
                    # 检查是否生成了转录文件
                    if transcript_file.exists():
                        file_size = transcript_file.stat().st_size
                        print(f"  转录文件大小: {file_size} 字节")
                    else:
                        print(f"  ⚠️  警告: 转录完成但未找到输出文件")
                        continue

            except FileNotFoundError:
                print(f"  ❌ 错误: 未找到 uvx 或 whisperx 命令")
                print(f"  请先安装 uv: curl -LsSf https://astral.sh/uv/install.sh | sh")
                print(f"  然后安装 whisperx: uvx install whisperx")
                continue

            except Exception as e:
                print(f"  ❌ 执行转录时发生错误: {e}")
                continue

        else:
            print(f"  ✅ 转录文件已存在，跳过")

        # 获取章节名（去掉扩展名）
        chapter_name = mp3_file.stem

        # 生成相对路径（用于JSON中的URL）
        course_dir_name = directory.name
        media_url = f"/{course_dir_name}/{mp3_file.name}"
        transcript_url = f"/{course_dir_name}/{transcript_file.name}"

        # 添加到章节列表
        chapters.append({
            "name": chapter_name,
            "mediaUrl": media_url,
            "transcriptUrl": transcript_url
        })

    # 创建课程数据结构
    course_data = [{
        "name": name,
        "intro": introduction,
        "author": author,
        "chapters": chapters
    }]

    # 生成JSON文件路径（在指定目录的同级目录）
    output_file = directory.parent / f"course.json"

    # 写入JSON文件
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(course_data, f, ensure_ascii=False, indent=2)

        print(f"\n课程JSON文件已生成: {output_file}")
        print(f"包含 {len(chapters)} 个章节")

    except Exception as e:
        print(f"错误: 写入JSON文件失败 - {e}")


def main():
    fire.Fire(mkcourse)


if __name__ == '__main__':
    main()
