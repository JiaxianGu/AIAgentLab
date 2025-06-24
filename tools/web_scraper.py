#!/usr/bin/env python3
# 指定脚本使用python3解释器执行

import asyncio  # 导入异步I/O库，用于处理并发操作
import argparse # 导入命令行参数解析库
import sys # 导入系统相关功能库
import os # 导入操作系统相关功能库
from typing import List, Optional # 从typing库导入类型提示，用于代码可读性和静态分析
from playwright.async_api import async_playwright # 从playwright库导入异步API，用于浏览器自动化
import html5lib # 导入HTML解析库
from multiprocessing import Pool # 从多进程库导入Pool，用于并行处理
import time # 导入时间库，用于计时
from urllib.parse import urlparse # 从URL处理库导入urlparse，用于解析URL
import logging # 导入日志记录库

# 配置日志记录
logging.basicConfig(
    level=logging.INFO,  # 设置日志级别为INFO，记录INFO、WARNING、ERROR、CRITICAL级别的日志
    format='%(asctime)s - %(levelname)s - %(message)s',  # 设置日志格式，包含时间、级别和消息
    stream=sys.stderr  # 将日志输出到标准错误流
)
logger = logging.getLogger(__name__)  # 创建一个名为当前模块名的日志记录器

async def fetch_page(url: str, context) -> Optional[str]:
    """异步获取网页内容。"""
    page = await context.new_page()  # 在给定的浏览器上下文中创建一个新页面
    try:
        logger.info(f"Fetching {url}")  # 记录正在获取的URL
        await page.goto(url)  # 异步导航到指定的URL
        await page.wait_for_load_state('networkidle')  # 等待网络连接变为空闲状态，确保动态内容加载完成
        content = await page.content()  # 获取页面的完整HTML内容
        logger.info(f"Successfully fetched {url}")  # 记录成功获取URL
        return content  # 返回页面内容
    except Exception as e:
        logger.error(f"Error fetching {url}: {str(e)}")  # 如果在获取过程中发生异常，记录错误信息
        return None  # 返回None表示获取失败
    finally:
        await page.close()  # 无论成功与否，最后都关闭页面以释放资源

def parse_html(html_content: Optional[str]) -> str:
    """解析HTML内容并提取文本和Markdown格式的超链接。"""
    if not html_content:  # 检查传入的HTML内容是否为空
        return ""  # 如果为空，则返回一个空字符串
    
    try:
        document = html5lib.parse(html_content)  # 使用html5lib库将HTML字符串解析成一个文档对象
        result = []  # 初始化一个列表，用于存储解析后的文本行
        seen_texts = set()  # 创建一个集合，用于存储已经处理过的文本，以避免重复
        
        def should_skip_element(elem) -> bool:
            """检查是否应该跳过某个HTML元素。"""
            # 跳过<script>和<style>标签，因为它们不包含可见的文本内容
            if elem.tag in ['{http://www.w3.org/1999/xhtml}script', 
                          '{http://www.w3.org/1999/xhtml}style']:
                return True
            # 跳过不包含任何实际文本（或只包含空白）的元素
            if not any(text.strip() for text in elem.itertext()):
                return True
            return False  # 如果不满足以上条件，则不跳过该元素
        
        def process_element(elem, depth=0):
            """递归地处理一个元素及其所有子元素。"""
            if should_skip_element(elem):  # 首先检查是否应该跳过当前元素
                return  # 如果是，则直接返回，不进行处理
            
            # 处理元素自身的文本内容（即开标签后的文本）
            if hasattr(elem, 'text') and elem.text:  # 检查元素是否有'text'属性并且该属性值不为空
                text = elem.text.strip()  # 去除文本内容两端的空白字符
                if text and text not in seen_texts:  # 确保文本不为空且之前未被处理过
                    # 检查当前元素是否为<a>标签（超链接）
                    if elem.tag == '{http://www.w3.org/1999/xhtml}a':
                        href = None  # 初始化href变量
                        for attr, value in elem.items():  # 遍历元素的所有属性
                            if attr.endswith('href'):  # 查找'href'属性
                                href = value  # 获取链接地址
                                break  # 找到后即退出循环
                        if href and not href.startswith(('#', 'javascript:')):  # 确保链接有效且不是页面内锚点或JS代码
                            # 将链接格式化为Markdown语法：[文本](链接)
                            link_text = f"[{text}]({href})"
                            result.append("  " * depth + link_text)  # 根据递归深度添加缩进，并存入结果列表
                            seen_texts.add(text)  # 将该文本标记为已处理
                    else:
                        result.append("  " * depth + text)  # 对于非链接元素，直接添加文本和缩进
                        seen_texts.add(text)  # 将该文本标记为已处理
            
            # 递归处理所有子元素
            for child in elem:  # 遍历当前元素下的每一个子元素
                process_element(child, depth + 1)  # 对子元素调用自身，并将深度加一
            
            # 处理元素的尾部文本（即闭标签后的文本）
            if hasattr(elem, 'tail') and elem.tail:  # 检查元素是否有'tail'属性且不为空
                tail = elem.tail.strip()  # 去除尾部文本两端的空白
                if tail and tail not in seen_texts:  # 确保尾部文本有效且未被处理过
                    result.append("  " * depth + tail)  # 添加尾部文本和缩进
                    seen_texts.add(tail)  # 将该文本标记为已处理
        
        # 从<body>标签开始进行解析，以获取主要内容
        body = document.find('.//{http://www.w3.org/1999/xhtml}body')  # 在解析后的文档中查找<body>元素
        if body is not None:  # 如果找到了<body>元素
            process_element(body)  # 从<body>元素开始递归处理
        else:
            # 如果没有找到<body>，则从整个文档的根节点开始处理作为备用方案
            process_element(document)
        
        # 过滤掉常见的不需要的文本模式，如脚本代码或样式
        filtered_result = []  # 创建一个新列表来存储过滤后的结果
        for line in result:  # 遍历已提取的每一行文本
            # 检查行中是否包含常见的噪声关键词
            if any(pattern in line.lower() for pattern in [
                'var ', 
                'function()', 
                '.js',
                '.css',
                'google-analytics',
                'disqus',
                '{',
                '}'
            ]):
                continue  # 如果包含，则跳过这一行
            filtered_result.append(line)  # 将干净的行添加到过滤结果列表中
        
        return '\n'.join(filtered_result)  # 将过滤后的文本行用换行符连接成一个字符串并返回
    except Exception as e:
        logger.error(f"Error parsing HTML: {str(e)}")  # 如果解析过程中发生异常，记录错误
        return ""  # 返回空字符串

async def process_urls(urls: List[str], max_concurrent: int = 5) -> List[str]:
    """使用并发机制处理多个URL。"""
    async with async_playwright() as p:  # 启动并管理playwright的生命周期
        browser = await p.chromium.launch()  # 启动一个Chromium浏览器实例
        try:
            # 创建多个浏览器上下文（类似无痕窗口）以实现并发
            n_contexts = min(len(urls), max_concurrent)  # 计算要创建的上下文数量，不超过URL总数和最大并发数
            contexts = [await browser.new_context() for _ in range(n_contexts)]  # 创建指定数量的浏览器上下文
            
            # 为每个URL创建一个异步获取任务
            tasks = []  # 初始化任务列表
            for i, url in enumerate(urls):  # 遍历所有待处理的URL
                context = contexts[i % len(contexts)]  # 通过取模运算，将URL轮流分配给不同的上下文
                task = fetch_page(url, context)  # 为当前URL和分配的上下文创建一个获取页面的任务
                tasks.append(task)  # 将任务添加到任务列表
            
            # 并发执行所有获取任务并等待结果
            html_contents = await asyncio.gather(*tasks)  # 'gather'会并发运行所有任务并按顺序返回结果
            
            # 使用多进程并行解析HTML内容，以提高CPU密集型任务的效率
            with Pool() as pool:  # 创建一个进程池
                results = pool.map(parse_html, html_contents)  # 将'parse_html'函数应用到每个HTML内容上，并行执行
                
            return results  # 返回所有URL解析后的文本结果列表
            
        finally:
            # 清理所有资源，确保浏览器和上下文被正确关闭
            for context in contexts:  # 遍历所有创建的上下文
                await context.close()  # 关闭上下文
            await browser.close()  # 关闭浏览器实例

def validate_url(url: str) -> bool:
    """验证给定的字符串是否是一个有效的URL。"""
    try:
        result = urlparse(url)  # 使用urlparse函数解析URL字符串
        return all([result.scheme, result.netloc])  # 检查解析结果是否同时包含协议（scheme）和域名（netloc）
    except:
        return False  # 如果解析过程中发生任何异常（如传入的不是字符串），则认为URL无效

def main():
    # 创建一个命令行参数解析器
    parser = argparse.ArgumentParser(description='从网页获取并提取文本内容。')
    # 添加一个位置参数'urls'，它可以接受一个或多个URL
    parser.add_argument('urls', nargs='+', help='需要处理的URL列表')
    # 添加一个可选参数'--max-concurrent'，用于指定最大并发数
    parser.add_argument('--max-concurrent', type=int, default=5,
                       help='最大并发浏览器实例数 (默认: 5)')
    # 添加一个可选标志'--debug'，用于开启调试模式
    parser.add_argument('--debug', action='store_true',
                       help='启用调试级别日志')
    
    args = parser.parse_args()  # 解析命令行传入的参数
    
    if args.debug:  # 如果用户指定了--debug
        logger.setLevel(logging.DEBUG)  # 将日志记录器的级别设置为DEBUG
    
    # 验证用户传入的URL
    valid_urls = []  # 初始化一个列表来存储有效的URL
    for url in args.urls:  # 遍历所有传入的URL
        if validate_url(url):  # 检查URL是否有效
            valid_urls.append(url)  # 如果有效，则添加到列表中
        else:
            logger.error(f"Invalid URL: {url}")  # 如果无效，则记录一条错误日志
    
    if not valid_urls:  # 如果没有提供任何有效的URL
        logger.error("No valid URLs provided")  # 记录错误
        sys.exit(1)  # 退出程序，返回状态码1表示错误
    
    start_time = time.time()  # 记录开始处理的时间
    try:
        # 运行异步函数'process_urls'来处理所有有效URL
        results = asyncio.run(process_urls(valid_urls, args.max_concurrent))
        
        # 将结果打印到标准输出
        for url, text in zip(valid_urls, results):  # 将URL和其对应的结果配对遍历
            print(f"\n=== Content from {url} ===")  # 打印URL来源标题
            print(text)  # 打印提取的文本内容
            print("=" * 80)  # 打印分隔线
        
        logger.info(f"Total processing time: {time.time() - start_time:.2f}s")  # 记录并打印总处理时间
        
    except Exception as e:
        logger.error(f"Error during execution: {str(e)}")  # 如果在执行过程中发生任何未捕获的异常
        sys.exit(1)  # 记录错误并退出程序

if __name__ == '__main__':
    # 这是一个标准的Python入口点检查。
    # 如果这个脚本是直接被执行的（而不是被导入到其他脚本中），
    # 那么就调用main()函数开始执行程序。
    main() 