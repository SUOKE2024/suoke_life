# Input 输入框组件

## 概述
Input 是一个核心的输入框组件，为 SuoKe Life 应用提供可定制的文本输入功能。它在 Flutter 基础输入能力的基础上扩展了应用所需的特定功能。

## 功能特性
- 支持主题定制的文本输入
- 输入验证和错误处理
- 支持多种输入类型（文本、数字、密码等）
- 可选的前缀和后缀图标
- 支持标签和占位文本
- 错误信息显示
- 字符计数支持

## 使用示例

### 基础用法

```dart
// 基础用法
AppInput(
  label: '用户名',
  hint: '请输入用户名',
  onChanged: (value) {
    print('输入内容: $value');
  },
)

// 密码输入
AppInput(
  label: '密码',
  obscureText: true,
  suffix: IconButton(
    icon: Icon(Icons.visibility),
    onPressed: () {
      // 切换密码显示/隐藏
    },
  ),
)

// 多行输入
AppInput(
  maxLines: 5,
  hint: '请输入备注',
)

// 带验证的输入
AppInput(
  label: '手机号',
  keyboardType: TextInputType.phone,
  maxLength: 11,
  inputFormatters: [
    FilteringTextInputFormatter.digitsOnly,
  ],
  error: '请输入正确的手机号',
)
```

## API

### 属性

| 参数 | 说明 | 类型 | 默认值 |
|------|------|------|--------|
| controller | 控制器 | TextEditingController? | - |
| label | 标签文本 | String? | - |
| hint | 提示文本 | String? | - |
| helper | 帮助文本 | String? | - |
| error | 错误文本 | String? | - |
| obscureText | 是否密码输入 | bool | false |
| maxLines | 最大行数 | int? | 1 |
| enabled | 是否可用 | bool | true |
| prefix | 前缀图标 | Widget? | - |
| suffix | 后缀图标 | Widget? | - |

### 事件

| 名称 | 说明 | 类型 |
|------|------|------|
| onChanged | 输入内容变化时触发 | ValueChanged<String>? |
| onSubmitted | 提交时触发 | ValueChanged<String>? |
| onTap | 点击时触发 | GestureTapCallback? |

### 样式

| 参数 | 说明 | 类型 | 默认值 |
|------|------|------|--------|
| style | 输入文本样式 | TextStyle? | - |
| contentPadding | 内容内边距 | EdgeInsets? | - |
| borderRadius | 边框圆角 | double? | 4 |
| fillColor | 填充颜色 | Color? | - |