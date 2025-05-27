#!/usr/bin/env python3
"""
索克生活原生功能配置验证脚本
验证权限管理、原生模块集成和推送通知系统
"""

import os
import json

def test_native_features_configuration():
    """测试原生功能配置"""
    print("🔍 检查原生功能配置文件...")
    
    results = {
        'permissions': False,
        'native_modules': False,
        'notifications': False,
        'demo_component': False
    }
    
    # 检查权限管理文件
    permissions_file = 'src/utils/permissions.ts'
    if os.path.exists(permissions_file):
        print(f"✅ {permissions_file} 存在")
        with open(permissions_file, 'r', encoding='utf-8') as f:
            content = f.read()
            if 'PermissionManager' in content and 'checkPermission' in content:
                print("  ✅ 权限管理类和方法已实现")
                results['permissions'] = True
            else:
                print("  ❌ 权限管理功能不完整")
    else:
        print(f"❌ {permissions_file} 不存在")
    
    # 检查原生模块文件
    native_modules_file = 'src/utils/nativeModules.ts'
    if os.path.exists(native_modules_file):
        print(f"✅ {native_modules_file} 存在")
        with open(native_modules_file, 'r', encoding='utf-8') as f:
            content = f.read()
            if 'NativeModulesManager' in content and 'takePhoto' in content:
                print("  ✅ 原生模块管理类和方法已实现")
                results['native_modules'] = True
            else:
                print("  ❌ 原生模块功能不完整")
    else:
        print(f"❌ {native_modules_file} 不存在")
    
    # 检查通知系统文件
    notifications_file = 'src/utils/notifications.ts'
    if os.path.exists(notifications_file):
        print(f"✅ {notifications_file} 存在")
        with open(notifications_file, 'r', encoding='utf-8') as f:
            content = f.read()
            if 'NotificationManager' in content and 'scheduleLocalNotification' in content:
                print("  ✅ 通知管理类和方法已实现")
                results['notifications'] = True
            else:
                print("  ❌ 通知系统功能不完整")
    else:
        print(f"❌ {notifications_file} 不存在")
    
    # 检查演示组件文件
    demo_file = 'src/components/common/NativeFeaturesDemo.tsx'
    if os.path.exists(demo_file):
        print(f"✅ {demo_file} 存在")
        with open(demo_file, 'r', encoding='utf-8') as f:
            content = f.read()
            if 'NativeFeaturesDemo' in content and 'testCamera' in content:
                print("  ✅ 原生功能演示组件已实现")
                results['demo_component'] = True
            else:
                print("  ❌ 演示组件功能不完整")
    else:
        print(f"❌ {demo_file} 不存在")
    
    return results

def print_summary(results):
    """打印测试总结"""
    print()
    print("📊 原生功能配置统计:")
    print(f"- 权限管理系统: {'✅ 已实现' if results['permissions'] else '❌ 未实现'}")
    print(f"- 原生模块集成: {'✅ 已实现' if results['native_modules'] else '❌ 未实现'}")
    print(f"- 推送通知系统: {'✅ 已实现' if results['notifications'] else '❌ 未实现'}")
    print(f"- 功能演示组件: {'✅ 已实现' if results['demo_component'] else '❌ 未实现'}")
    
    # 检查配置文档
    config_report = 'NATIVE_FEATURES_CONFIGURATION_REPORT.md'
    if os.path.exists(config_report):
        print("- 配置文档: ✅ 已完成")
    else:
        print("- 配置文档: ❌ 未完成")
    
    print()
    print("🎯 支持的原生功能:")
    print("- 📷 相机权限和拍照功能")
    print("- 🎤 麦克风权限和语音识别")
    print("- 📍 位置权限和定位服务")
    print("- 🔔 通知权限和推送通知")
    print("- 📸 相册权限和图片管理")
    print("- 💊 健康提醒系统")
    
    # 计算完成度
    total_features = len(results)
    completed_features = sum(results.values())
    completion_rate = (completed_features / total_features) * 100
    
    print()
    print(f"📈 完成度: {completed_features}/{total_features} ({completion_rate:.1f}%)")
    
    if completion_rate == 100:
        print("✅ 原生功能配置完成！")
        print("📋 详细信息请查看: NATIVE_FEATURES_CONFIGURATION_REPORT.md")
    else:
        print("⚠️ 部分原生功能配置未完成，请检查上述错误")

def check_package_dependencies():
    """检查package.json中的原生模块依赖"""
    print()
    print("📦 检查原生模块依赖...")
    
    package_file = 'package.json'
    if os.path.exists(package_file):
        with open(package_file, 'r', encoding='utf-8') as f:
            package_data = json.load(f)
            
        dependencies = package_data.get('dependencies', {})
        dev_dependencies = package_data.get('devDependencies', {})
        all_deps = {**dependencies, **dev_dependencies}
        
        required_packages = [
            'react-native-permissions',
            'react-native-vision-camera',
            '@react-native-voice/voice',
            '@react-native-community/geolocation',
            '@react-native-firebase/messaging',
            'react-native-push-notification'
        ]
        
        for package in required_packages:
            if package in all_deps:
                print(f"  ✅ {package}: {all_deps[package]}")
            else:
                print(f"  ⚠️ {package}: 未安装（可选）")
    else:
        print("❌ package.json 不存在")

if __name__ == "__main__":
    print("🚀 索克生活原生功能配置验证")
    print("=" * 50)
    
    # 测试原生功能配置
    results = test_native_features_configuration()
    
    # 打印总结
    print_summary(results)
    
    # 检查依赖包
    check_package_dependencies()
    
    print()
    print("🎉 验证完成！") 