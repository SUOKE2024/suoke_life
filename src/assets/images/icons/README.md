# 索克生活 - 应用图标资源

## 📱 移动端图标

### iOS 图标
位置：`ios/SuokeLife/Images.xcassets/AppIcon.appiconset/`

| 尺寸 | 用途 | 文件名 |
|------|------|--------|
| 20@2x (40x40) | 通知图标 | AppIcon-20@2x.png |
| 20@3x (60x60) | 通知图标 | AppIcon-20@3x.png |
| 29@2x (58x58) | 设置图标 | AppIcon-29@2x.png |
| 29@3x (87x87) | 设置图标 | AppIcon-29@3x.png |
| 40@2x (80x80) | Spotlight搜索 | AppIcon-40@2x.png |
| 40@3x (120x120) | Spotlight搜索 | AppIcon-40@3x.png |
| 60@2x (120x120) | 应用图标 | AppIcon-60@2x.png |
| 60@3x (180x180) | 应用图标 | AppIcon-60@3x.png |
| 1024x1024 | App Store | AppIcon-1024.png |

### Android 图标
位置：`android/app/src/main/res/mipmap-*/`

| 密度 | 尺寸 | 文件名 |
|------|------|--------|
| mdpi | 48x48 | ic_launcher.png |
| hdpi | 72x72 | ic_launcher.png |
| xhdpi | 96x96 | ic_launcher.png |
| xxhdpi | 144x144 | ic_launcher.png |
| xxxhdpi | 192x192 | ic_launcher.png |

## 🖥️ 桌面端图标

### 桌面应用图标
位置：`src/assets/images/icons/desktop/`

| 尺寸 | 用途 | 文件名 |
|------|------|--------|
| 1024x1024 | 高分辨率显示 | app-icon-1024.png |
| 512x512 | 标准桌面图标 | app-icon-512.png |
| 256x256 | 中等尺寸图标 | app-icon-256.png |
| 128x128 | 小尺寸图标 | app-icon-128.png |
| 64x64 | 最小尺寸图标 | app-icon-64.png |

## 🎨 设计规范

### 品牌色彩
- **主色调**: #35bb78 (索克绿)
- **辅助色**: #ff6800 (索克橙)
- **背景色**: #FFFFFF (白色)

### 设计原则
1. **简洁明了**: 图标设计简洁，易于识别
2. **品牌一致**: 保持索克生活的品牌视觉统一
3. **多平台适配**: 确保在不同平台和尺寸下都清晰可见
4. **中医元素**: 融入传统中医文化元素

### 图标特点
- 圆角设计，现代简约
- 使用品牌主色调
- 包含健康管理相关元素
- 支持高分辨率显示

## 🔧 使用说明

### 更新图标
1. 修改源文件：`src/assets/images/logo_1024.png`
2. 运行生成脚本重新生成所有尺寸
3. 更新相应平台的配置文件

### 生成命令
```bash
# iOS图标生成
cd ios/SuokeLife/Images.xcassets/AppIcon.appiconset
sips -z 40 40 AppIcon-1024.png --out AppIcon-20@2x.png
# ... 其他尺寸

# Android图标生成
sips -z 48 48 src/assets/images/logo_1024.png --out android/app/src/main/res/mipmap-mdpi/ic_launcher.png
# ... 其他密度
```

## 📝 注意事项

1. **文件格式**: 使用PNG格式，支持透明背景
2. **命名规范**: 遵循各平台的命名约定
3. **尺寸精确**: 确保图标尺寸完全符合平台要求
4. **质量保证**: 使用高质量源文件生成，避免模糊
5. **版本控制**: 图标更新时同步更新所有平台

---

*索克生活 - AI驱动的智慧健康管理平台*