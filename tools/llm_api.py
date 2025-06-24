#!/usr/bin/env python3
# 指定脚本使用python3解释器执行

import google.generativeai as genai  # 导入Google Gemini模型的官方库
from openai import OpenAI, AzureOpenAI  # 从openai库导入主客户端和Azure专用客户端
from anthropic import Anthropic  # 导入Anthropic Claude模型的官方库
import argparse  # 导入用于解析命令行参数的库
import os  # 导入与操作系统交互的库，如此处用于获取环境变量
from dotenv import load_dotenv  # 从python-dotenv库导入函数，用于从.env文件加载环境变量
from pathlib import Path  # 导入Path对象，用于以面向对象的方式处理文件系统路径
import sys  # 导入系统相关的参数和函数，如此处用于向标准错误流输出信息
import base64  # 导入用于Base64编码和解码的库，主要用于处理图片
from typing import Optional, Union, List  # 从typing库导入类型提示，增强代码可读性和健壮性
import mimetypes  # 导入用于猜测文件MIME类型的库

def load_environment():
    """按照预设的优先级顺序从.env系列文件加载环境变量。"""
    # 优先级顺序如下:
    # 1. 系统环境变量 (已经由操作系统加载)
    # 2. .env.local (用户本地的特定配置，优先级最高)
    # 3. .env (项目的默认配置)
    # 4. .env.example (示例配置，优先级最低)
    
    env_files = ['.env.local', '.env', '.env.example']  # 定义要查找的.env文件列表，按优先级排序
    env_loaded = False  # 初始化一个标志，用于记录是否成功加载了任何.env文件
    
    print("Current working directory:", Path('.').absolute(), file=sys.stderr)  # 打印当前工作目录的绝对路径，用于调试
    print("Looking for environment files:", env_files, file=sys.stderr)  # 打印将要查找的env文件列表，用于调试
    
    for env_file in env_files:  # 遍历文件列表
        env_path = Path('.') / env_file  # 构建当前工作目录下.env文件的完整路径
        print(f"Checking {env_path.absolute()}", file=sys.stderr)  # 打印正在检查的文件路径，用于调试
        if env_path.exists():  # 检查文件是否存在
            print(f"Found {env_file}, loading variables...", file=sys.stderr)  # 如果找到文件，打印提示信息
            load_dotenv(dotenv_path=env_path, override=True)  # 加载该.env文件中的环境变量, override=True表示后加载的文件会覆盖先加载的
            env_loaded = True  # 设置标志为True
            print(f"Loaded environment variables from {env_file}", file=sys.stderr)  # 打印成功加载的提示
            # 为了安全，只打印加载的变量名（key），不打印值（value）
            with open(env_path) as f:  # 打开.env文件
                # 读取文件中的每一行，提取等号前的key，并排除注释行
                keys = [line.split('=')[0].strip() for line in f if '=' in line and not line.startswith('#')]
                print(f"Keys loaded from {env_file}: {keys}", file=sys.stderr)  # 打印从文件中加载的key列表
    
    if not env_loaded:  # 如果遍历完所有文件后，仍然没有加载任何.env文件
        print("Warning: No .env files found. Using system environment variables only.", file=sys.stderr)  # 打印警告信息
        print("Available system environment variables:", list(os.environ.keys()), file=sys.stderr)  # 打印当前所有可用的系统环境变量名

# 在模块导入时立即执行load_environment函数，以确保环境变量在后续代码执行前已准备就绪
load_environment()

def encode_image_file(image_path: str) -> tuple[str, str]:
    """
    将图片文件编码为Base64字符串，并确定其MIME类型。
    
    Args:
        image_path (str): 图片文件的路径
        
    Returns:
        tuple: (Base64编码的字符串, MIME类型)
    """
    mime_type, _ = mimetypes.guess_type(image_path)  # 根据文件路径猜测文件的MIME类型
    if not mime_type:  # 如果无法确定MIME类型
        mime_type = 'image/png'  # 默认使用'image/png'
        
    with open(image_path, "rb") as image_file:  # 以二进制只读模式("rb")打开图片文件
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')  # 读取文件内容，进行Base64编码，然后解码为UTF-8字符串
        
    return encoded_string, mime_type  # 返回编码后的字符串和MIME类型

def create_llm_client(provider="openai"):
    """根据指定的提供商名称，创建并返回相应的大语言模型客户端实例。"""
    if provider == "openai":  # 如果提供商是'openai'
        api_key = os.getenv('OPENAI_API_KEY')  # 从环境变量中获取OpenAI API Key
        base_url = os.getenv('OPENAI_BASE_URL', "https://api.openai.com/v1")  # 获取基础URL，如果未设置则使用官方默认值
        if not api_key:  # 如果未找到API Key
            raise ValueError("OPENAI_API_KEY not found in environment variables")  # 抛出错误
        return OpenAI(api_key=api_key, base_url=base_url)  # 创建并返回OpenAI客户端实例
    
    elif provider == "azure":  # 如果提供商是'azure'
        api_key = os.getenv('AZURE_OPENAI_API_KEY')  # 从环境变量获取Azure OpenAI API Key
        if not api_key:  # 如果未找到
            raise ValueError("AZURE_OPENAI_API_KEY not found in environment variables")  # 抛出错误
        return AzureOpenAI(  # 创建并返回Azure OpenAI客户端实例
            api_key=api_key,
            api_version="2024-08-01-preview",  # 指定API版本
            azure_endpoint="https://msopenai.openai.azure.com"  # 指定Azure的端点
        )
        
    elif provider == "deepseek":  # 如果提供商是'deepseek'
        api_key = os.getenv('DEEPSEEK_API_KEY')  # 获取DeepSeek API Key
        if not api_key:  # 如果未找到
            raise ValueError("DEEPSEEK_API_KEY not found in environment variables")  # 抛出错误
        return OpenAI(  # DeepSeek使用与OpenAI兼容的API，因此也用OpenAI客户端
            api_key=api_key,
            base_url="https://api.deepseek.com/v1",  # 指定DeepSeek的API地址
        )
        
    elif provider == "siliconflow":  # 如果提供商是'siliconflow'
        api_key = os.getenv('SILICONFLOW_API_KEY')  # 获取SiliconFlow API Key
        if not api_key:  # 如果未找到
            raise ValueError("SILICONFLOW_API_KEY not found in environment variables")  # 抛出错误
        return OpenAI(  # SiliconFlow也使用与OpenAI兼容的API
            api_key=api_key,
            base_url="https://api.siliconflow.cn/v1"  # 指定SiliconFlow的API地址
        )
        
    elif provider == "anthropic":  # 如果提供商是'anthropic'
        api_key = os.getenv('ANTHROPIC_API_KEY')  # 获取Anthropic API Key
        if not api_key:  # 如果未找到
            raise ValueError("ANTHROPIC_API_KEY not found in environment variables")  # 抛出错误
        return Anthropic(api_key=api_key)  # 创建并返回Anthropic客户端实例
    
    elif provider == "gemini":  # 如果提供商是'gemini'
        api_key = os.getenv('GOOGLE_API_KEY')  # 获取Google API Key
        if not api_key:  # 如果未找到
            raise ValueError("GOOGLE_API_KEY not found in environment variables")  # 抛出错误
        genai.configure(api_key=api_key)  # 配置Google Gemini库
        return genai  # 返回配置好的genai模块本身作为客户端
    
    elif provider == "local":  # 如果是本地部署的模型
        return OpenAI(  # 假设本地模型服务也兼容OpenAI的API格式
            base_url="http://192.168.180.137:8006/v1",  # 指定本地服务的地址
            api_key="not-needed"  # 本地服务通常不需要API Key
        )
        
    else:  # 如果提供了不支持的provider名称
        raise ValueError(f"Unsupported provider: {provider}")  # 抛出错误

def query_llm(prompt: str, client=None, model=None, provider="openai", image_path: Optional[str] = None) -> Optional[str]:
    """
    使用给定的提示语和可选的图片，查询一个大语言模型。
    
    Args:
        prompt (str): 发送给模型的文本提示
        client: LLM客户端实例，如果为None则会自动创建一个
        model (str, optional): 要使用的具体模型名称
        provider (str): 要使用的API提供商
        image_path (str, optional): 要附加的图片文件的路径
        
    Returns:
        Optional[str]: 模型的回复内容，如果出错则返回None
    """
    if client is None:  # 如果没有传入客户端实例
        client = create_llm_client(provider)  # 则根据provider创建一个新的
    
    try:
        # 如果没有指定模型，则根据提供商设置默认模型
        if model is None:
            if provider == "openai":
                model = os.getenv('OPENAI_MODEL_DEPLOYMENT', 'gpt-4o')  # OpenAI默认使用gpt-4o
            elif provider == "azure":
                model = os.getenv('AZURE_OPENAI_MODEL_DEPLOYMENT', 'gpt-4o-ms')  # Azure默认使用环境变量中指定的模型或'gpt-4o-ms'
            elif provider == "deepseek":
                model = "deepseek-chat"  # DeepSeek默认模型
            elif provider == "siliconflow":
                model = "deepseek-ai/DeepSeek-R1"  # SiliconFlow默认模型
            elif provider == "anthropic":
                model = "claude-3-7-sonnet-20250219"  # Anthropic默认模型
            elif provider == "gemini":
                model = "gemini-2.0-flash-exp"  # Gemini默认模型
            elif provider == "local":
                model = "Qwen/Qwen2.5-32B-Instruct-AWQ"  # 本地默认模型
        
        # 处理与OpenAI API兼容的提供商
        if provider in ["openai", "local", "deepseek", "azure", "siliconflow"]:
            messages = [{"role": "user", "content": []}]  # 初始化消息列表，采用OpenAI格式
            
            # 添加文本内容
            messages[0]["content"].append({
                "type": "text",
                "text": prompt
            })
            
            # 如果提供了图片路径，则添加图片内容
            if image_path:
                if provider == "openai":  # OpenAI的多模态输入格式
                    encoded_image, mime_type = encode_image_file(image_path)  # 编码图片
                    # 重新构造content列表以包含文本和图片
                    messages[0]["content"] = [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:{mime_type};base64,{encoded_image}"}}
                    ]
            
            # 准备API调用的参数
            kwargs = {
                "model": model,
                "messages": messages,
                "temperature": 0.7,  # temperature控制生成文本的随机性
            }
            
            # 针对特定模型"o1"的特殊参数处理 (如果存在)
            if model == "o1":
                kwargs["response_format"] = {"type": "text"}
                kwargs["reasoning_effort"] = "low"
                del kwargs["temperature"]
            
            response = client.chat.completions.create(**kwargs)  # 发起API请求
            return response.choices[0].message.content  # 返回模型生成的内容
            
        # 处理Anthropic (Claude)
        elif provider == "anthropic":
            messages = [{"role": "user", "content": []}]  # 初始化消息列表，采用Anthropic格式
            
            # 添加文本内容
            messages[0]["content"].append({
                "type": "text",
                "text": prompt
            })
            
            # 如果提供了图片，则添加图片内容
            if image_path:
                encoded_image, mime_type = encode_image_file(image_path)  # 编码图片
                messages[0]["content"].append({  # 添加图片数据块
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": mime_type,
                        "data": encoded_image
                    }
                })
            
            response = client.messages.create(  # 发起API请求
                model=model,
                max_tokens=1000,  # 设置最大生成token数
                messages=messages
            )
            return response.content[0].text  # 返回模型生成的内容
            
        # 处理Google Gemini
        elif provider == "gemini":
            model = client.GenerativeModel(model)  # 获取具体的生成模型实例
            if image_path:  # 如果有图片
                file = genai.upload_file(image_path, mime_type="image/png")  # 上传图片文件
                chat_session = model.start_chat(  # 开始一个聊天会话，历史消息包含图片和提示
                    history=[{
                        "role": "user",
                        "parts": [file, prompt]
                    }]
                )
            else:  # 如果没有图片
                chat_session = model.start_chat(  # 开始一个聊天会话，历史消息只包含提示
                    history=[{
                        "role": "user",
                        "parts": [prompt]
                    }]
                )
            response = chat_session.send_message(prompt)  # 发送当前提示并获取回复
            return response.text  # 返回回复中的文本内容
            
    except Exception as e:
        print(f"Error querying LLM: {e}", file=sys.stderr)  # 如果发生任何异常，打印错误信息到标准错误流
        return None  # 返回None表示失败

def main():
    # 创建命令行参数解析器
    parser = argparse.ArgumentParser(description='使用提示查询一个大语言模型')
    # 添加'--prompt'参数，必须提供
    parser.add_argument('--prompt', type=str, help='发送给LLM的提示', required=True)
    # 添加'--provider'参数，有固定选项，默认为'openai'
    parser.add_argument('--provider', choices=['openai','anthropic','gemini','local','deepseek','azure','siliconflow'], default='openai', help='要使用的API提供商')
    # 添加'--model'参数，可选
    parser.add_argument('--model', type=str, help='要使用的模型 (默认值取决于提供商)')
    # 添加'--image'参数，用于指定图片路径
    parser.add_argument('--image', type=str, help='要附加到提示的图片文件路径')
    args = parser.parse_args()  # 解析命令行传入的参数

    # 如果用户没有通过命令行指定模型，则设置默认模型
    if not args.model:
        if args.provider == 'openai':
            args.model = "gpt-4o" 
        elif args.provider == "deepseek":
            args.model = "deepseek-chat"
        elif args.provider == "siliconflow":
            args.model = "deepseek-ai/DeepSeek-R1"
        elif args.provider == 'anthropic':
            args.model = "claude-3-7-sonnet-20250219"
        elif args.provider == 'gemini':
            args.model = "gemini-2.0-flash-exp"
        elif args.provider == 'azure':
            args.model = os.getenv('AZURE_OPENAI_MODEL_DEPLOYMENT', 'gpt-4o-ms')  # 对于Azure，再次尝试从环境变量获取

    client = create_llm_client(args.provider)  # 根据提供商创建LLM客户端
    # 调用核心查询函数，传入所有相关参数
    response = query_llm(args.prompt, client, model=args.model, provider=args.provider, image_path=args.image)
    if response:  # 如果成功获取到回复
        print(response)  # 打印回复内容
    else:
        print("Failed to get response from LLM")  # 否则打印失败信息

if __name__ == "__main__":
    # 检查脚本是否作为主程序运行
    main()  # 如果是，则调用main函数