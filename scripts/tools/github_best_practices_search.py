#!/usr/bin/env python3
"""
GitHub最佳实践搜索脚本
用于搜索和评估与索克生活项目相关的最佳实践
"""

import requests
import json
import time
from typing import List, Dict

class GitHubBestPracticesSearcher:
    def __init__(self, token: str = None):
        self.token = token
        self.base_url = "https://api.github.com"
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "SuokeLife-BestPractices-Searcher"
        }
        if token:
            self.headers["Authorization"] = f"token {token}"
    
    def search_repositories(self, query: str, sort: str = "stars", order: str = "desc", per_page: int = 10) -> List[Dict]:
        """搜索GitHub仓库"""
        url = f"{self.base_url}/search/repositories"
        params = {
            "q": query,
            "sort": sort,
            "order": order,
            "per_page": per_page
        }
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json().get("items", [])
        except requests.RequestException as e:
            print(f"搜索失败: {e}")
            return []
    
    def get_repository_details(self, owner: str, repo: str) -> Dict:
        """获取仓库详细信息"""
        url = f"{self.base_url}/repos/{owner}/{repo}"
        
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"获取仓库详情失败: {e}")
            return {}
    
    def evaluate_repository(self, repo: Dict) -> Dict:
        """评估仓库质量"""
        score = 0
        evaluation = {
            "name": repo.get("full_name", ""),
            "description": repo.get("description", ""),
            "stars": repo.get("stargazers_count", 0),
            "forks": repo.get("forks_count", 0),
            "issues": repo.get("open_issues_count", 0),
            "last_updated": repo.get("updated_at", ""),
            "language": repo.get("language", ""),
            "license": repo.get("license", {}).get("name", "None") if repo.get("license") else "None",
            "has_wiki": repo.get("has_wiki", False),
            "has_documentation": repo.get("has_pages", False),
            "score": 0,
            "recommendation": ""
        }
        
        # 评分标准
        if evaluation["stars"] > 1000:
            score += 3
        elif evaluation["stars"] > 100:
            score += 2
        elif evaluation["stars"] > 10:
            score += 1
        
        if evaluation["forks"] > 100:
            score += 2
        elif evaluation["forks"] > 10:
            score += 1
        
        # 最近更新（6个月内）
        try:
            from datetime import datetime, timedelta
            last_update = datetime.strptime(evaluation["last_updated"][:10], "%Y-%m-%d")
            if datetime.now() - last_update < timedelta(days=180):
                score += 2
        except:
            pass
        
        # 有文档和wiki
        if evaluation["has_wiki"]:
            score += 1
        if evaluation["has_documentation"]:
            score += 1
        
        # 有许可证
        if evaluation["license"] != "None":
            score += 1
        
        evaluation["score"] = score
        
        # 推荐等级
        if score >= 8:
            evaluation["recommendation"] = "强烈推荐"
        elif score >= 6:
            evaluation["recommendation"] = "推荐"
        elif score >= 4:
            evaluation["recommendation"] = "可考虑"
        else:
            evaluation["recommendation"] = "不推荐"
        
        return evaluation

def main():
    # 搜索关键词列表
    search_queries = [
        # 微服务架构
        "microservices best practices go",
        "microservices architecture patterns",
        "service mesh istio",
        
        # React Native
        "react native best practices",
        "react native boilerplate",
        "react native navigation",
        
        # AI/ML
        "multi agent systems",
        "langchain python",
        "machine learning pipeline",
        
        # 健康数据
        "healthcare data management",
        "medical data privacy",
        "fhir healthcare",
        
        # 区块链
        "blockchain healthcare",
        "hyperledger fabric",
        "zero knowledge proofs",
        
        # 项目质量
        "code quality tools",
        "software metrics",
        "performance monitoring",
        
        # 中医相关
        "traditional chinese medicine ai",
        "tcm digitalization",
        "syndrome differentiation"
    ]
    
    searcher = GitHubBestPracticesSearcher()
    all_results = []
    
    print("开始搜索GitHub最佳实践项目...")
    
    for query in search_queries:
        print(f"\n搜索: {query}")
        repos = searcher.search_repositories(query, per_page=5)
        
        for repo in repos:
            evaluation = searcher.evaluate_repository(repo)
            all_results.append(evaluation)
            print(f"  - {evaluation['name']} (⭐{evaluation['stars']}) - {evaluation['recommendation']}")
        
        # 避免API限制
        time.sleep(1)
    
    # 按评分排序
    all_results.sort(key=lambda x: x["score"], reverse=True)
    
    # 保存结果
    output_file = "github_best_practices_evaluation.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)
    
    print(f"\n评估结果已保存到: {output_file}")
    
    # 显示top 10推荐
    print("\n=== TOP 10 推荐项目 ===")
    for i, result in enumerate(all_results[:10], 1):
        print(f"{i}. {result['name']}")
        print(f"   描述: {result['description'][:100]}...")
        print(f"   评分: {result['score']}/10 - {result['recommendation']}")
        print(f"   ⭐{result['stars']} 🍴{result['forks']} 📝{result['language']}")

if __name__ == "__main__":
    main() 