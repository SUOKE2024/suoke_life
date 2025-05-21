# 索克生活项目贡献指南

感谢您对索克生活项目的关注与支持！本文档提供了如何参与项目贡献的详细指南。

## 目录

- [代码贡献流程](#代码贡献流程)
- [提交规范](#提交规范)
- [开发环境配置](#开发环境配置)
- [代码规范](#代码规范)
- [测试规范](#测试规范)
- [文档贡献](#文档贡献)
- [问题报告](#问题报告)
- [功能建议](#功能建议)
- [行为准则](#行为准则)

## 代码贡献流程

1. **Fork仓库**
   - 在GitHub上访问[项目主页](https://github.com/SUOKE2024/suoke_life)
   - 点击右上角的"Fork"按钮，将仓库复制到您的GitHub账户下

2. **Clone本地副本**
   ```bash
   git clone git@github.com:YOUR_USERNAME/suoke_life.git
   cd suoke_life
   ```

3. **添加上游仓库**
   ```bash
   git remote add upstream git@github.com:SUOKE2024/suoke_life.git
   ```

4. **创建特性分支**
   ```bash
   git checkout -b feature/your-feature-name
   ```
   分支命名规范：
   - `feature/xxx`：新功能开发
   - `fix/xxx`：问题修复
   - `docs/xxx`：文档更新
   - `test/xxx`：测试相关
   - `refactor/xxx`：代码重构
   - `style/xxx`：代码风格调整

5. **开发您的功能**
   - 确保代码符合项目的代码规范
   - 添加必要的测试用例
   - 确保所有测试通过

6. **保持分支同步**
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

7. **提交您的更改**
   ```bash
   git add .
   git commit -m "feat: 添加新功能描述"
   ```

8. **推送到您的仓库**
   ```bash
   git push origin feature/your-feature-name
   ```

9. **创建Pull Request**
   - 访问您的GitHub仓库
   - 点击"Compare & pull request"
   - 填写PR描述，包括：
     - 实现的功能或修复的问题
     - 实现方法和设计决策
     - 测试方法和结果
     - 任何相关的文档或截图

10. **代码审查**
    - 项目维护者会审查您的代码
    - 根据反馈进行必要的修改
    - 持续推送更改到您的分支，PR会自动更新

11. **合并**
    - 一旦您的PR被批准，项目维护者会将其合并到主分支

## 提交规范

我们使用[约定式提交](https://www.conventionalcommits.org/)规范，每个提交消息应当由以下部分组成：

```
<类型>[可选的作用域]: <描述>

[可选的正文]

[可选的脚注]
```

### 类型

- `feat`: 新功能
- `fix`: 错误修复
- `docs`: 文档变更
- `style`: 不影响代码功能的格式变化（空格、格式、缺少分号等）
- `refactor`: 重构（既不是新功能，也不是修复错误）
- `perf`: 性能优化
- `test`: 添加缺失的测试或修正现有测试
- `build`: 影响构建系统或外部依赖的更改（例如：npm, yarn, Android/iOS构建配置）
- `ci`: 对CI配置文件和脚本的更改
- `chore`: 其他不修改源代码或测试文件的变更
- `revert`: 撤销之前的提交

### 示例

```
feat(auth): 添加微信登录功能

实现了基于微信OAuth的登录流程，包括：
- 微信授权API集成
- 用户信息获取
- 账号关联逻辑

修复了用户无法使用微信直接登录的问题
```

```
fix(medical): 修复舌象分析错误

修复了在光线不足情况下舌象颜色判断不准确的问题
调整了图像预处理算法，提高了弱光环境下的识别率

关联Issue: #123
```

## 开发环境配置

### 前端环境

1. **安装Node.js和npm**
   - 推荐使用nvm管理Node.js版本
   - 需要Node.js 16.x或更高版本

2. **克隆并安装依赖**
   ```bash
   git clone git@github.com:YOUR_USERNAME/suoke_life.git
   cd suoke_life
   npm install
   ```

3. **运行开发服务器**
   ```bash
   # iOS
   npx react-native run-ios
   # Android
   npx react-native run-android
   ```

### 后端环境

1. **安装Docker和Docker Compose**

2. **启动开发环境**
   ```bash
   cd services
   docker-compose -f docker-compose.dev.yml up -d
   ```

### 编辑器配置

推荐使用Visual Studio Code，并安装以下扩展：
- ESLint
- Prettier
- TypeScript React code snippets
- Jest
- Docker

## 代码规范

### JavaScript/TypeScript规范

- 使用TypeScript编写所有新功能
- 使用ES6+特性
- 使用2个空格缩进
- 每行最大长度：100个字符
- 使用单引号`'`作为字符串默认引号风格
- 每个文件末尾保留一个空行
- 所有导出的函数和类必须有JSDoc注释

### React Native规范

- 使用函数组件和React Hooks，避免使用类组件
- 组件文件采用PascalCase命名，例如`ProfileScreen.tsx`
- 非组件文件采用camelCase命名，例如`apiService.ts`
- 组件prop必须有完整的TypeScript类型定义
- 使用`PropTypes`作为额外的类型检查
- 对于大型组件，拆分为更小的子组件
- 使用React Native Paper组件库保持UI一致性

### 目录结构规范

遵循功能模块化目录结构：
- `/src/api`：API服务
- `/src/components`：共享UI组件
- `/src/features`：功能模块
- `/src/navigation`：导航配置
- `/src/screens`：页面组件
- `/src/services`：业务服务
- `/src/store`：状态管理
- `/src/utils`：工具函数

## 测试规范

### 单元测试

- 所有新功能必须包含单元测试
- 使用Jest作为测试框架
- 测试文件命名：`*.test.tsx`或`*.test.ts`
- 测试覆盖率目标：80%+

### 组件测试

- 使用React Native Testing Library
- 测试文件放在与组件相同的目录下
- 主要测试组件渲染和用户交互

### 端到端测试

- 使用Detox进行关键流程的端到端测试
- 测试文件放在`/e2e`目录下

### 测试命令

```bash
# 运行单元测试
npm test

# 带有覆盖率报告的测试
npm test -- --coverage

# 端到端测试(iOS)
npm run e2e:ios

# 端到端测试(Android)
npm run e2e:android
```

## 文档贡献

### 文档类型

1. **API文档**：位于`/docs/api`目录
2. **架构文档**：位于`/docs/architecture`目录
3. **开发指南**：位于`/docs/development`目录
4. **用户指南**：位于`/docs/user`目录

### 文档规范

- 使用Markdown格式编写文档
- 图表使用[mermaid](https://mermaid-js.github.io/)绘制
- 代码示例应当可直接运行
- 包含版本信息和最后更新日期

## 问题报告

如果您发现了问题但暂时没有时间修复，请通过GitHub Issues报告。提交问题时请包含以下信息：

1. **问题标题**：简洁明了地概括问题
2. **环境信息**：
   - 操作系统版本
   - 设备型号（如适用）
   - React Native版本
   - Node.js版本
   - 相关依赖库版本
3. **重现步骤**：详细的步骤说明，最好包含截图
4. **期望行为**：您认为正确的行为是什么
5. **实际行为**：实际发生的情况
6. **相关代码或日志**：如果有，请添加相关代码或日志片段

## 功能建议

我们欢迎功能建议！通过GitHub Issues提交功能建议时，请包含：

1. **功能标题**：简洁描述您建议的功能
2. **功能详情**：详细描述功能的工作方式
3. **使用场景**：该功能将在哪些场景下使用
4. **预期收益**：该功能将为用户带来什么价值
5. **可能的实现方案**：如果您有实现思路，请一并分享

## 行为准则

为了营造一个开放包容的社区环境，我们请求所有参与者遵守以下行为准则：

1. **尊重他人**：尊重不同背景、经验和观点的项目参与者
2. **专业交流**：使用专业、包容的语言进行交流
3. **建设性反馈**：提供具体、建设性的反馈，而非简单的批评
4. **专注于项目**：讨论应当专注于项目改进，避免无关主题
5. **接受批评**：乐于接受建设性的批评，持续改进

---

希望本指南能帮助您顺利参与索克生活项目的贡献。如有任何疑问，请通过GitHub Issues或发送邮件至contact@suoke.life联系我们。

感谢您的贡献！
