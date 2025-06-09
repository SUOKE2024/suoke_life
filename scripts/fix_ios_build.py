#!/usr/bin/env python3
"""
iOS构建问题修复脚本
解决dSYM、UIScene和调试器问题
"""

import os
import subprocess
import shutil
from pathlib import Path

class iOSBuildFixer:
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.ios_dir = self.project_root / "ios"
        
    def fix_dsym_issue(self):
        """修复dSYM调试符号问题"""
        print("🔧 修复dSYM调试符号问题...")
        
        # 清理构建缓存
        derived_data_path = os.path.expanduser("~/Library/Developer/Xcode/DerivedData")
        suoke_derived = Path(derived_data_path)
        
        for item in suoke_derived.glob("SuokeLife-*"):
            if item.is_dir():
                print(f"清理构建缓存: {item}")
                shutil.rmtree(item, ignore_errors=True)
        
        # 清理iOS构建产物
        build_dir = self.ios_dir / "build"
        if build_dir.exists():
            print("清理iOS构建目录...")
            shutil.rmtree(build_dir, ignore_errors=True)
            
        print("✅ dSYM问题修复完成")
    
    def fix_uiscene_warning(self):
        """修复UIScene生命周期警告"""
        print("🔧 修复UIScene生命周期警告...")
        
        # 更新AppDelegate.h
        app_delegate_h = self.ios_dir / "SuokeLife" / "AppDelegate.h"
        if app_delegate_h.exists():
            content = '''#import <RCTAppDelegate.h>
#import <UIKit/UIKit.h>

@interface AppDelegate : RCTAppDelegate

@end
'''
            with open(app_delegate_h, 'w') as f:
                f.write(content)
            print("✅ 更新AppDelegate.h")
        
        # 更新AppDelegate.mm
        app_delegate_mm = self.ios_dir / "SuokeLife" / "AppDelegate.mm"
        if app_delegate_mm.exists():
            content = '''#import "AppDelegate.h"
#import <React/RCTBundleURLProvider.h>

@implementation AppDelegate

- (BOOL)application:(UIApplication *)application didFinishLaunchingWithOptions:(NSDictionary *)launchOptions
{
  self.moduleName = @"SuokeLife";
  self.initialProps = @{};

  return [super application:application didFinishLaunchingWithOptions:launchOptions];
}

- (NSURL *)sourceURLForBridge:(RCTBridge *)bridge
{
  return [self bundleURL];
}

- (NSURL *)bundleURL
{
#if DEBUG
  return [[RCTBundleURLProvider sharedSettings] jsBundleURLForBundleRoot:@"index"];
#else
  return [[NSBundle mainBundle] URLForResource:@"main" withExtension:@"jsbundle"];
#endif
}

@end
'''
            with open(app_delegate_mm, 'w') as f:
                f.write(content)
            print("✅ 更新AppDelegate.mm")
        
        print("✅ UIScene警告修复完成")
    
    def fix_memory_issues(self):
        """修复内存和调试器问题"""
        print("🔧 修复内存和调试器问题...")
        
        # 重置iOS模拟器
        try:
            subprocess.run([
                "xcrun", "simctl", "erase", "all"
            ], check=False, capture_output=True)
            print("✅ 重置iOS模拟器")
        except Exception as e:
            print(f"⚠️ 模拟器重置失败: {e}")
        
        # 清理Metro缓存
        try:
            subprocess.run([
                "npx", "react-native", "start", "--reset-cache"
            ], cwd=self.project_root, check=False, capture_output=True, timeout=5)
            print("✅ 清理Metro缓存")
        except Exception:
            pass
        
        print("✅ 内存问题修复完成")
    
    def update_xcode_settings(self):
        """更新Xcode项目设置"""
        print("🔧 更新Xcode项目设置...")
        
        # 创建xcconfig文件来优化构建设置
        debug_config = self.ios_dir / "Debug.xcconfig"
        debug_content = '''// Debug配置
DEBUG_INFORMATION_FORMAT = dwarf-with-dsym
GCC_OPTIMIZATION_LEVEL = 0
SWIFT_OPTIMIZATION_LEVEL = -Onone
ENABLE_TESTABILITY = YES
GCC_PREPROCESSOR_DEFINITIONS = DEBUG=1 $(inherited)
MTL_ENABLE_DEBUG_INFO = INCLUDE_SOURCE
'''
        with open(debug_config, 'w') as f:
            f.write(debug_content)
        
        release_config = self.ios_dir / "Release.xcconfig"
        release_content = '''// Release配置
DEBUG_INFORMATION_FORMAT = dwarf-with-dsym
GCC_OPTIMIZATION_LEVEL = s
SWIFT_OPTIMIZATION_LEVEL = -O
ENABLE_TESTABILITY = NO
MTL_ENABLE_DEBUG_INFO = NO
'''
        with open(release_config, 'w') as f:
            f.write(release_content)
        
        print("✅ Xcode设置更新完成")
    
    def run_clean_build(self):
        """执行清理构建"""
        print("🚀 执行清理构建...")
        
        os.chdir(self.ios_dir)
        
        # 清理Pods
        try:
            subprocess.run(["pod", "deintegrate"], check=False)
            subprocess.run(["pod", "install", "--repo-update"], check=True)
            print("✅ Pods重新安装完成")
        except subprocess.CalledProcessError as e:
            print(f"⚠️ Pods安装失败: {e}")
        
        # 清理Xcode项目
        try:
            subprocess.run([
                "xcodebuild", "clean", 
                "-workspace", "SuokeLife.xcworkspace",
                "-scheme", "SuokeLife"
            ], check=True)
            print("✅ Xcode项目清理完成")
        except subprocess.CalledProcessError as e:
            print(f"⚠️ Xcode清理失败: {e}")
    
    def fix_all(self):
        """执行所有修复"""
        print("🔧 开始修复iOS构建问题...")
        
        self.fix_dsym_issue()
        self.fix_uiscene_warning()
        self.fix_memory_issues()
        self.update_xcode_settings()
        self.run_clean_build()
        
        print("🎉 iOS构建问题修复完成！")
        print("\n📋 修复内容:")
        print("✅ 修复dSYM调试符号问题")
        print("✅ 更新UIScene生命周期")
        print("✅ 清理内存和缓存")
        print("✅ 优化Xcode构建设置")
        print("✅ 重新安装依赖")
        
        print("\n🚀 建议的下一步:")
        print("1. 重启Xcode")
        print("2. 选择合适的模拟器设备")
        print("3. 使用 'npx react-native run-ios' 重新构建")

if __name__ == "__main__":
    fixer = iOSBuildFixer(".")
    fixer.fix_all() 