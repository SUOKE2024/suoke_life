/**
 * 索克生活 - Switch组件
 * 开关组件，用于切换状态
 */

import React from 'react';
import { Switch as RNSwitch, View, StyleSheet, ViewStyle } from 'react-native';
import { colors, spacing } from '../../constants/theme';
import Text from './Text';

export interface SwitchProps {
  // 基础属性
  value: boolean;
  onValueChange: (value: boolean) => void;
  
  // 样式
  size?: 'small' | 'medium' | 'large';
  color?: string;
  
  // 状态
  disabled?: boolean;
  
  // 标签
  label?: string;
  description?: string;
  
  // 布局
  labelPosition?: 'left' | 'right';
  
  // 自定义样式
  style?: ViewStyle;
  
  // 其他属性
  testID?: string;
}

const Switch: React.FC<SwitchProps> = ({
  value,
  onValueChange,
  size = 'medium',
  color = colors.primary,
  disabled = false,
  label,
  description,
  labelPosition = 'right',
  style,
  testID,
}) => {
  const getSwitchStyle = () => {
    switch (size) {
      case 'small':
        return {
          transform: [{ scaleX: 0.8 }, { scaleY: 0.8 }],
        };
      case 'large':
        return {
          transform: [{ scaleX: 1.2 }, { scaleY: 1.2 }],
        };
      default:
        return {};
    }
  };

  const renderSwitch = () => (
    <RNSwitch
      value={value}
      onValueChange={onValueChange}
      disabled={disabled}
      trackColor={{
        false: colors.gray300,
        true: color,
      }}
      thumbColor={value ? colors.white : colors.gray100}
      ios_backgroundColor={colors.gray300}
      style={getSwitchStyle()}
      testID={testID}
    />
  );

  const renderLabel = () => {
    if (!label && !description) return null;
    
    return (
      <View style={styles.labelContainer}>
        {label && (
          <Text 
            variant="body1" 
            style={disabled ? { ...styles.label, ...styles.disabledText } : styles.label}
          >
            {label}
          </Text>
        )}
        {description && (
          <Text 
            variant="caption" 
            style={disabled ? { ...styles.description, ...styles.disabledText } : styles.description}
          >
            {description}
          </Text>
        )}
      </View>
    );
  };

  const containerStyle = [
    styles.container,
    labelPosition === 'left' && styles.containerReverse,
    style,
  ].filter(Boolean) as ViewStyle[];

  return (
    <View style={containerStyle}>
      {labelPosition === 'left' && renderLabel()}
      {renderSwitch()}
      {labelPosition === 'right' && renderLabel()}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    alignItems: 'center',
    marginVertical: spacing.xs,
  },
  
  containerReverse: {
    justifyContent: 'space-between',
  },
  
  labelContainer: {
    flex: 1,
    marginLeft: spacing.sm,
  },
  
  label: {
    marginBottom: spacing.xs / 2,
  },
  
  description: {
    color: colors.textTertiary,
  },
  
  disabledText: {
    color: colors.gray400,
  },
});

export default Switch; 