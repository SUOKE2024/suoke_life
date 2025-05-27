#!/usr/bin/env python3
"""
测试智能体对话系统UI集成
验证四个智能体（小艾、小克、老克、索儿）的对话功能是否正确集成到各个频道
"""

import os
import re
import sys
from pathlib import Path

def check_file_exists(file_path):
    """检查文件是否存在"""
    return os.path.exists(file_path)

def check_import_in_file(file_path, import_statement):
    """检查文件中是否包含特定的导入语句"""
    if not check_file_exists(file_path):
        return False
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        return import_statement in content

def check_component_usage(file_path, component_name, agent_type=None):
    """检查文件中是否正确使用了组件"""
    if not check_file_exists(file_path):
        return False
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
        # 检查组件是否被使用
        component_pattern = f'<{component_name}'
        if component_pattern not in content:
            return False
        
        # 如果指定了智能体类型，检查agentType属性
        if agent_type:
            agent_pattern = f'agentType="{agent_type}"'
            return agent_pattern in content
        
        return True

def check_state_variable(file_path, variable_name):
    """检查文件中是否定义了状态变量"""
    if not check_file_exists(file_path):
        return False
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        # 检查useState定义
        pattern = f'const \\[{variable_name}.*useState'
        return bool(re.search(pattern, content))

def test_agent_chat_integration():
    """测试智能体对话系统集成"""
    print("🤖 测试智能体对话系统UI集成...")
    print("=" * 60)
    
    # 测试结果
    results = {
        'AgentChatInterface组件': False,
        'ContactsList组件': False,
        'HomeScreen集成': False,
        'ExploreScreen集成': False,
        'LifeScreen集成': False,
        'SuokeScreen集成': False,
    }
    
    # 1. 检查AgentChatInterface组件
    print("\n1. 检查AgentChatInterface组件...")
    agent_chat_path = "src/components/common/AgentChatInterface.tsx"
    if check_file_exists(agent_chat_path):
        print(f"   ✅ {agent_chat_path} 存在")
        results['AgentChatInterface组件'] = True
    else:
        print(f"   ❌ {agent_chat_path} 不存在")
    
    # 2. 检查ContactsList组件
    print("\n2. 检查ContactsList组件...")
    contacts_path = "src/components/common/ContactsList.tsx"
    if check_file_exists(contacts_path):
        print(f"   ✅ {contacts_path} 存在")
        results['ContactsList组件'] = True
    else:
        print(f"   ❌ {contacts_path} 不存在")
    
    # 3. 检查HomeScreen集成（小艾）
    print("\n3. 检查HomeScreen集成（小艾）...")
    home_path = "src/screens/main/HomeScreen.tsx"
    home_checks = [
        check_import_in_file(home_path, "AgentChatInterface"),
        check_import_in_file(home_path, "ContactsList"),
        check_state_variable(home_path, "agentChatVisible"),
        check_component_usage(home_path, "AgentChatInterface"),
        check_component_usage(home_path, "ContactsList")
    ]
    
    if all(home_checks):
        print("   ✅ HomeScreen集成完成")
        results['HomeScreen集成'] = True
    else:
        print("   ❌ HomeScreen集成不完整")
        print(f"      导入AgentChatInterface: {'✅' if home_checks[0] else '❌'}")
        print(f"      导入ContactsList: {'✅' if home_checks[1] else '❌'}")
        print(f"      状态变量agentChatVisible: {'✅' if home_checks[2] else '❌'}")
        print(f"      使用AgentChatInterface: {'✅' if home_checks[3] else '❌'}")
        print(f"      使用ContactsList: {'✅' if home_checks[4] else '❌'}")
    
    # 4. 检查ExploreScreen集成（老克）
    print("\n4. 检查ExploreScreen集成（老克）...")
    explore_path = "src/screens/explore/ExploreScreen.tsx"
    explore_checks = [
        check_import_in_file(explore_path, "AgentChatInterface"),
        check_state_variable(explore_path, "agentChatVisible"),
        check_component_usage(explore_path, "AgentChatInterface", "laoke")
    ]
    
    if all(explore_checks):
        print("   ✅ ExploreScreen集成完成")
        results['ExploreScreen集成'] = True
    else:
        print("   ❌ ExploreScreen集成不完整")
        print(f"      导入AgentChatInterface: {'✅' if explore_checks[0] else '❌'}")
        print(f"      状态变量agentChatVisible: {'✅' if explore_checks[1] else '❌'}")
        print(f"      使用AgentChatInterface(laoke): {'✅' if explore_checks[2] else '❌'}")
    
    # 5. 检查LifeScreen集成（索儿）
    print("\n5. 检查LifeScreen集成（索儿）...")
    life_path = "src/screens/life/LifeScreen.tsx"
    life_checks = [
        check_import_in_file(life_path, "AgentChatInterface"),
        check_state_variable(life_path, "soerChatVisible"),
        check_component_usage(life_path, "AgentChatInterface", "soer")
    ]
    
    if all(life_checks):
        print("   ✅ LifeScreen集成完成")
        results['LifeScreen集成'] = True
    else:
        print("   ❌ LifeScreen集成不完整")
        print(f"      导入AgentChatInterface: {'✅' if life_checks[0] else '❌'}")
        print(f"      状态变量soerChatVisible: {'✅' if life_checks[1] else '❌'}")
        print(f"      使用AgentChatInterface(soer): {'✅' if life_checks[2] else '❌'}")
    
    # 6. 检查SuokeScreen集成（小克）
    print("\n6. 检查SuokeScreen集成（小克）...")
    suoke_path = "src/screens/suoke/SuokeScreen.tsx"
    suoke_checks = [
        check_import_in_file(suoke_path, "AgentChatInterface"),
        check_state_variable(suoke_path, "xiaokeChatVisible"),
        check_component_usage(suoke_path, "AgentChatInterface", "xiaoke")
    ]
    
    if all(suoke_checks):
        print("   ✅ SuokeScreen集成完成")
        results['SuokeScreen集成'] = True
    else:
        print("   ❌ SuokeScreen集成不完整")
        print(f"      导入AgentChatInterface: {'✅' if suoke_checks[0] else '❌'}")
        print(f"      状态变量xiaokeChatVisible: {'✅' if suoke_checks[1] else '❌'}")
        print(f"      使用AgentChatInterface(xiaoke): {'✅' if suoke_checks[2] else '❌'}")
    
    # 总结
    print("\n" + "=" * 60)
    print("📊 智能体对话系统集成测试结果:")
    print("=" * 60)
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    
    for test_name, passed in results.items():
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"   {test_name}: {status}")
    
    print(f"\n总体进度: {passed_tests}/{total_tests} ({passed_tests/total_tests*100:.1f}%)")
    
    if passed_tests == total_tests:
        print("\n🎉 所有智能体对话系统集成测试通过！")
        print("\n智能体分布:")
        print("   🏠 Home频道: 小艾 (xiaoai) - 健康诊断与建议")
        print("   🔍 Explore频道: 老克 (laoke) - 中医养生教育")
        print("   🏥 SUOKE频道: 小克 (xiaoke) - 医疗服务管理")
        print("   🌱 LIFE频道: 索儿 (soer) - 生活方式指导")
        return True
    else:
        print(f"\n⚠️  还有 {total_tests - passed_tests} 个测试未通过，需要继续完善")
        return False

if __name__ == "__main__":
    success = test_agent_chat_integration()
    sys.exit(0 if success else 1)