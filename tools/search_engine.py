#!/usr/bin/env python3
# 指定脚本使用python3解释器执行

import argparse  # 导入用于解析命令行参数的库
import sys  # 导入系统相关的参数和函数，如此处用于向标准错误流输出信息
import time  # 导入时间库，用于在重试之间添加延迟
from duckduckgo_search import DDGS  # 从duckduckgo_search库导入DDGS客户端

def search_with_retry(query, max_results=10, max_retries=3):
    """
    使用DuckDuckGo进行搜索，并返回包含URL和文本摘要的结果。
    此函数包含了重试机制以应对可能的临时网络错误。
    
    Args:
        query (str): 搜索的关键词
        max_results (int): 希望返回的最大结果数量
        max_retries (int): 失败后最大重试次数
    """
    for attempt in range(max_retries):  # 循环进行多次尝试，最多'max_retries'次
        try:
            # 打印调试信息到标准错误流，显示当前正在尝试的查询和次数
            print(f"DEBUG: Searching for query: {query} (attempt {attempt + 1}/{max_retries})", 
                  file=sys.stderr)
            
            with DDGS() as ddgs:  # 使用上下文管理器创建并自动关闭DDGS客户端实例
                # 执行文本搜索，并将生成器结果转换为列表
                results = list(ddgs.text(query, max_results=max_results))
                
            if not results:  # 如果搜索没有返回任何结果
                print("DEBUG: No results found", file=sys.stderr)  # 打印调试信息
                return []  # 返回一个空列表
            
            print(f"DEBUG: Found {len(results)} results", file=sys.stderr)  # 打印成功找到的结果数量
            return results  # 返回搜索结果列表
                
        except Exception as e:  # 捕获在搜索过程中可能发生的任何异常
            # 打印错误信息，包括尝试次数和具体的异常内容
            print(f"ERROR: Attempt {attempt + 1}/{max_retries} failed: {str(e)}", file=sys.stderr)
            if attempt < max_retries - 1:  # 检查是否还有重试机会
                print(f"DEBUG: Waiting 1 second before retry...", file=sys.stderr)  # 打印等待提示
                time.sleep(1)  # 程序暂停1秒钟，然后再进行下一次尝试
            else:  # 如果所有重试都已用尽
                print(f"ERROR: All {max_retries} attempts failed", file=sys.stderr)  # 打印最终的失败信息
                raise  # 重新抛出最后的异常，让上层调用者知道操作失败

def format_results(results):
    """格式化并打印搜索结果。"""
    for i, r in enumerate(results, 1):  # 遍历搜索结果列表，i从1开始计数
        print(f"\n=== Result {i} ===")  # 打印每个结果的标题
        print(f"URL: {r.get('href', 'N/A')}")  # 打印结果的URL，如果不存在则打印'N/A'
        print(f"Title: {r.get('title', 'N/A')}")  # 打印结果的标题，如果不存在则打印'N/A'
        print(f"Snippet: {r.get('body', 'N/A')}")  # 打印结果的摘要文本，如果不存在则打印'N/A'

def search(query, max_results=10, max_retries=3):
    """
    主搜索函数，封装了带重试的搜索逻辑和结果格式化。
    
    Args:
        query (str): 搜索的关键词
        max_results (int): 希望返回的最大结果数量
        max_retries (int): 失败后最大重试次数
    """
    try:
        results = search_with_retry(query, max_results, max_retries)  # 调用带重试的搜索函数
        if results:  # 如果获取到了结果
            format_results(results)  # 调用函数将结果格式化并打印出来
            
    except Exception as e:  # 捕获从search_with_retry抛出的最终异常
        print(f"ERROR: Search failed: {str(e)}", file=sys.stderr)  # 打印最终的失败信息
        sys.exit(1)  # 退出程序，返回状态码1表示发生了错误

def main():
    """脚本的主入口函数，负责处理命令行参数。"""
    parser = argparse.ArgumentParser(description="使用DuckDuckGo API进行搜索")  # 创建参数解析器
    parser.add_argument("query", help="要搜索的关键词")  # 添加一个必须的位置参数'query'
    parser.add_argument("--max-results", type=int, default=10,
                      help="最大结果数量 (默认: 10)")  # 添加可选参数'--max-results'
    parser.add_argument("--max-retries", type=int, default=3,
                      help="最大重试次数 (默认: 3)")  # 添加可选参数'--max-retries'
    
    args = parser.parse_args()  # 解析命令行传入的参数
    search(args.query, args.max_results, args.max_retries)  # 使用解析到的参数调用主搜索函数

if __name__ == "__main__":
    # 这是一个标准的Python入口点检查。
    # 如果这个脚本是直接被执行的（而不是被导入到其他脚本中），
    # 那么就调用main()函数开始执行程序。
    main()