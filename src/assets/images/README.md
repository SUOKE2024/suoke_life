# 图片资源说明

## app_icon.png
应用图标文件，建议规格：
- 尺寸：1024x1024px
- 格式：PNG
- 背景：透明或白色
- 设计：索克生活品牌标识

## 使用方法
在WelcomeScreen.tsx中，将以下注释代码取消注释并删除Icon占位符：

```tsx
<Image
  source={require('../../assets/images/app_icon.png')}
  style={styles.logoImage}
  resizeMode="contain"
/>
```

同时添加对应的样式：

```tsx
logoImage: {
  width: 120,
  height: 120,
  borderRadius: 60,
},
```