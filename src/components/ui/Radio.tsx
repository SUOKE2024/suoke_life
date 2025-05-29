/**
 * 索克生活 - Radio组件
 * 单选框组件，用于单选操作
 */

import React from 'react';
import { TouchableOpacity, View, StyleSheet, ViewStyle } from 'react-native';
import { colors, spacing } from '../../constants/theme';
import Text from './Text';

export interface RadioProps {
  // 基础属性
  selected: boolean;
  onPress: () => void;
  value?: string | number;
  
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

const Radio: React.FC<RadioProps> = ({
  selected,
  onPress,
  size = 'medium',
  color = colors.primary,
  disabled = false,
  label,
  description,
  labelPosition = 'right',
  style,
  testID,
}) => {
  const getRadioSize = () => {
    switch (size) {
      case 'small':
        return 16;
      case 'large':
        return 24;
      default:
        return 20;
    }
  };

  const radioSize = getRadioSize();

  const handlePress = () => {
    if (!disabled) {
      onPress();
    }
  };

  const getRadioStyle = () => {
    const baseStyle = {
      width: radioSize,
      height: radioSize,
      borderRadius: radioSize / 2,
      borderWidth: 2,
      alignItems: 'center' as const,
      justifyContent: 'center' as const,
    };

    if (disabled) {
      return {
        ...baseStyle,
        backgroundColor: colors.gray100,
        borderColor: colors.gray300,
      };
    }

    if (selected) {
      return {
        ...baseStyle,
        backgroundColor: colors.surface,
        borderColor: color,
      };
    }

    return {
      ...baseStyle,
      backgroundColor: colors.surface,
      borderColor: colors.border,
    };
  };

  const renderDot = () => {
    if (selected) {
      return (
        <View
          style={{
            width: radioSize * 0.5,
            height: radioSize * 0.5,
            borderRadius: (radioSize * 0.5) / 2,
            backgroundColor: disabled ? colors.gray400 : color,
          }}
        />
      );
    }
    return null;
  };

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
    <TouchableOpacity
      style={containerStyle}
      onPress={handlePress}
      disabled={disabled}
      activeOpacity={0.7}
      testID={testID}
    >
      {labelPosition === 'left' && renderLabel()}
      <View style={getRadioStyle()}>
        {renderDot()}
      </View>
      {labelPosition === 'right' && renderLabel()}
    </TouchableOpacity>
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

export default Radio; 