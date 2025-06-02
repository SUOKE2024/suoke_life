#!/usr/bin/env python3
"""
分析GitHub最佳实践搜索结果
针对索克生活项目的特定需求进行分类和推荐
"""

import json

def analyze_results():
    with open('github_best_practices_evaluation.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    print('🎯 针对索克生活项目的重点推荐项目分析:')
    print('=' * 60)

    # 按类别分析
    categories = {
        'microservices': ['go', 'microservice', 'service mesh', 'istio', 'api gateway', 'distributed'],
        'react_native': ['react native', 'react-native', 'mobile', 'navigation', 'boilerplate'],
        'ai_ml': ['ai', 'agent', 'langchain', 'machine learning', 'llm', 'multi agent'],
        'healthcare': ['healthcare', 'medical', 'fhir', 'health'],
        'architecture': ['architecture', 'pattern', 'design', 'clean architecture']
    }

    for category, keywords in categories.items():
        print(f'\n📂 {category.upper()} 相关项目:')
        relevant_projects = []

        for project in data:
            name_desc = (project['name'] + ' ' + project.get('description', '')).lower()
            if any(keyword in name_desc for keyword in keywords):
                relevant_projects.append(project)

        # 按评分排序，取前5个
        relevant_projects.sort(key=lambda x: x['score'], reverse=True)
        for i, project in enumerate(relevant_projects[:5], 1):
            print(f'  {i}. {project["name"]} (⭐{project["stars"]}) - {project["recommendation"]}')
            print(f'     {project["description"][:80]}...')
            print(f'     语言: {project["language"] or "多语言"}, 许可: {project["license"]}')
            print()

    # 总体统计
    print('\n📊 总体统计:')
    print(f'总项目数: {len(data)}')

    recommendations = {}
    for item in data:
        rec = item.get('recommendation', '未知')
        recommendations[rec] = recommendations.get(rec, 0) + 1

    for rec, count in recommendations.items():
        print(f'{rec}: {count}个项目')

    # 按语言统计
    print('\n💻 编程语言分布:')
    languages = {}
    for item in data:
        lang = item.get('language') or '多语言'
        languages[lang] = languages.get(lang, 0) + 1

    sorted_langs = sorted(languages.items(), key=lambda x: x[1], reverse=True)
    for lang, count in sorted_langs[:10]:
        print(f'{lang}: {count}个项目')

if __name__ == "__main__":
    analyze_results()