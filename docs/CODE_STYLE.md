# 索克生活项目代码风格规范

本文档定义了索克生活项目的代码风格和规范。所有参与项目开发的贡献者都应遵循这些规范，以保持代码库的一致性和可维护性。

## 目录

- [JavaScript/TypeScript规范](#javascripttypescript规范)
- [React/React Native规范](#reactreact-native规范)
- [CSS/样式规范](#css样式规范)
- [命名规范](#命名规范)
- [文件组织规范](#文件组织规范)
- [注释规范](#注释规范)
- [Git提交规范](#git提交规范)

## JavaScript/TypeScript规范

### 基本规则

- 使用TypeScript开发所有新功能
- 使用ES6+语法特性
- 使用2个空格缩进
- 行末不加分号
- 每行最大长度为100个字符
- 使用单引号`'`作为字符串默认引号风格
- 优先使用模板字符串进行字符串拼接
- 使用`===`和`!==`代替`==`和`!=`
- 所有变量声明使用`const`或`let`，禁止使用`var`
- 每个文件末尾保留一个空行

### TypeScript规则

- 为所有导出的函数、类和接口编写类型定义
- 为函数参数和返回值添加类型注解
- 使用接口`interface`定义对象类型，使用类型别名`type`定义联合类型或交叉类型
- 避免使用`any`类型，必要时使用`unknown`
- 使用明确的可选属性标记`?`而不是联合类型`| undefined`
- 使用类型推断，减少冗余的类型注解
- 对于React组件的props和state，使用接口定义

### 示例

```typescript
// 好的例子
interface User {
  id: string;
  name: string;
  email?: string;
  age: number;
}

const getFullName = (user: User): string => {
  return `${user.name} (${user.id})`;
};

// 避免的例子
var getName = function(user) {
  return user.name + " (" + user.id + ")";
};
```

## React/React Native规范

### 组件编写

- 使用函数组件和React Hooks，避免使用类组件
- 每个文件只导出一个组件
- 组件文件名与组件名保持一致，使用PascalCase
- 为组件props定义明确的接口
- 使用解构获取props和state
- 使用React.memo优化渲染性能
- 使用useMemo和useCallback优化引用稳定性

### 钩子(Hooks)使用

- 遵循Hook使用规则，不在条件或循环中调用Hook
- 自定义Hook名称以`use`开头
- 相关的状态Hook应组合在一起
- 使用useReducer处理复杂的状态逻辑

### 组件结构

```typescript
// UserProfile.tsx
import React, { useState, useCallback } from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { Button } from 'components/common';
import { useUser } from 'hooks';
import { User } from 'types';

interface UserProfileProps {
  userId: string;
  onEdit?: () => void;
}

export const UserProfile: React.FC<UserProfileProps> = ({ userId, onEdit }) => {
  const { user, loading } = useUser(userId);
  const [isExpanded, setIsExpanded] = useState(false);
  
  const handleToggle = useCallback(() => {
    setIsExpanded(prev => !prev);
  }, []);
  
  if (loading) {
    return <Text>Loading...</Text>;
  }
  
  return (
    <View style={styles.container}>
      <Text style={styles.name}>{user.name}</Text>
      {isExpanded && (
        <View style={styles.details}>
          <Text>{user.email}</Text>
          <Text>{user.bio}</Text>
        </View>
      )}
      <Button onPress={handleToggle}>
        {isExpanded ? 'Show Less' : 'Show More'}
      </Button>
      {onEdit && (
        <Button onPress={onEdit}>
          Edit Profile
        </Button>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    padding: 16,
    backgroundColor: '#fff',
    borderRadius: 8,
  },
  name: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 8,
  },
  details: {
    marginTop: 8,
    marginBottom: 16,
  },
});
```

## CSS/样式规范

### React Native样式

- 使用StyleSheet.create创建样式对象
- 样式属性按照类型分组：布局、尺寸、边距、颜色、字体等
- 样式对象的属性名使用camelCase
- 共享样式放在独立文件中
- 尽量避免内联样式
- 遵循8像素网格系统
- 使用应用主题中定义的颜色、字体大小等常量

### 样式组织

```typescript
// 推荐的样式组织
const styles = StyleSheet.create({
  container: {
    // 位置和布局
    position: 'relative',
    flexDirection: 'column',
    alignItems: 'center',
    
    // 尺寸
    width: '100%',
    height: 200,
    
    // 边距和填充
    margin: 16,
    padding: 8,
    
    // 边框和圆角
    borderRadius: 8,
    borderWidth: 1,
    
    // 颜色和背景
    backgroundColor: '#ffffff',
    borderColor: '#e0e0e0',
  },
  title: {
    // 字体和文本
    fontSize: 18,
    fontWeight: 'bold',
    textAlign: 'center',
    color: '#333333',
    marginBottom: 8,
  },
});
```

## 命名规范

### 通用命名原则

- 使用有意义的、描述性的名称
- 避免使用单字母变量名(除了循环索引或临时变量)
- 避免使用缩写(除非是普遍接受的缩写)
- 避免使用过长的名称

### 特定命名规范

- **组件名称**: 使用PascalCase，如`UserProfile`
- **函数名称**: 使用camelCase，如`getUserData`
- **变量名称**: 使用camelCase，如`userData`
- **常量名称**: 使用全大写下划线分隔，如`API_URL`
- **接口名称**: 使用PascalCase，通常不加前缀，如`User`
- **类型别名**: 使用PascalCase，如`UserResponse`
- **枚举名称**: 使用PascalCase，如`UserRole`
- **枚举值**: 使用PascalCase，如`Admin`

### 命名约定

- **布尔值**: 使用`is`、`has`、`can`等前缀，如`isLoading`, `hasError`
- **事件处理函数**: 使用`handle`前缀，如`handleSubmit`, `handleChange`
- **自定义钩子**: 使用`use`前缀，如`useAuth`, `useFormValidation`
- **异步函数**: 通常使用`fetch`、`get`、`load`等前缀，如`fetchUserData`
- **包装组件**: 使用`with`前缀，如`withAuth`
- **CRUD操作**: 使用`create`、`get`、`update`、`delete`等前缀

## 文件组织规范

### 目录结构

- 相关的文件应该放在同一目录下
- 按功能/业务领域组织文件，而不是按文件类型
- 组件、样式、测试和相关文件应该放在一起
- 公共组件放在`components/common`目录下
- 特性相关组件放在`features/<feature-name>/components`目录下

### 文件命名

- 组件文件: PascalCase，如`UserProfile.tsx`
- 非组件文件: camelCase，如`apiService.ts`
- 测试文件: 原文件名加`.test`或`.spec`，如`UserProfile.test.tsx`
- 样式文件: 原文件名加`.styles`，如`UserProfile.styles.ts`
- 类型定义文件: 原文件名加`.types`，如`UserProfile.types.ts`

### 目录结构示例

```
src/
├── features/
│   ├── auth/
│   │   ├── components/
│   │   │   ├── LoginForm.tsx
│   │   │   ├── LoginForm.test.tsx
│   │   │   └── RegistrationForm.tsx
│   │   ├── hooks/
│   │   │   └── useAuth.ts
│   │   ├── services/
│   │   │   └── authService.ts
│   │   └── authSlice.ts
│   └── profile/
│       ├── components/
│       ├── hooks/
│       └── services/
├── components/
│   ├── common/
│   │   ├── Button.tsx
│   │   ├── Input.tsx
│   │   └── Modal.tsx
│   └── layout/
│       ├── Header.tsx
│       └── Footer.tsx
└── utils/
    ├── date.ts
    └── format.ts
```

## 注释规范

### 一般规则

- 代码应该是自文档化的，注释应该解释"为什么"而不是"做什么"
- 使用JSDoc注释所有公共API、函数和组件
- 对于复杂的算法或业务逻辑，添加详细的注释
- 临时性的代码应该使用`TODO:`或`FIXME:`标记

### JSDoc示例

```typescript
/**
 * 获取用户完整信息
 * 
 * @param userId - 用户ID
 * @param includePrivate - 是否包含私有信息
 * @returns 用户信息对象
 * @throws {ApiError} 当API请求失败时
 */
export const getUserDetails = async (
  userId: string, 
  includePrivate: boolean = false
): Promise<UserDetails> => {
  // 实现...
};
```

### 组件注释

```typescript
/**
 * 用户资料卡片组件
 * 
 * 显示用户的基本信息，并提供编辑功能。
 * 
 * @example
 * ```tsx
 * <UserCard userId="123" editable />
 * ```
 */
export const UserCard: React.FC<UserCardProps> = ({ userId, editable }) => {
  // 实现...
};
```

## Git提交规范

我们使用[Conventional Commits](https://www.conventionalcommits.org/)规范进行Git提交。

### 提交消息格式

```
<类型>[可选的作用域]: <描述>

[可选的正文]

[可选的脚注]
```

### 类型

- `feat`: 新功能
- `fix`: 错误修复
- `docs`: 文档修改
- `style`: 不影响代码功能的格式变化
- `refactor`: 重构（既不是新功能，也不是修复错误）
- `perf`: 性能优化
- `test`: 添加缺失的测试或修正现有测试
- `build`: 影响构建系统或外部依赖的更改
- `ci`: 对CI配置文件和脚本的更改
- `chore`: 其他不修改源代码或测试文件的变更
- `revert`: 撤销之前的提交

### 提交消息示例

```
feat(auth): 添加微信登录功能

实现了基于微信OAuth的登录流程，包括微信授权、用户信息获取和账号关联逻辑

关联Issue: #123
```

```
fix(ui): 修复暗模式下按钮文字不可见的问题

在暗模式下按钮文字颜色与背景颜色太接近，导致可读性差。
修改了按钮组件的样式逻辑，根据当前主题自动调整文字颜色。

关联PR: #456
```

---

遵循这些规范将有助于保持代码库的一致性和可维护性。如有任何问题或建议，请联系项目维护者。 