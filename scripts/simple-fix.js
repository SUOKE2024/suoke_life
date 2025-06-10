#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

console.log('🚀 开始简化修复...');
console.log('==================================================');

// 创建缺失的组件文件
function createMissingComponents() {
  console.log('🔧 创建缺失的组件文件...');
  
  const missingComponents = [
    {
      path: 'src/screens/main/HomeScreen.tsx',
      content: `import React from 'react';
import { View, Text, StyleSheet } from 'react-native';

const HomeScreen: React.FC = () => {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>首页</Text>
      <Text style={styles.subtitle}>欢迎使用索克生活</Text>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#ffffff',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 10,
  },
  subtitle: {
    fontSize: 16,
    color: '#666666',
  },
});

export default HomeScreen;`
    },
    {
      path: 'src/screens/health/LifeOverviewScreen.tsx',
      content: `import React from 'react';
import { View, Text, StyleSheet } from 'react-native';

const LifeOverviewScreen: React.FC = () => {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>生活概览</Text>
      <Text style={styles.subtitle}>健康数据总览</Text>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#ffffff',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 10,
  },
  subtitle: {
    fontSize: 16,
    color: '#666666',
  },
});

export default LifeOverviewScreen;`
    },
    {
      path: 'src/screens/explore/ExploreScreen.tsx',
      content: `import React from 'react';
import { View, Text, StyleSheet } from 'react-native';

const ExploreScreen: React.FC = () => {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>探索</Text>
      <Text style={styles.subtitle}>发现更多功能</Text>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#ffffff',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 10,
  },
  subtitle: {
    fontSize: 16,
    color: '#666666',
  },
});

export default ExploreScreen;`
    },
    {
      path: 'src/screens/demo/FiveDiagnosisAgentIntegrationScreen.tsx',
      content: `import React from 'react';
import { View, Text, StyleSheet } from 'react-native';

const FiveDiagnosisAgentIntegrationScreen: React.FC = () => {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>五诊智能体集成</Text>
      <Text style={styles.subtitle}>中医五诊法智能诊断</Text>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#ffffff',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 10,
  },
  subtitle: {
    fontSize: 16,
    color: '#666666',
  },
});

export default FiveDiagnosisAgentIntegrationScreen;`
    },
    {
      path: 'src/navigation/BusinessNavigator.tsx',
      content: `import React from 'react';
import { View, Text, StyleSheet } from 'react-native';

const BusinessNavigator: React.FC = () => {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>商业导航</Text>
      <Text style={styles.subtitle}>商业功能模块</Text>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#ffffff',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 10,
  },
  subtitle: {
    fontSize: 16,
    color: '#666666',
  },
});

export default BusinessNavigator;`
    },
    {
      path: 'src/navigation/AgentNavigator.tsx',
      content: `import React from 'react';
import { View, Text, StyleSheet } from 'react-native';

const AgentNavigator: React.FC = () => {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>智能体导航</Text>
      <Text style={styles.subtitle}>AI智能体管理</Text>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#ffffff',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 10,
  },
  subtitle: {
    fontSize: 16,
    color: '#666666',
  },
});

export default AgentNavigator;`
    },
    {
      path: 'src/components/business/BusinessQuickAccess.tsx',
      content: `import React from 'react';
import { View, Text, StyleSheet } from 'react-native';

const BusinessQuickAccess: React.FC = () => {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>商业快速访问</Text>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    padding: 20,
    backgroundColor: '#f5f5f5',
    borderRadius: 10,
    margin: 10,
  },
  title: {
    fontSize: 18,
    fontWeight: 'bold',
    textAlign: 'center',
  },
});

export default BusinessQuickAccess;`
    },
    {
      path: 'src/components/common/GatewayMonitor.tsx',
      content: `import React from 'react';
import { View, Text, StyleSheet } from 'react-native';

const GatewayMonitor: React.FC = () => {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>网关监控</Text>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 20,
    backgroundColor: '#ffffff',
  },
  title: {
    fontSize: 18,
    fontWeight: 'bold',
  },
});

export default GatewayMonitor;`
    },
    {
      path: 'src/components/common/GatewayConfig.tsx',
      content: `import React from 'react';
import { View, Text, StyleSheet } from 'react-native';

const GatewayConfig: React.FC = () => {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>网关配置</Text>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 20,
    backgroundColor: '#ffffff',
  },
  title: {
    fontSize: 18,
    fontWeight: 'bold',
  },
});

export default GatewayConfig;`
    },
    {
      path: 'src/components/common/AnalyticsDashboard.tsx',
      content: `import React from 'react';
import { View, Text, StyleSheet } from 'react-native';

const AnalyticsDashboard: React.FC = () => {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>分析仪表板</Text>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 20,
    backgroundColor: '#ffffff',
  },
  title: {
    fontSize: 18,
    fontWeight: 'bold',
  },
});

export default AnalyticsDashboard;`
    },
    {
      path: 'src/components/common/GatewayConfigManager.tsx',
      content: `import React from 'react';
import { View, Text, StyleSheet } from 'react-native';

const GatewayConfigManager: React.FC = () => {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>网关配置管理</Text>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 20,
    backgroundColor: '#ffffff',
  },
  title: {
    fontSize: 18,
    fontWeight: 'bold',
  },
});

export default GatewayConfigManager;`
    }
  ];
  
  let createdCount = 0;
  missingComponents.forEach(({ path: filePath, content }) => {
    try {
      // 确保目录存在
      const dir = path.dirname(filePath);
      if (!fs.existsSync(dir)) {
        fs.mkdirSync(dir, { recursive: true });
      }
      
      // 如果文件不存在则创建
      if (!fs.existsSync(filePath)) {
        fs.writeFileSync(filePath, content, 'utf8');
        createdCount++;
        console.log(`✅ 创建 ${filePath}`);
      }
    } catch (error) {
      console.log(`❌ 创建文件失败 ${filePath}: ${error.message}`);
    }
  });
  
  console.log(`✅ 创建了 ${createdCount} 个缺失的组件文件`);
}

// 运行Prettier格式化
function runPrettierFix() {
  try {
    console.log('🔧 运行Prettier格式化...');
    execSync('npx prettier --write "src/**/*.{ts,tsx,js,jsx}"', { stdio: 'inherit' });
    console.log('✅ Prettier格式化完成');
  } catch (error) {
    console.log('⚠️ Prettier格式化部分完成');
  }
}

// 运行ESLint自动修复
function runESLintFix() {
  try {
    console.log('🔧 运行ESLint自动修复...');
    execSync('npx eslint src/ --ext .ts,.tsx,.js,.jsx --fix', { stdio: 'inherit' });
    console.log('✅ ESLint自动修复完成');
  } catch (error) {
    console.log('⚠️ ESLint自动修复部分完成');
  }
}

// 主修复流程
function main() {
  console.log('🔧 步骤1: 创建缺失的组件文件...');
  createMissingComponents();
  
  console.log('🔧 步骤2: 运行Prettier格式化...');
  runPrettierFix();
  
  console.log('🔧 步骤3: 运行ESLint自动修复...');
  runESLintFix();
  
  console.log('==================================================');
  console.log('✅ 简化修复完成!');
  console.log('📊 请运行 npm run lint 查看剩余问题');
}

main(); 