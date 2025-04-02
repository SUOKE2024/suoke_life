#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
中医词典模块
=========
提供中医术语字典功能，支持术语查询、同义词获取等
"""

import os
import logging
import json
from typing import Dict, List, Set, Any, Optional, Tuple
import jieba
import re

logger = logging.getLogger(__name__)

class Dictionary:
    """中医术语词典类"""
    
    def __init__(self, dictionary_path: str = None):
        """
        初始化词典
        
        Args:
            dictionary_path: 字典文件路径，默认为 data/dictionaries/dict.txt
        """
        self.terms = {}
        self.categories = set()
        self.synonyms_map = {}
        
        if dictionary_path is None:
            # 使用相对于当前文件的默认路径
            dictionary_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                "data/dictionaries/dict.txt"
            )
            
        self.dictionary_path = dictionary_path
        self.load_dictionary()
        
    def load_dictionary(self):
        """加载词典文件"""
        try:
            with open(self.dictionary_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                        
                    # 解析行内容
                    parts = line.split('|')
                    if len(parts) < 2:
                        continue
                        
                    term = parts[0].strip()
                    category = parts[1].strip()
                    synonyms = []
                    
                    if len(parts) > 2 and parts[2].strip():
                        synonyms = [s.strip() for s in parts[2].split(',')]
                        
                    # 添加术语信息
                    self.terms[term] = {
                        'term': term,
                        'category': category,
                        'synonyms': synonyms
                    }
                    
                    # 添加同义词映射
                    for synonym in synonyms:
                        self.synonyms_map[synonym] = term
                        
                    # 更新类别集合
                    self.categories.add(category)
                    
            logger.info(f"已加载中医词典，包含 {len(self.terms)} 个术语，{len(self.categories)} 个类别")
            
            # 将术语添加到结巴分词器中
            for term in list(self.terms.keys()) + list(self.synonyms_map.keys()):
                jieba.add_word(term)
                
        except Exception as e:
            logger.error(f"加载词典失败: {e}")
            raise
            
    def get_term_info(self, term: str) -> Optional[Dict[str, Any]]:
        """
        获取术语信息
        
        Args:
            term: 术语名称或同义词
            
        Returns:
            包含术语信息的字典，如找不到则返回None
        """
        # 检查原始术语
        if term in self.terms:
            return self.terms[term]
            
        # 检查同义词
        if term in self.synonyms_map:
            primary_term = self.synonyms_map[term]
            return self.terms[primary_term]
            
        return None
        
    def get_category(self, term: str) -> Optional[str]:
        """
        获取术语的类别
        
        Args:
            term: 术语名称或同义词
            
        Returns:
            术语类别，如找不到则返回None
        """
        info = self.get_term_info(term)
        return info['category'] if info else None
        
    def get_synonyms(self, term: str) -> List[str]:
        """
        获取术语的同义词
        
        Args:
            term: 术语名称
            
        Returns:
            同义词列表
        """
        info = self.get_term_info(term)
        return info['synonyms'] if info else []
        
    def is_term(self, term: str) -> bool:
        """
        检查是否为中医术语
        
        Args:
            term: 待检查的术语
            
        Returns:
            是否为中医术语
        """
        return term in self.terms or term in self.synonyms_map
        
    def extract_terms(self, text: str) -> List[Dict[str, Any]]:
        """
        从文本中提取中医术语
        
        Args:
            text: 输入文本
            
        Returns:
            提取出的术语信息列表
        """
        if not text:
            return []
            
        # 使用结巴分词
        words = jieba.cut(text)
        
        # 提取中医术语
        extracted_terms = []
        term_set = set()  # 用于去重
        
        for word in words:
            if self.is_term(word) and word not in term_set:
                term_info = self.get_term_info(word)
                extracted_terms.append(term_info)
                term_set.add(word)
                
        return extracted_terms
        
    def add_term(self, term: str, category: str, synonyms: List[str] = None) -> bool:
        """
        添加新术语
        
        Args:
            term: 术语名称
            category: 术语类别
            synonyms: 同义词列表
            
        Returns:
            是否添加成功
        """
        if not term or not category:
            return False
            
        if category not in self.categories:
            self.categories.add(category)
            
        if synonyms is None:
            synonyms = []
            
        # 已存在则更新
        if term in self.terms:
            self.terms[term]['category'] = category
            self.terms[term]['synonyms'] = synonyms
        else:
            # 添加新术语
            self.terms[term] = {
                'term': term,
                'category': category,
                'synonyms': synonyms
            }
            
            # 添加到jieba分词器
            jieba.add_word(term)
            
        # 更新同义词映射
        for synonym in synonyms:
            self.synonyms_map[synonym] = term
            jieba.add_word(synonym)
            
        return True
        
    def remove_term(self, term: str) -> bool:
        """
        删除术语
        
        Args:
            term: 术语名称
            
        Returns:
            是否删除成功
        """
        if term not in self.terms:
            return False
            
        # 删除同义词映射
        for synonym in self.terms[term]['synonyms']:
            if synonym in self.synonyms_map:
                del self.synonyms_map[synonym]
                
        # 删除术语
        del self.terms[term]
        return True
        
    def save_dictionary(self):
        """保存词典到文件"""
        try:
            with open(self.dictionary_path, 'w', encoding='utf-8') as f:
                f.write("# 中医术语词典\n")
                f.write("# 格式: 术语|类别|同义词1,同义词2,...\n\n")
                
                for term_info in self.terms.values():
                    synonyms_str = ",".join(term_info['synonyms'])
                    line = f"{term_info['term']}|{term_info['category']}|{synonyms_str}\n"
                    f.write(line)
                    
            logger.info(f"已保存词典到 {self.dictionary_path}")
            return True
            
        except Exception as e:
            logger.error(f"保存词典失败: {e}")
            return False 