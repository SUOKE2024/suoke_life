# 📱 索克生活UI页面路由访问顺序分析

## 🏗️ 导航架构概览

### 根导航器层级结构
```
AppNavigator (根导航器)
├── AuthNavigator (认证流程)
│   ├── WelcomeScreen (欢迎页)
│   ├── LoginScreen (登录页)
│   ├── RegisterScreen (注册页)
│   └── ForgotPasswordScreen (忘记密码页)
└── MainNavigator (主应用)
    ├── MainTabNavigator (底部Tab导航)
    │   ├── HomeScreen (聊天主页)
    │   ├── SuokeScreen (SUOKE页)
    │   ├── ExploreScreen (探索页)
    │   ├── LifeScreen (LIFE页)
    │   ├── MazeNavigator (迷宫游戏)
    │   ├── BenchmarkScreen (评测页)
    │   └── ProfileScreen (我的页面)
    └── StackNavigator (堆栈页面)
        ├── SettingsScreen (设置页)
        ├── ServiceStatusScreen (服务状态页)
        ├── ServiceManagementScreen (服务管理页)
        ├── DeveloperPanelScreen (开发者面板)
        ├── ApiIntegrationDemo (API集成演示)
        ├── ChatDetailScreen (聊天详情页)
        ├── AgentChatScreen (智能体聊天页)
        └── DiagnosisServiceScreen (诊断服务页)
```

## 🚀 应用启动流程

### 1. 应用启动序列
```
App.tsx
└── AppNavigator
    ├── 检查认证状态 (isAuthenticated)
    ├── 检查演示模式 (isDemoMode)
    ├── 恢复导航状态 (AsyncStorage)
    └── 路由分发
        ├── 未认证 → AuthNavigator
        └── 已认证 → MainNavigator
```

### 2. 启动页面优先级
1. **启动画面** (Loading Screen) - 检查认证状态
2. **欢迎页面** (WelcomeScreen) - 首次使用引导
3. **主页面** (HomeScreen) - 认证后的默认页面

## 🔐 认证流程路由

### 认证页面访问顺序
```
WelcomeScreen (欢迎页)
├── → LoginScreen (登录)
│   ├── → ForgotPasswordScreen (忘记密码)
│   └── → MainNavigator (登录成功)
├── → RegisterScreen (注册)
│   └── → MainNavigator (注册成功)
└── → AgentDemo (演示模式)
```

### 认证页面动画配置
- **WelcomeScreen**: `fade` 淡入动画
- **LoginScreen**: `slide_from_bottom` 从底部滑入
- **RegisterScreen**: `slide_from_right` 从右侧滑入
- **ForgotPasswordScreen**: `slide_from_right` 从右侧滑入

## 🏠 主应用导航结构

### 底部Tab页面访问顺序 (MainTabNavigator)
```
1. HomeScreen (聊天) - 默认首页
   ├── 智能体快速访问
   ├── 诊断服务入口
   ├── 健康数据概览
   └── 微服务状态监控

2. SuokeScreen (SUOKE)
   ├── 核心功能展示
   └── 智能体协作

3. ExploreScreen (探索)
   ├── 功能发现
   └── 内容推荐

4. LifeScreen (LIFE)
   ├── 健康管理
   ├── 生活方式
   └── 数据分析

5. MazeNavigator (迷宫)
   ├── MazeHome (迷宫首页)
   ├── MazeGame (游戏页面)
   └── MazeResults (结果页面)

6. BenchmarkScreen (评测)
   ├── 性能测试
   └── 系统评估

7. ProfileScreen (我的)
   ├── 个人信息
   ├── 设置入口
   └── 服务管理
```

### Tab页面图标配置
| 页面 | 激活图标 | 非激活图标 | 标签 |
|------|----------|------------|------|
| Home | chat | chat-outline | 聊天 |
| Suoke | stethoscope | stethoscope | SUOKE |
| Explore | compass | compass-outline | 探索 |
| Life | heart-pulse | heart-outline | LIFE |
| Maze | maze | maze | 迷宫 |
| Benchmark | speedometer | speedometer-slow | 评测 |
| Profile | account | account-outline | 我的 |

## 🔄 页面跳转路径分析

### 从HomeScreen的跳转路径
```
HomeScreen
├── → ChatDetailScreen
│   └── 参数: { chatId, chatType, chatName }
├── → AgentChatScreen
│   └── 参数: { agentId, agentName }
│   └── 智能体类型:
│       ├── xiaoai (小艾) - 多模态感知
│       ├── xiaoke (小克) - 健康服务
│       ├── laoke (老克) - 知识传播
│       └── soer (索儿) - 营养生活
├── → DiagnosisServiceScreen
│   └── 参数: { serviceType }
│   └── 诊断服务类型:
│       ├── calculation (算诊服务)
│       ├── look (望诊服务)
│       ├── listen (闻诊服务)
│       ├── inquiry (问诊服务)
│       └── palpation (切诊服务)
├── → HealthData (健康数据)
└── → KnowledgeBase (知识库)
```

### 从ProfileScreen的跳转路径
```
ProfileScreen
├── → SettingsScreen (设置)
├── → ServiceStatusScreen (服务状态)
├── → ServiceManagementScreen (服务管理)
├── → DeveloperPanelScreen (开发者面板)
└── → ApiIntegrationDemo (API集成演示)
```

### 诊断服务页面跳转路径
```
DiagnosisServiceScreen
├── → DiagnosisHistory (诊断历史)
├── → DiagnosisResult (诊断结果)
│   └── 参数: { resultId }
└── → FiveDiagnosisScreen (五诊详情)
```

## 🎯 智能体服务路由

### 智能体访问端点配置
```javascript
const microservices = {
  agents: {
    xiaoai: { name: '小艾', port: 8015, description: '多模态感知智能体' },
    xiaoke: { name: '小克', port: 8016, description: '健康服务智能体' },
    laoke: { name: '老克', port: 8017, description: '知识传播智能体' },
    soer: { name: '索儿', port: 8018, description: '营养生活智能体' }
  }
}
```

### 智能体页面主题配置
```javascript
const agentConfigs = {
  xiaoai: {
    colors: { primary: '#4A90E2', secondary: '#E3F2FD' },
    avatar: '🤖',
    tag: '多模态感知'
  },
  xiaoke: {
    colors: { primary: '#7B68EE', secondary: '#F3E5F5' },
    avatar: '🧘‍♂️',
    tag: '健康服务'
  },
  laoke: {
    colors: { primary: '#FF6B6B', secondary: '#FFEBEE' },
    avatar: '👨‍⚕️',
    tag: '知识传播'
  },
  soer: {
    colors: { primary: '#4ECDC4', secondary: '#E0F2F1' },
    avatar: '🏃‍♀️',
    tag: '营养生活'
  }
}
```

## 🏥 诊断服务路由

### 五诊服务端点配置
```javascript
const diagnosis = {
  calculation: { name: '算诊服务', port: 8023, description: '计算诊断' },
  look: { name: '望诊服务', port: 8020, description: '图像分析诊断' },
  listen: { name: '闻诊服务', port: 8022, description: '语音分析诊断' },
  inquiry: { name: '问诊服务', port: 8021, description: '问答交互诊断' },
  palpation: { name: '切诊服务', port: 8024, description: '触诊模拟' }
}
```

### 诊断页面访问流程
1. **DiagnosisServiceScreen** - 诊断服务选择
2. **FiveDiagnosisScreen** - 五诊协调器
3. **EnhancedDiagnosisScreen** - 增强诊断
4. **DiagnosisDetailScreen** - 诊断详情

## 🔧 核心服务路由

### 核心微服务端点
```javascript
const core = {
  gateway: { name: 'API网关', port: 8000, description: '统一入口' },
  user: { name: '用户管理', port: 8001, description: '用户服务' },
  knowledge: { name: '知识服务', port: 8002, description: '统一知识库' },
  health: { name: '健康数据', port: 8003, description: '健康数据管理' },
  blockchain: { name: '区块链服务', port: 8004, description: '隐私保护' },
  communication: { name: '通信服务', port: 8005, description: '消息通信' }
}
```

## 🎨 页面动画配置

### 全局动画设置
- **默认动画**: `slide_from_right` (从右侧滑入)
- **手势支持**: `gestureEnabled: true`
- **手势方向**: `horizontal` (水平滑动)

### 特殊动画配置
- **Modal页面**: `presentation: "card"`
- **认证页面**: 各种动画类型组合
- **Tab切换**: 无动画 (即时切换)

## 📊 页面访问统计

### 页面文件统计
- **主要页面**: 7个 (Tab页面)
- **认证页面**: 4个
- **详情页面**: 10+个
- **管理页面**: 5个
- **演示页面**: 3个

### 导航层级深度
- **最大深度**: 4层 (Root → Main → Tab → Detail)
- **平均深度**: 3层
- **常用路径**: 2-3层

## 🔍 深度链接配置

### URL路由映射
```javascript
const linkingConfig = {
  screens: {
    Auth: {
      screens: {
        Welcome: 'welcome',
        Login: 'login',
        Register: 'register',
        ForgotPassword: 'forgot-password'
      }
    },
    Main: {
      screens: {
        MainTabs: {
          screens: {
            Home: 'home',
            Suoke: 'suoke',
            Explore: 'explore',
            Life: 'life',
            Profile: 'profile'
          }
        },
        ChatDetail: 'chat/:chatId',
        AgentChat: 'agent/:agentId',
        DiagnosisService: 'diagnosis/:serviceType'
      }
    }
  }
}
```

## 🚦 路由访问控制

### 认证保护
- **公开页面**: Welcome, Login, Register, ForgotPassword, AgentDemo
- **保护页面**: 所有Main导航下的页面
- **权限检查**: 基于Redux状态管理

### 页面状态管理
- **导航状态持久化**: AsyncStorage
- **页面状态恢复**: 应用重启后恢复
- **深度链接处理**: 支持外部链接跳转

## 📱 用户体验优化

### 页面加载策略
- **懒加载**: 非关键页面使用React.lazy()
- **预加载**: 主要Tab页面预先加载
- **缓存策略**: 页面状态缓存

### 性能监控
- **页面渲染时间**: usePerformanceMonitor
- **内存使用**: 可选监控
- **导航性能**: 页面切换时间统计

## 🎯 用户旅程分析

### 典型用户路径
1. **新用户**: Welcome → Register → Home → AgentChat
2. **老用户**: Login → Home → DiagnosisService
3. **演示用户**: Welcome → AgentDemo → Home
4. **管理员**: Login → Profile → DeveloperPanel

### 高频访问路径
1. **Home → AgentChat** (智能体交互)
2. **Home → DiagnosisService** (健康诊断)
3. **Profile → Settings** (设置管理)
4. **Life → HealthDashboard** (健康数据)

---

*分析时间: 2024年6月9日*  
*基于版本: React Native 0.79.2*  
*页面总数: 30+ 个主要页面* 