import { StyleSheet } from 'react-native';
import { colors, spacing, borderRadius, fonts, shadows } from '../../constants/theme';

export const commonStyles = StyleSheet.create({
  // 容器样式
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  safeContainer: {
    flex: 1,
    backgroundColor: colors.background,
  },
  centeredContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: colors.background,
  },
  
  // 内容区域
  content: {
    flex: 1,
    paddingHorizontal: spacing.md,
  },
  contentWithPadding: {
    flex: 1,
    padding: spacing.md,
  },
  
  // 卡片样式
  card: {
    backgroundColor: colors.surface,
    borderRadius: borderRadius.md,
    padding: spacing.md,
    marginVertical: spacing.xs,
    ...shadows.sm,
  },
  cardLarge: {
    backgroundColor: colors.surface,
    borderRadius: borderRadius.lg,
    padding: spacing.lg,
    marginVertical: spacing.sm,
    ...shadows.md,
  },
  
  // 分割线
  divider: {
    height: 1,
    backgroundColor: colors.divider,
    marginVertical: spacing.sm,
  },
  dividerThick: {
    height: 8,
    backgroundColor: colors.background,
    marginVertical: spacing.md,
  },
  
  // 文本样式
  title: {
    fontSize: fonts.size.xl,
    fontWeight: 'bold',
    color: colors.text,
    marginBottom: spacing.sm,
  },
  subtitle: {
    fontSize: fonts.size.lg,
    fontWeight: '600',
    color: colors.text,
    marginBottom: spacing.xs,
  },
  body: {
    fontSize: fonts.size.md,
    color: colors.text,
    lineHeight: fonts.lineHeight.md,
  },
  caption: {
    fontSize: fonts.size.sm,
    color: colors.textSecondary,
    lineHeight: fonts.lineHeight.sm,
  },
  
  // 按钮样式
  button: {
    backgroundColor: colors.primary,
    borderRadius: borderRadius.md,
    paddingVertical: spacing.md,
    paddingHorizontal: spacing.lg,
    alignItems: 'center',
    justifyContent: 'center',
    ...shadows.sm,
  },
  buttonSecondary: {
    backgroundColor: colors.surface,
    borderRadius: borderRadius.md,
    paddingVertical: spacing.md,
    paddingHorizontal: spacing.lg,
    alignItems: 'center',
    justifyContent: 'center',
    borderWidth: 1,
    borderColor: colors.border,
  },
  buttonText: {
    fontSize: fonts.size.md,
    fontWeight: '600',
    color: colors.white,
  },
  buttonTextSecondary: {
    fontSize: fonts.size.md,
    fontWeight: '600',
    color: colors.text,
  },
  
  // 输入框样式
  input: {
    backgroundColor: colors.surface,
    borderRadius: borderRadius.md,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    fontSize: fonts.size.md,
    color: colors.text,
    borderWidth: 1,
    borderColor: colors.border,
  },
  inputFocused: {
    borderColor: colors.primary,
    ...shadows.sm,
  },
  inputError: {
    borderColor: colors.error,
  },
  
  // 列表样式
  listContainer: {
    paddingVertical: spacing.sm,
  },
  listItem: {
    backgroundColor: colors.surface,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.md,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  listItemLast: {
    borderBottomWidth: 0,
  },
  
  // 网格样式
  gridContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    paddingHorizontal: spacing.md,
  },
  gridItem: {
    flex: 1,
    margin: spacing.xs,
  },
  gridItemHalf: {
    width: '48%',
    margin: spacing.xs,
  },
  
  // 居中样式
  centerHorizontal: {
    alignItems: 'center',
  },
  centerVertical: {
    justifyContent: 'center',
  },
  centerBoth: {
    alignItems: 'center',
    justifyContent: 'center',
  },
  
  // 间距样式
  marginTop: {
    marginTop: spacing.md,
  },
  marginBottom: {
    marginBottom: spacing.md,
  },
  marginHorizontal: {
    marginHorizontal: spacing.md,
  },
  marginVertical: {
    marginVertical: spacing.md,
  },
  
  // 填充样式
  paddingTop: {
    paddingTop: spacing.md,
  },
  paddingBottom: {
    paddingBottom: spacing.md,
  },
  paddingHorizontal: {
    paddingHorizontal: spacing.md,
  },
  paddingVertical: {
    paddingVertical: spacing.md,
  },
  
  // 阴影样式
  shadowSmall: shadows.sm,
  shadowMedium: shadows.md,
  shadowLarge: shadows.lg,
  
  // 边框样式
  border: {
    borderWidth: 1,
    borderColor: colors.border,
  },
  borderTop: {
    borderTopWidth: 1,
    borderTopColor: colors.border,
  },
  borderBottom: {
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  
  // 圆角样式
  rounded: {
    borderRadius: borderRadius.md,
  },
  roundedLarge: {
    borderRadius: borderRadius.lg,
  },
  roundedFull: {
    borderRadius: borderRadius.circle,
  },
}); 