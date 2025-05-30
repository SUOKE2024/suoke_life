# 索克生活 UI 改进功能使用指南

## 概述

本指南介绍了索克生活项目中新实现的UI改进功能，包括主题系统、无障碍功能、动画系统、响应式设计等。这些功能旨在提供现代化、无障碍、响应式的用户界面体验。

## 功能特性

### 🎨 主题系统

#### 特点
- 支持浅色和暗黑模式
- 融入中医特色的五行色彩系统
- 自动跟随系统主题或手动切换
- 持久化主题偏好设置

#### 使用方法

```tsx
import { useTheme } from '../contexts/ThemeContext';

const MyComponent = () => {
  const { theme, isDark, toggleTheme } = useTheme();
  
  return (
    <View style={{ backgroundColor: theme.colors.surface }}>
      <Text style={{ color: theme.colors.onSurface }}>
        当前主题: {isDark ? '暗黑模式' : '浅色模式'}
      </Text>
    </View>
  );
};
```

#### 中医特色色彩
- 木 (Wood): 绿色 - 代表生命力和成长
- 火 (Fire): 红色 - 代表活力和热情
- 土 (Earth): 黄色 - 代表稳定和平衡
- 金 (Metal): 灰色 - 代表坚韧和精确
- 水 (Water): 蓝色 - 代表流动和智慧

### ♿ 无障碍功能

#### 特点
- 完整的屏幕阅读器支持
- 高对比度模式
- 大字体模式和字体缩放
- 减少动画选项
- 语音导航和播报
- 触觉反馈
- 焦点指示器
- 符合WCAG标准

#### 使用方法

```tsx
import { useAccessibility } from '../contexts/AccessibilityContext';

const MyComponent = () => {
  const { 
    config, 
    updateConfig, 
    announceForAccessibility, 
    triggerHapticFeedback 
  } = useAccessibility();
  
  const handleAction = () => {
    // 触觉反馈
    triggerHapticFeedback('success');
    
    // 语音公告
    announceForAccessibility('操作已完成');
  };
  
  return (
    <TouchableOpacity
      onPress={handleAction}
      accessible={true}
      accessibilityLabel="执行操作"
      accessibilityHint="双击执行操作"
      accessibilityRole="button"
    >
      <Text>点击我</Text>
    </TouchableOpacity>
  );
};
```

### 🎬 动画系统

#### 特点
- 丰富的预定义动画效果
- 支持原生驱动优化
- 性能监控和优化
- 手势动画支持
- 页面转场动画

#### 使用方法

```tsx
import { animations, createAnimatedValue } from '../utils/animations';

const MyComponent = () => {
  const fadeValue = useRef(createAnimatedValue(0)).current;
  
  useEffect(() => {
    animations.fadeIn(fadeValue).start();
  }, []);
  
  return (
    <Animated.View style={{ opacity: fadeValue }}>
      <Text>淡入动画</Text>
    </Animated.View>
  );
};
```

### 📱 响应式设计

#### 特点
- 多设备适配 (手机、平板、桌面)
- 智能字体缩放
- 断点系统
- 网格布局
- 安全区域处理
- 触摸目标优化

#### 使用方法

```tsx
import { responsive, breakpoints } from '../utils/responsive';

const MyComponent = () => {
  const styles = StyleSheet.create({
    container: {
      padding: responsive.width(16),
      fontSize: responsive.fontSize(16),
    },
    responsiveText: {
      fontSize: breakpoints.isTablet() ? 20 : 16,
    },
  });
  
  return (
    <View style={styles.container}>
      <Text style={styles.responsiveText}>响应式文本</Text>
    </View>
  );
};
```

## 组件使用

### Button 组件

```tsx
import { Button } from '../components/ui';

// 基础用法
<Button
  title="点击我"
  onPress={() => console.log('按钮被点击')}
/>

// 高级用法
<Button
  title="主要按钮"
  variant="primary"
  size="large"
  animationType="bounce"
  hapticFeedback={true}
  accessibilityHint="这是一个主要操作按钮"
  onPress={handlePress}
/>
```

### Text 组件

```tsx
import { Text } from '../components/ui';

// 语义化标题
<Text variant="h1">主标题</Text>
<Text variant="h2">副标题</Text>

// 正文内容
<Text variant="body1">主要正文内容</Text>
<Text variant="body2">次要正文内容</Text>

// 自定义颜色和大小
<Text 
  variant="body1" 
  color="primary" 
  size="lg"
  accessibilityRole="header"
>
  自定义文本
</Text>
```

### ThemeToggle 组件

```tsx
import { ThemeToggle } from '../components/ui';

// 基础主题切换
<ThemeToggle />

// 自定义尺寸和标签
<ThemeToggle 
  size="large" 
  showLabel={true} 
/>
```

### AccessibilityPanel 组件

```tsx
import { AccessibilityPanel } from '../components/ui';

const [showPanel, setShowPanel] = useState(false);

<Modal visible={showPanel} onClose={() => setShowPanel(false)}>
  <AccessibilityPanel onClose={() => setShowPanel(false)} />
</Modal>
```

## 最佳实践

### 1. 主题使用
- 始终使用主题颜色而不是硬编码颜色
- 确保在暗黑模式下的可读性
- 利用中医特色色彩增强品牌识别

### 2. 无障碍设计
- 为所有交互元素提供无障碍标签
- 确保触摸目标至少44x44像素
- 提供清晰的焦点指示器
- 支持键盘导航

### 3. 响应式设计
- 使用响应式工具函数进行尺寸适配
- 考虑不同屏幕尺寸的布局变化
- 确保在各种设备上的可用性

### 4. 动画使用
- 适度使用动画，避免过度装饰
- 考虑用户的减少动画偏好
- 使用原生驱动优化性能

### 5. 性能优化
- 使用memo和useMemo优化渲染
- 避免在动画中使用非原生驱动属性
- 监控内存使用和帧率

## 集成步骤

### 1. 在App.tsx中集成上下文提供者

```tsx
import { ThemeProvider } from './contexts/ThemeContext';
import { AccessibilityProvider } from './contexts/AccessibilityContext';

const App = () => {
  return (
    <ThemeProvider>
      <AccessibilityProvider>
        {/* 你的应用内容 */}
      </AccessibilityProvider>
    </ThemeProvider>
  );
};
```

### 2. 在组件中使用钩子

```tsx
import { useTheme } from './contexts/ThemeContext';
import { useAccessibility } from './contexts/AccessibilityContext';

const MyComponent = () => {
  const { theme } = useTheme();
  const { config } = useAccessibility();
  
  // 使用主题和无障碍配置
};
```

### 3. 导入和使用UI组件

```tsx
import { Button, Text, ThemeToggle } from './components/ui';

const MyScreen = () => {
  return (
    <View>
      <Text variant="h1">欢迎使用索克生活</Text>
      <Button title="开始体验" variant="primary" />
      <ThemeToggle />
    </View>
  );
};
```

## 故障排除

### 常见问题

1. **主题不生效**
   - 确保组件被ThemeProvider包裹
   - 检查是否正确使用useTheme钩子

2. **无障碍功能不工作**
   - 确保组件被AccessibilityProvider包裹
   - 检查设备的无障碍设置

3. **动画性能问题**
   - 检查是否使用了原生驱动
   - 避免在动画中修改布局属性

4. **响应式布局问题**
   - 检查设计稿基准尺寸设置
   - 确保使用响应式工具函数

### 调试技巧

1. 使用React DevTools检查上下文状态
2. 启用动画帧率监控
3. 使用无障碍检查工具验证实现
4. 在不同设备上测试响应式布局

## 更新日志

### v1.0.0 (2024-01-XX)
- ✨ 新增主题系统，支持浅色/暗黑模式
- ✨ 新增完整的无障碍功能支持
- ✨ 新增动画系统和响应式设计工具
- ✨ 升级Button和Text组件
- ✨ 新增ThemeToggle和AccessibilityPanel组件
- 🎨 融入中医特色设计元素
- 📱 优化移动端体验
- ♿ 符合WCAG无障碍标准

## 贡献指南

欢迎为索克生活的UI改进功能贡献代码！请遵循以下指南：

1. 遵循现有的代码风格和架构
2. 确保新功能支持无障碍访问
3. 添加适当的TypeScript类型定义
4. 编写单元测试和集成测试
5. 更新相关文档

## 技术支持

如有问题或建议，请通过以下方式联系：

- 创建GitHub Issue
- 发送邮件至开发团队
- 参与社区讨论

---

**索克生活团队**  
*让健康管理更智能、更人性化* 