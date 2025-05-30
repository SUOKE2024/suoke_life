import { useTheme } from '../contexts/ThemeContext';
import { Text, Button, ThemeToggle, Card } from '../components/ui';





/**
 * 索克生活品牌色彩演示页面
 * 展示新的索克绿和索克橙品牌色彩系统
 */

import React from 'react';
  View,
  ScrollView,
  StyleSheet,
} from 'react-native';

// 色彩样本组件
const ColorSwatch = useCallback( ({ 
  color, 
  name, 
  description, 
}: { 
  color: string; 
  name: string; 
  description: string;
}) => {, []);
  const { theme } = useTheme();
  
  return (
    <View style={styles.colorSwatch}>
      <View style={[styles.colorBox, { backgroundColor: color }]} />
      <View style={styles.colorInfo}>
        <Text variant="body1" style={{ fontWeight: 'bold' }}>
          {name}
        </Text>
        <Text variant="caption" style={{ color: theme.colors.onSurfaceVariant }}>
          {color}
        </Text>
        <Text variant="caption" style={{ marginTop: 4 }}>
          {description}
        </Text>
      </View>
    </View>
  );
};

// 色彩组组件
const ColorGroup = useCallback( ({ 
  title, 
  colors, 
}: { 
  title: string; 
  colors: Array<{ color: string; name: string; description: string }>;
}) => {, []);
  const { theme } = useTheme();
  
  return (
    <View style={styles.colorGroup}>
      <Text variant="h5" style={{ 
        marginBottom: 16, 
        color: theme.colors.primary,
        fontWeight: 'bold',
      }}>
        {title}
      </Text>
      {colors.map((colorInfo, index) => (
        <ColorSwatch
          key={index}
          color={colorInfo.color}
          name={colorInfo.name}
          description={colorInfo.description}
        />
      ))}
    </View>
  );
};

// 按钮演示组件
const ButtonShowcase = useCallback( ({ 
  title, 
  buttons, 
}: { 
  title: string; 
  buttons: Array<{ variant: any; size: any; title: string }>;
}) => {, []);
  const { theme } = useTheme();
  
  return (
    <View style={styles.buttonShowcase}>
      <Text variant="h6" style={{ 
        marginBottom: 12, 
        color: theme.colors.onSurface,
        fontWeight: 'bold',
      }}>
        {title}
      </Text>
      <View style={styles.buttonRow}>
        {buttons.map((btn, index) => (
          <Button
            key={index}
            variant={btn.variant}
            size={btn.size}
            title={btn.title}
            onPress={() => {}}
            style={{ marginRight: 8, marginBottom: 8 }}
          />
        ))}
      </View>
    </View>
  );
};

// 状态色彩演示组件
const StatusColorDemo = useCallback( ({ 
  colors, 
}: { 
  colors: Array<{ color: string; name: string; icon: string }>;
}) => {, []);
  const { theme } = useTheme();
  
  return (
    <View style={styles.statusColors}>
      <Text variant="h6" style={{ 
        marginBottom: 12, 
        color: theme.colors.onSurface,
        fontWeight: 'bold',
      }}>
        状态色彩系统
      </Text>
      <View style={styles.statusRow}>
        {colors.map((status, index) => (
          <View key={index} style={styles.statusItem}>
            <View style={[
              styles.statusIndicator, 
              { backgroundColor: status.color },
            ]} />
            <Text variant="caption" style={{ textAlign: 'center', marginTop: 4 }}>
              {status.icon} {status.name}
            </Text>
          </View>
        ))}
      </View>
    </View>
  );
};

const BrandColorDemo: React.FC = () => {
  const { theme, isDark } = useTheme();

  // 索克绿色系
  const suokeGreenColors = [
    { 
      color: theme.colors.primaryDark, 
      name: '深索克绿', 
      description: '深沉稳重，象征专业与信任', 
    },
    { 
      color: theme.colors.primary, 
      name: '索克绿', 
      description: '生命力的象征，代表健康与活力', 
    },
    { 
      color: theme.colors.primaryLight, 
      name: '浅索克绿', 
      description: '清新自然，传递希望与成长', 
    },
  ];

  // 索克橙色系
  const suokeOrangeColors = [
    { 
      color: theme.colors.secondaryDark, 
      name: '深索克橙', 
      description: '温暖深邃，体现专业关怀', 
    },
    { 
      color: theme.colors.secondary, 
      name: '索克橙', 
      description: '活力四射，代表热情与温暖', 
    },
    { 
      color: theme.colors.secondaryLight, 
      name: '浅索克橙', 
      description: '温和亲切，营造舒适体验', 
    },
  ];

  // 中医五行色彩
  const tcmColors = [
    { 
      color: theme.colors.tcm.wood, 
      name: '木 - 青色', 
      description: '肝胆经络，主生发疏泄', 
    },
    { 
      color: theme.colors.tcm.fire, 
      name: '火 - 红色', 
      description: '心小肠经，主血脉神明', 
    },
    { 
      color: theme.colors.tcm.earth, 
      name: '土 - 黄色', 
      description: '脾胃经络，主运化水谷', 
    },
    { 
      color: theme.colors.tcm.metal, 
      name: '金 - 白色', 
      description: '肺大肠经，主气机宣降', 
    },
    { 
      color: theme.colors.tcm.water, 
      name: '水 - 黑色', 
      description: '肾膀胱经，主藏精纳气', 
    },
  ];

  // 按钮变体演示
  const primaryButtons = [
    { variant: 'primary', size: 'small', title: '小按钮' },
    { variant: 'primary', size: 'medium', title: '中按钮' },
    { variant: 'primary', size: 'large', title: '大按钮' },
  ];

  const secondaryButtons = [
    { variant: 'secondary', size: 'small', title: '次要小' },
    { variant: 'secondary', size: 'medium', title: '次要中' },
    { variant: 'secondary', size: 'large', title: '次要大' },
  ];

  const outlineButtons = [
    { variant: 'outline', size: 'small', title: '轮廓小' },
    { variant: 'outline', size: 'medium', title: '轮廓中' },
    { variant: 'outline', size: 'large', title: '轮廓大' },
  ];

  // 状态色彩
  const statusColors = [
    { color: theme.colors.success, name: '成功', icon: '✅' },
    { color: theme.colors.warning, name: '警告', icon: '⚠️' },
    { color: theme.colors.error, name: '错误', icon: '❌' },
    { color: theme.colors.info, name: '信息', icon: 'ℹ️' },
  ];

  return (
    <ScrollView 
      style={[styles.container, { backgroundColor: theme.colors.background }]}
      showsVerticalScrollIndicator={false}
    >
      {/* 标题区域 */}
      <View style={styles.header}>
        <Text variant="h2" style={{ 
          color: theme.colors.primary, 
          textAlign: 'center',
          fontWeight: 'bold',
          marginBottom: 8,
        }}>
          索克生活品牌色彩
        </Text>
        <Text variant="h4" style={{ 
          color: theme.colors.secondary, 
          textAlign: 'center',
          fontWeight: '600',
          marginBottom: 16,
        }}>
          🌿 索克绿 × 🧡 索克橙
        </Text>
        
        {/* 主题切换 */}
        <View style={styles.themeToggleContainer}>
          <ThemeToggle size="large" showLabel />
        </View>
        
        <Text variant="body1" style={{ 
          textAlign: 'center', 
          color: theme.colors.onSurfaceVariant,
          lineHeight: 24,
        }}>
          索克绿代表生命力与健康，作为主色调传递专业可信赖的品牌形象；
          索克橙代表活力与温暖，作为次要色调，代表活力与温暖。
        </Text>
        <Text variant="body2" style={Object.assign({}, styles.introText, { marginTop: 8 })}>
          这套色彩系统完美融合了传统中医文化与现代设计美学，
          为用户提供既专业又温暖的健康管理体验。
        </Text>
      </View>

      {/* 索克绿色系 */}
      <Card style={styles.section}>
        <ColorGroup title="🌿 索克绿色系" colors={suokeGreenColors} />
      </Card>

      {/* 索克橙色系 */}
      <Card style={styles.section}>
        <ColorGroup title="🧡 索克橙色系" colors={suokeOrangeColors} />
      </Card>

      {/* 中医五行色彩 */}
      <Card style={styles.section}>
        <ColorGroup title="🏮 中医五行色彩" colors={tcmColors} />
      </Card>

      {/* 按钮组件演示 */}
      <Card style={styles.section}>
        <Text variant="h4" style={{ 
          marginBottom: 20, 
          color: theme.colors.primary,
          fontWeight: 'bold',
        }}>
          🎨 按钮组件演示
        </Text>
        
        <ButtonShowcase title="主要按钮 (索克绿)" buttons={primaryButtons} />
        <ButtonShowcase title="次要按钮 (索克橙)" buttons={secondaryButtons} />
        <ButtonShowcase title="轮廓按钮" buttons={outlineButtons} />
      </Card>

      {/* 状态色彩系统 */}
      <Card style={styles.section}>
        <StatusColorDemo colors={statusColors} />
      </Card>

      {/* 底部说明 */}
      <Card style={Object.assign({}, styles.section, styles.footerCard)}>
        <Text variant="h4" style={styles.footerTitle}>
          设计理念 💡
        </Text>
        <Text variant="body1" style={styles.footerText}>
          索克生活的品牌色彩设计深度融合了中医文化内涵与现代设计美学。
          索克绿象征着生命的蓬勃与健康的活力，体现了我们对用户健康的专业承诺；
          索克橙则代表着温暖的关怀与积极的生活态度，传递着我们对用户体验的用心呵护。
        </Text>
        <Text variant="body2" style={Object.assign({}, styles.footerText, { marginTop: 12 })}>
          这套色彩系统不仅在视觉上具有强烈的识别度，更在情感上与用户建立深度连接，
          让每一次交互都充满温度，让健康管理变得更加人性化和有温度。
        </Text>
        
        <View style={styles.modeIndicator}>
          <Text variant="caption" style={{ color: theme.colors.onSurfaceVariant }}>
            当前模式：{isDark ? '🌙 暗黑模式' : '☀️ 浅色模式'}
          </Text>
        </View>
      </Card>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  header: {
    padding: 20,
    alignItems: 'center',
  },
  themeToggleContainer: {
    marginVertical: 16,
  },
  introText: {
    textAlign: 'center',
    lineHeight: 20,
  },
  section: {
    margin: 16,
    padding: 20,
  },
  colorSwatch: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 16,
  },
  colorBox: {
    width: 60,
    height: 60,
    borderRadius: 12,
    marginRight: 16,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  colorInfo: {
    flex: 1,
  },
  colorGroup: {
    marginBottom: 8,
  },
  buttonShowcase: {
    marginBottom: 20,
  },
  buttonRow: {
    flexDirection: 'row',
    flexWrap: 'wrap',
  },
  statusColors: {
    marginBottom: 8,
  },
  statusRow: {
    flexDirection: 'row',
    justifyContent: 'space-around',
  },
  statusItem: {
    alignItems: 'center',
    flex: 1,
  },
  statusIndicator: {
    width: 40,
    height: 40,
    borderRadius: 20,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  footerCard: {
    marginBottom: 40,
  },
  footerTitle: {
    marginBottom: 16,
    textAlign: 'center',
    fontWeight: 'bold',
  },
  footerText: {
    lineHeight: 24,
    textAlign: 'center',
  },
  modeIndicator: {
    marginTop: 20,
    padding: 12,
    borderRadius: 8,
    alignItems: 'center',
  },
});

export default React.memo(BrandColorDemo); 