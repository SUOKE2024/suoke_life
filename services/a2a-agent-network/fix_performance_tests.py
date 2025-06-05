#!/usr/bin/env python3

def fix_performance_tests():
    """修复性能测试中的condition字段"""
    file_path = "test/performance/test_load_performance.py"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 移除所有的condition=""参数
    content = content.replace('                condition="",\n', '')
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("已修复性能测试中的condition字段")

if __name__ == "__main__":
    fix_performance_tests() 