#!/usr/bin/env python3
"""
模型预热脚本
用于在RAG服务启动前预加载和预热各类模型
支持嵌入模型、重排序模型和文本生成模型
"""

import argparse
import json
import logging
import os
import sys
import time
from typing import Dict, Any, Optional

import torch
from transformers import AutoModel, AutoTokenizer, AutoModelForCausalLM
try:
    from sentence_transformers import SentenceTransformer, CrossEncoder
except ImportError:
    # 如果sentence_transformers未安装，提供错误信息
    print("Error: sentence_transformers package is required for this script.")
    print("Please install it using: pip install sentence-transformers")
    sys.exit(1)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('model-warmup')

def load_config(config_path: str) -> Dict[str, Any]:
    """
    加载配置文件
    
    Args:
        config_path: 配置文件路径
        
    Returns:
        配置字典
    """
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        return config
    except Exception as e:
        logger.error(f"加载配置文件失败: {str(e)}")
        sys.exit(1)

def warmup_embedding_model(config: Dict[str, Any]) -> None:
    """
    预热嵌入模型
    
    Args:
        config: 配置字典
    """
    model_config = config.get('models', {}).get('embedding', {})
    model_name = model_config.get('model_name', 'BAAI/bge-small-zh-v1.5')
    cache_dir = model_config.get('cache_dir', '/app/models/embedding')
    device = model_config.get('device', 'cpu')
    normalize = model_config.get('normalize_embeddings', True)
    
    logger.info(f"正在加载嵌入模型: {model_name}")
    start_time = time.time()
    
    try:
        # 使用SentenceTransformer加载模型
        model = SentenceTransformer(model_name, cache_folder=cache_dir, device=device)
        
        # 进行简单的预热操作
        sample_texts = [
            "中医养生的基本原则是什么？",
            "如何根据体质进行食疗调养？",
            "经络穴位按摩的作用与方法",
            "四季养生食材有哪些推荐？",
            "索克生活平台提供哪些健康服务？"
        ]
        
        logger.info("正在预热嵌入模型...")
        embeddings = model.encode(sample_texts, normalize_embeddings=normalize)
        
        logger.info(f"嵌入模型预热完成，耗时: {time.time() - start_time:.2f}秒")
        logger.info(f"生成的嵌入维度: {embeddings.shape}")
        
    except Exception as e:
        logger.error(f"预热嵌入模型失败: {str(e)}")
        sys.exit(1)

def warmup_reranker_model(config: Dict[str, Any]) -> None:
    """
    预热重排序模型
    
    Args:
        config: 配置字典
    """
    model_config = config.get('models', {}).get('reranker', {})
    model_name = model_config.get('model_name', 'BAAI/bge-reranker-base')
    cache_dir = model_config.get('cache_dir', '/app/models/reranker')
    device = model_config.get('device', 'cpu')
    
    logger.info(f"正在加载重排序模型: {model_name}")
    start_time = time.time()
    
    try:
        # 使用CrossEncoder加载模型
        model = CrossEncoder(model_name, device=device, cache_folder=cache_dir)
        
        # 进行简单的预热操作
        sample_pairs = [
            ["中医养生的基本原则是什么？", "中医养生讲究顺应自然、阴阳平衡，注重防病于未然。"],
            ["如何根据体质进行食疗调养？", "不同体质的人需要不同的食疗方案，比如阳虚体质宜温补，阴虚体质宜滋阴。"],
            ["经络穴位按摩的作用与方法", "经络穴位按摩可以疏通气血，缓解疲劳，增强身体免疫力。"],
            ["四季养生食材有哪些推荐？", "春季宜食葱姜蒜；夏季宜食苦瓜莲藕；秋季宜食梨柿栗子；冬季宜食羊肉大枣。"],
            ["索克生活平台提供哪些健康服务？", "索克生活平台提供中医体质辨识、健康咨询、养生指导和个性化健康方案。"]
        ]
        
        logger.info("正在预热重排序模型...")
        scores = model.predict(sample_pairs)
        
        logger.info(f"重排序模型预热完成，耗时: {time.time() - start_time:.2f}秒")
        logger.info(f"预热生成的得分数量: {len(scores)}")
        
    except Exception as e:
        logger.error(f"预热重排序模型失败: {str(e)}")
        sys.exit(1)

def warmup_generation_model(config: Dict[str, Any]) -> None:
    """
    预热文本生成模型
    
    Args:
        config: 配置字典
    """
    model_config = config.get('models', {}).get('llm', {})
    model_name = model_config.get('model_name', 'Qwen/Qwen1.5-7B-Chat')
    cache_dir = model_config.get('cache_dir', '/app/models/text-generation')
    device = model_config.get('device', 'cpu')
    max_length = model_config.get('max_length', 2048)
    temperature = model_config.get('temperature', 0.7)
    
    logger.info(f"正在加载文本生成模型: {model_name}")
    start_time = time.time()
    
    try:
        # 使用Transformers加载模型
        tokenizer = AutoTokenizer.from_pretrained(model_name, cache_dir=cache_dir)
        model = AutoModelForCausalLM.from_pretrained(
            model_name, 
            cache_dir=cache_dir,
            torch_dtype=torch.float16 if device != 'cpu' else torch.float32,
            low_cpu_mem_usage=True
        )
        
        # 如果有GPU且配置为使用GPU，则将模型移至GPU
        if device != 'cpu' and torch.cuda.is_available():
            model = model.to(device)
        
        # 进行简单的预热操作
        sample_prompt = "请用中医理论解释一下什么是\"阴阳平衡\"？"
        
        logger.info("正在预热文本生成模型...")
        inputs = tokenizer(sample_prompt, return_tensors="pt")
        if device != 'cpu' and torch.cuda.is_available():
            inputs = {k: v.to(device) for k, v in inputs.items()}
            
        # 生成文本
        with torch.no_grad():
            outputs = model.generate(
                **inputs, 
                max_length=max_length, 
                temperature=temperature,
                num_return_sequences=1
            )
        
        # 解码输出
        generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        logger.info(f"文本生成模型预热完成，耗时: {time.time() - start_time:.2f}秒")
        logger.info(f"生成的文本长度: {len(generated_text)}")
        
    except Exception as e:
        logger.error(f"预热文本生成模型失败: {str(e)}")
        sys.exit(1)

def main():
    """
    主函数
    """
    max_retries = 3
    retry_delay = 10  # 秒
    
    parser = argparse.ArgumentParser(description='RAG模型预热工具')
    parser.add_argument('--model-type', type=str, required=True, 
                      choices=['embedding', 'reranker', 'generation', 'all'],
                      help='要预热的模型类型: embedding, reranker, generation, all')
    parser.add_argument('--config', type=str, required=True,
                      help='配置文件路径')
    
    args = parser.parse_args()
    
    # 带重试机制的配置加载
    config = None
    for attempt in range(max_retries):
        try:
            config = load_config(args.config)
            break
        except Exception as e:
            if attempt == max_retries - 1:
                logger.error(f"配置加载失败（尝试 {attempt+1}/{max_retries}）: {str(e)}")
                sys.exit(1)
            logger.warning(f"配置加载失败，{retry_delay}秒后重试...（{attempt+1}/{max_retries}）")
            time.sleep(retry_delay)
    
    # 带异常处理的模型预热流程
    success = False
    for attempt in range(max_retries):
        try:
            # 根据模型类型进行预热
            if args.model_type == 'embedding' or args.model_type == 'all':
                warmup_embedding_model(config)
                
            if args.model_type == 'reranker' or args.model_type == 'all':
                warmup_reranker_model(config)
                
            if args.model_type == 'generation' or args.model_type == 'all':
                warmup_generation_model(config)
            
            success = True
            break
        except Exception as e:
            if attempt == max_retries - 1:
                logger.error(f"模型预热失败（尝试 {attempt+1}/{max_retries}）: {str(e)}")
                sys.exit(1)
            logger.warning(f"模型预热失败，{retry_delay}秒后重试...（{attempt+1}/{max_retries}）")
            time.sleep(retry_delay)
    
    if success:
        logger.info("所有指定模型预热完成！")
        # 验证性检查
        try:
            if torch.cuda.is_available():
                logger.info(f"GPU内存使用情况: {torch.cuda.memory_allocated()/1024**2:.2f}MB / {torch.cuda.memory_reserved()/1024**2:.2f}MB")
        except Exception as e:
            logger.warning(f"资源检查失败: {str(e)}")

if __name__ == "__main__":
    main()
