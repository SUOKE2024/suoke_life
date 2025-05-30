import { useTheme } from '../../contexts/ThemeContext';
import { useAccessibility } from '../../contexts/AccessibilityContext';
import { responsive, touchTarget } from '../../utils/responsive';
import Button from './Button';





/**
 * 索克生活 - 无障碍设置面板
 * 提供完整的无障碍功能配置界面
 */

import React from 'react';
  View,
  Text,
  StyleSheet,
  ScrollView,
  Switch,
  TouchableOpacity,
} from 'react-native';

interface AccessibilityPanelProps {
  style?: any;
  onClose?: () => void;
}

export const AccessibilityPanel: React.FC<AccessibilityPanelProps> = ({
  style,
  onClose,
}) => {
  const { theme } = useTheme();
  const { config, updateConfig, resetConfig, triggerHapticFeedback, announceForAccessibility } = useAccessibility();

  // 处理配置更新
  const handleConfigUpdate = useCallback( (key: string, value: any) => {, []);
    updateConfig({ [key]: value });
    
    // 触觉反馈
    if (config.hapticFeedbackEnabled) {
      triggerHapticFeedback('light');
    }
    
    // 无障碍公告
    announceForAccessibility(`${getSettingLabel(key)}已${value ? '启用' : '禁用'}`);
  };

  // 获取设置标签
  const getSettingLabel = (key: string): string => {
    const labels: Record<string, string> = {
      highContrastEnabled: '高对比度模式',
      largeFontEnabled: '大字体模式',
      reduceMotionEnabled: '减少动画',
      voiceNavigationEnabled: '语音导航',
      hapticFeedbackEnabled: '触觉反馈',
      focusIndicatorEnabled: '焦点指示器',
    };
    return labels[key] || key;
  };

  // 获取设置描述
  const getSettingDescription = (key: string): string => {
    const descriptions: Record<string, string> = {
      highContrastEnabled: '提高界面元素的对比度，便于视觉障碍用户使用',
      largeFontEnabled: '增大字体尺寸，提高文本可读性',
      reduceMotionEnabled: '减少界面动画效果，避免眩晕',
      voiceNavigationEnabled: '启用语音播报和导航功能',
      hapticFeedbackEnabled: '在交互时提供触觉反馈',
      focusIndicatorEnabled: '显示焦点指示器，便于键盘导航',
    };
    return descriptions[key] || '';
  };

  // 渲染设置项
  const renderSettingItem = (
    key: string,
    value: boolean,
    label: string,
    description: string
  ) => (
    <View key={key} style={[styles.settingItem, { borderBottomColor: theme.colors.outline }]}>
      <View style={styles.settingContent}>
        <Text style={[styles.settingLabel, { color: theme.colors.onSurface }]}>
          {label}
        </Text>
        <Text style={[styles.settingDescription, { color: theme.colors.onSurfaceVariant }]}>
          {description}
        </Text>
      </View>
      
      <Switch
        value={value}
        onValueChange={(newValue) => handleConfigUpdate(key, newValue)}
        trackColor={{
          false: theme.colors.outline,
          true: theme.colors.primary,
        }}
        thumbColor={value ? theme.colors.surface : theme.colors.surface}
        accessible={true}
        accessibilityLabel={`${label}开关`}
        accessibilityHint={`当前${value ? '已启用' : '已禁用'}，双击切换`}
        accessibilityRole="switch"
      />
    </View>
  );

  // 渲染滑块设置项
  const renderSliderItem = (
    key: string,
    value: number,
    label: string,
    description: string,
    min: number,
    max: number,
    step: number = 0.1
  ) => (
    <View key={key} style={[styles.settingItem, { borderBottomColor: theme.colors.outline }]}>
      <View style={styles.settingContent}>
        <Text style={[styles.settingLabel, { color: theme.colors.onSurface }]}>
          {label}: {value.toFixed(1)}
        </Text>
        <Text style={[styles.settingDescription, { color: theme.colors.onSurfaceVariant }]}>
          {description}
        </Text>
      </View>
      
      <View style={styles.sliderContainer}>
        <TouchableOpacity
          style={[styles.sliderButton, { backgroundColor: theme.colors.outline }]}
          onPress={() => {
            const newValue = Math.max(min, value - step);
            handleConfigUpdate(key, newValue);
          }}
          accessible={true}
          accessibilityLabel={`减少${label}`}
          accessibilityRole="button"
        >
          <Text style={[styles.sliderButtonText, { color: theme.colors.onSurface }]}>-</Text>
        </TouchableOpacity>
        
        <View style={[styles.sliderValue, { backgroundColor: theme.colors.surface }]}>
          <Text style={[styles.sliderValueText, { color: theme.colors.onSurface }]}>
            {value.toFixed(1)}
          </Text>
        </View>
        
        <TouchableOpacity
          style={[styles.sliderButton, { backgroundColor: theme.colors.outline }]}
          onPress={() => {
            const newValue = Math.min(max, value + step);
            handleConfigUpdate(key, newValue);
          }}
          accessible={true}
          accessibilityLabel={`增加${label}`}
          accessibilityRole="button"
        >
          <Text style={[styles.sliderButtonText, { color: theme.colors.onSurface }]}>+</Text>
        </TouchableOpacity>
      </View>
    </View>
  );

  return (
    <View style={[styles.container, { backgroundColor: theme.colors.surface }, style]}>
      <View style={[styles.header, { borderBottomColor: theme.colors.outline }]}>
        <Text style={[styles.title, { color: theme.colors.onSurface }]}>
          无障碍设置
        </Text>
        {onClose && (
          <Button
            title="关闭"
            variant="ghost"
            size="small"
            onPress={onClose}
          />
        )}
      </View>

      <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>
        <View style={styles.section}>
          <Text style={[styles.sectionTitle, { color: theme.colors.primary }]}>
            视觉辅助
          </Text>
          
          {renderSettingItem(
            'highContrastEnabled',
            config.highContrastEnabled,
            '高对比度模式',
            '提高界面元素的对比度，便于视觉障碍用户使用'
          )}
          
          {renderSettingItem(
            'largeFontEnabled',
            config.largeFontEnabled,
            '大字体模式',
            '增大字体尺寸，提高文本可读性'
          )}
          
          {renderSliderItem(
            'fontScale',
            config.fontScale,
            '字体缩放',
            '调整字体大小比例',
            0.8,
            2.0,
            0.1
          )}
        </View>

        <View style={styles.section}>
          <Text style={[styles.sectionTitle, { color: theme.colors.primary }]}>
            动画与交互
          </Text>
          
          {renderSettingItem(
            'reduceMotionEnabled',
            config.reduceMotionEnabled,
            '减少动画',
            '减少界面动画效果，避免眩晕'
          )}
          
          {renderSettingItem(
            'hapticFeedbackEnabled',
            config.hapticFeedbackEnabled,
            '触觉反馈',
            '在交互时提供触觉反馈'
          )}
        </View>

        <View style={styles.section}>
          <Text style={[styles.sectionTitle, { color: theme.colors.primary }]}>
            导航辅助
          </Text>
          
          {renderSettingItem(
            'voiceNavigationEnabled',
            config.voiceNavigationEnabled,
            '语音导航',
            '启用语音播报和导航功能'
          )}
          
          {renderSettingItem(
            'focusIndicatorEnabled',
            config.focusIndicatorEnabled,
            '焦点指示器',
            '显示焦点指示器，便于键盘导航'
          )}
          
          {renderSliderItem(
            'speechRate',
            config.speechRate,
            '语音速度',
            '调整语音播报的速度',
            0.5,
            2.0,
            0.1
          )}
        </View>

        <View style={styles.section}>
          <Text style={[styles.sectionTitle, { color: theme.colors.primary }]}>
            触摸设置
          </Text>
          
          {renderSliderItem(
            'minimumTouchTargetSize',
            config.minimumTouchTargetSize,
            '最小触摸目标',
            '设置触摸目标的最小尺寸（像素）',
            32,
            64,
            4
          )}
        </View>

        <View style={styles.actions}>
          <Button
            title="重置为默认设置"
            variant="outline"
            onPress={() => {
              resetConfig();
              announceForAccessibility('无障碍设置已重置为默认值');
            }}
            style={styles.resetButton}
          />
        </View>
      </ScrollView>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    borderRadius: responsive.width(12),
    overflow: 'hidden',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: responsive.width(16),
    borderBottomWidth: 1,
  },
  title: {
    fontSize: responsive.fontSize(20),
    fontWeight: '600',
  },
  content: {
    flex: 1,
  },
  section: {
    padding: responsive.width(16),
  },
  sectionTitle: {
    fontSize: responsive.fontSize(16),
    fontWeight: '600',
    marginBottom: responsive.height(12),
  },
  settingItem: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: responsive.height(12),
    borderBottomWidth: 1,
    minHeight: touchTarget.MIN_SIZE,
  },
  settingContent: {
    flex: 1,
    marginRight: responsive.width(12),
  },
  settingLabel: {
    fontSize: responsive.fontSize(16),
    fontWeight: '500',
    marginBottom: responsive.height(4),
  },
  settingDescription: {
    fontSize: responsive.fontSize(14),
    lineHeight: responsive.fontSize(20),
  },
  sliderContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: responsive.width(8),
  },
  sliderButton: {
    width: touchTarget.MIN_SIZE,
    height: touchTarget.MIN_SIZE,
    borderRadius: responsive.width(6),
    justifyContent: 'center',
    alignItems: 'center',
  },
  sliderButtonText: {
    fontSize: responsive.fontSize(18),
    fontWeight: '600',
  },
  sliderValue: {
    paddingHorizontal: responsive.width(12),
    paddingVertical: responsive.height(8),
    borderRadius: responsive.width(6),
    minWidth: responsive.width(60),
    alignItems: 'center',
  },
  sliderValueText: {
    fontSize: responsive.fontSize(14),
    fontWeight: '500',
  },
  actions: {
    padding: responsive.width(16),
    paddingTop: responsive.height(24),
  },
  resetButton: {
    marginTop: responsive.height(8),
  },
});

export default React.memo(AccessibilityPanel); 