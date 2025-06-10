# 索克生活 UI 组件库

这是索克生活项目的统一UI组件库，提供了一套完整、一致、可复用的React Native组件。

## 设计理念

- **一致性**: 统一的设计语言和视觉风格
- **可复用性**: 高度可配置的组件，适应不同场景
- **可维护性**: 清晰的代码结构和完整的类型定义
- **可扩展性**: 易于扩展和自定义的组件架构
- **中医特色**: 融入中医文化元素和健康管理特色

## 组件分类

### 基础组件

#### Button - 按钮组件

支持多种变体、尺寸和状态的按钮组件。

```tsx
import { Button } from '../components/ui';

<Button variant="primary" size="medium" title="确认" onPress={() => {}} />;
```

**属性:**

- `variant`: 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger'
- `size`: 'small' | 'medium' | 'large'
- `disabled`: boolean
- `loading`: boolean

#### Text - 文本组件

语义化的文本组件，支持多种预设样式。

```tsx
import { Text } from '../components/ui';

<Text variant="h1">标题</Text>
<Text variant="body1">正文内容</Text>
```

**属性:**

- `variant`: 'h1' | 'h2' | 'h3' | 'h4' | 'h5' | 'h6' | 'body1' | 'body2' | 'caption' | 'overline'
- `color`: string
- `align`: 'left' | 'center' | 'right'

#### Input - 输入框组件

功能完整的输入框组件，支持多种类型和验证。

```tsx
import { Input } from '../components/ui';

<Input
  label="用户名"
  placeholder="请输入用户名"
  value={value}
  onChangeText={setValue}
  type="text"
  variant="outlined"
/>;
```

**属性:**

- `type`: 'text' | 'password' | 'email' | 'number' | 'phone'
- `variant`: 'outlined' | 'filled' | 'underlined'
- `label`: string
- `helperText`: string
- `error`: boolean

#### Card - 卡片组件

灵活的卡片容器组件。

```tsx
import { Card } from '../components/ui';

<Card variant="elevated" onPress={() => {}}>
  <Text>卡片内容</Text>
</Card>;
```

**属性:**

- `variant`: 'elevated' | 'outlined' | 'filled' | 'flat'
- `onPress`: function

#### Container - 容器组件

布局容器组件，支持flexbox属性。

```tsx
import { Container } from '../components/ui';

<Container padding="lg" direction="row" justify="center">
  <Text>内容</Text>
</Container>;
```

#### Avatar - 头像组件

支持图片、文字、占位符的头像组件。

```tsx
import { Avatar } from '../components/ui';

<Avatar
  size="medium"
  source={{ uri: 'https://example.com/avatar.jpg' }}
/>
<Avatar size="large" name="张三" />
```

### 表单组件

#### Switch - 开关组件

用于切换状态的开关组件。

```tsx
import { Switch } from '../components/ui';

<Switch
  value={enabled}
  onValueChange={setEnabled}
  label="启用通知"
  description="接收健康提醒和建议"
/>;
```

**属性:**

- `value`: boolean
- `onValueChange`: (value: boolean) => void
- `size`: 'small' | 'medium' | 'large'
- `disabled`: boolean
- `label`: string
- `description`: string

#### Checkbox - 复选框组件

用于多选操作的复选框组件。

```tsx
import { Checkbox } from '../components/ui';

<Checkbox
  checked={agreed}
  onPress={setAgreed}
  label="同意用户协议"
  description="我已阅读并同意《用户服务协议》"
/>;
```

**属性:**

- `checked`: boolean
- `onPress`: (checked: boolean) => void
- `size`: 'small' | 'medium' | 'large'
- `disabled`: boolean
- `indeterminate`: boolean
- `label`: string
- `description`: string

#### Radio - 单选框组件

用于单选操作的单选框组件。

```tsx
import { Radio } from '../components/ui';

<Radio
  selected={value === 'option1'}
  onPress={() => setValue('option1')}
  label="选项一"
  description="这是第一个选项"
/>;
```

**属性:**

- `selected`: boolean
- `onPress`: () => void
- `value`: string | number
- `size`: 'small' | 'medium' | 'large'
- `disabled`: boolean
- `label`: string
- `description`: string

#### Slider - 滑块组件

用于数值选择的滑块组件。

```tsx
import { Slider } from '../components/ui';

<Slider
  value={healthScore}
  onValueChange={setHealthScore}
  minimumValue={0}
  maximumValue={100}
  step={1}
  label="健康指数"
  showValue
/>;
```

**属性:**

- `value`: number
- `onValueChange`: (value: number) => void
- `minimumValue`: number
- `maximumValue`: number
- `step`: number
- `label`: string
- `showValue`: boolean

### 反馈组件

#### Badge - 徽章组件

用于显示数字、状态或标签的徽章组件。

```tsx
import { Badge } from '../components/ui';

<Badge variant="primary" count={5} />
<Badge variant="error" dot />
<Badge variant="success">NEW</Badge>
```

**属性:**

- `variant`: 'primary' | 'secondary' | 'success' | 'warning' | 'error' | 'default'
- `count`: number
- `dot`: boolean
- `children`: string

#### Loading - 加载组件

显示加载状态的组件。

```tsx
import { Loading } from '../components/ui';

<Loading text="正在加载..." />
<Loading overlay />
```

**属性:**

- `text`: string
- `overlay`: boolean

#### Modal - 模态框组件

模态对话框组件。

```tsx
import { Modal } from '../components/ui';

<Modal
  visible={visible}
  onClose={() => setVisible(false)}
  size="medium"
  position="center"
>
  <Text>模态框内容</Text>
</Modal>;
```

**属性:**

- `visible`: boolean
- `onClose`: () => void
- `size`: 'small' | 'medium' | 'large' | 'fullscreen'
- `position`: 'center' | 'bottom' | 'top'

### 特色组件

#### AgentAvatar - 智能体头像

为四个智能体（小艾、小克、老克、索儿）提供特色头像。

```tsx
import { AgentAvatar } from '../components/ui';

<AgentAvatar agent="xiaoai" size="medium" online={true} />
<AgentAvatar agent="xiaoke" size="large" />
```

**属性:**

- `agent`: 'xiaoai' | 'xiaoke' | 'laoke' | 'soer'
- `size`: 'small' | 'medium' | 'large'
- `online`: boolean

### 布局组件

#### Divider - 分割线组件

用于分隔内容的分割线组件。

```tsx
import { Divider } from '../components/ui';

<Divider margin="md" />
<Divider text="或者" margin="lg" />
<Divider orientation="vertical" />
```

**属性:**

- `orientation`: 'horizontal' | 'vertical'
- `margin`: 'xs' | 'sm' | 'md' | 'lg' | 'xl'
- `text`: string

## 主题系统

组件库基于统一的主题系统，包含：

- **颜色系统**: 主色调、辅助色、功能色、中性色
- **字体系统**: 字体大小、行高、字重
- **间距系统**: 统一的间距规范
- **圆角系统**: 一致的圆角设置
- **阴影系统**: 层次感的阴影效果

## 使用方式

### 单个导入

```tsx
import { Button, Text, Input } from '../components/ui';
```

### 类型导入

```tsx
import { ButtonProps, TextProps } from '../components/ui';
```

## 开发指南

### 添加新组件

1. 在 `src/components/ui/` 目录下创建组件文件
2. 定义完整的 TypeScript 接口
3. 实现组件逻辑
4. 在 `index.ts` 中导出组件和类型
5. 添加单元测试
6. 更新文档

### 样式规范

- 使用主题系统中的设计令牌
- 保持一致的命名规范
- 支持自定义样式覆盖
- 考虑无障碍访问性

### 测试要求

- 每个组件都应有对应的单元测试
- 测试覆盖基本功能、属性变化、事件处理
- 使用 `@testing-library/react-native` 进行测试

## 最佳实践

1. **组件设计**: 遵循单一职责原则，保持组件功能聚焦
2. **属性设计**: 提供合理的默认值，支持必要的自定义
3. **性能优化**: 避免不必要的重渲染，合理使用 memo
4. **无障碍性**: 提供适当的 accessibility 属性
5. **文档完善**: 保持代码注释和使用示例的完整性

## 版本历史

### v1.1.0 (当前版本)

- ✅ 新增 Switch 开关组件
- ✅ 新增 Checkbox 复选框组件
- ✅ 新增 Radio 单选框组件
- ✅ 新增 Slider 滑块组件
- ✅ 完善表单组件系列
- ✅ 增加组件单元测试
- ✅ 更新 UIShowcase 展示页面

### v1.0.0

- ✅ 基础组件: Button, Text, Input, Card, Container, Avatar
- ✅ 反馈组件: Badge, Loading, Modal
- ✅ 特色组件: AgentAvatar
- ✅ 布局组件: Divider
- ✅ 统一主题系统
- ✅ TypeScript 支持
- ✅ 单元测试框架
