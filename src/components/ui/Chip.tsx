import React from 'react';
import {
    StyleSheet,
    Text,
    TextStyle,
    TouchableOpacity,
    View,
    ViewStyle,
} from 'react-native';
import { useTheme } from '../../contexts/ThemeContext';

export interface ChipProps {
  children?: React.ReactNode;
  label?: string;
  selected?: boolean;
  disabled?: boolean;
  variant?: 'filled' | 'outlined' | 'elevated';
  size?: 'small' | 'medium' | 'large';
  color?: 'default' | 'primary' | 'secondary' | 'success' | 'warning' | 'error' | 'info';
  avatar?: React.ReactNode;
  icon?: React.ReactNode;
  deleteIcon?: React.ReactNode;
  onPress?: () => void;
  onDelete?: () => void;
  style?: ViewStyle;
  textStyle?: TextStyle;
  accessible?: boolean;
  testID?: string;
}

export const Chip: React.FC<ChipProps> = ({
  children,
  label,
  selected = false,
  disabled = false,
  variant = 'filled',
  size = 'medium',
  color = 'default',
  avatar,
  icon,
  deleteIcon,
  onPress,
  onDelete,
  style,
  textStyle,
  accessible = true,
  testID,
}) => {
  const { currentTheme } = useTheme();

  const displayText = label || children;

  // 获取颜色配置
  const getColorConfig = () => {
    const baseColors = {
      default: {
        background: currentTheme.colors.surfaceVariant,
        text: currentTheme.colors.onSurfaceVariant,
        border: currentTheme.colors.outline,
      },
      primary: {
        background: currentTheme.colors.primary,
        text: currentTheme.colors.onPrimary,
        border: currentTheme.colors.primary,
      },
      secondary: {
        background: currentTheme.colors.secondary,
        text: currentTheme.colors.onSecondary,
        border: currentTheme.colors.secondary,
      },
      success: {
        background: '#4CAF50',
        text: '#ffffff',
        border: '#4CAF50',
      },
      warning: {
        background: '#FF9800',
        text: '#ffffff',
        border: '#FF9800',
      },
      error: {
        background: currentTheme.colors.error,
        text: '#ffffff',
        border: currentTheme.colors.error,
      },
      info: {
        background: '#2196F3',
        text: '#ffffff',
        border: '#2196F3',
      },
    };

    const colorConfig = baseColors[color];

    switch (variant) {
      case 'outlined':
        return {
          backgroundColor: 'transparent',
          borderColor: colorConfig.border,
          textColor: colorConfig.background,
          borderWidth: 1,
        };
      case 'elevated':
        return {
          backgroundColor: currentTheme.colors.surface,
          borderColor: 'transparent',
          textColor: colorConfig.background,
          borderWidth: 0,
          elevation: 2,
          shadowColor: '#000',
          shadowOffset: { width: 0, height: 2 },
          shadowOpacity: 0.1,
          shadowRadius: 4,
        };
      default: // filled
        return {
          backgroundColor: selected ? colorConfig.background : currentTheme.colors.surfaceVariant,
          borderColor: 'transparent',
          textColor: selected ? colorConfig.text : currentTheme.colors.onSurfaceVariant,
          borderWidth: 0,
        };
    }
  };

  // 获取尺寸配置
  const getSizeConfig = () => {
    switch (size) {
      case 'small':
        return {
          height: 24,
          paddingHorizontal: 8,
          fontSize: 12,
          iconSize: 16,
          borderRadius: 12,
        };
      case 'large':
        return {
          height: 40,
          paddingHorizontal: 16,
          fontSize: 16,
          iconSize: 20,
          borderRadius: 20,
        };
      default: // medium
        return {
          height: 32,
          paddingHorizontal: 12,
          fontSize: 14,
          iconSize: 18,
          borderRadius: 16,
        };
    }
  };

  const colorConfig = getColorConfig();
  const sizeConfig = getSizeConfig();

  const styles = StyleSheet.create({
    container: {
      flexDirection: 'row',
      alignItems: 'center',
      height: sizeConfig.height,
      paddingHorizontal: sizeConfig.paddingHorizontal,
      borderRadius: sizeConfig.borderRadius,
      backgroundColor: colorConfig.backgroundColor,
      borderWidth: colorConfig.borderWidth,
      borderColor: colorConfig.borderColor,
      opacity: disabled ? 0.5 : 1,
      ...(colorConfig.elevation && {
        elevation: colorConfig.elevation,
        shadowColor: colorConfig.shadowColor,
        shadowOffset: colorConfig.shadowOffset,
        shadowOpacity: colorConfig.shadowOpacity,
        shadowRadius: colorConfig.shadowRadius,
      }),
    },
    avatar: {
      marginRight: 6,
      width: sizeConfig.iconSize,
      height: sizeConfig.iconSize,
      borderRadius: sizeConfig.iconSize / 2,
      overflow: 'hidden',
    },
    icon: {
      marginRight: 6,
      width: sizeConfig.iconSize,
      height: sizeConfig.iconSize,
    },
    text: {
      flex: 1,
      fontSize: sizeConfig.fontSize,
      fontWeight: '500',
      color: colorConfig.textColor,
      textAlign: 'center',
    },
    deleteIcon: {
      marginLeft: 6,
      width: sizeConfig.iconSize,
      height: sizeConfig.iconSize,
      justifyContent: 'center',
      alignItems: 'center',
    },
    deleteButton: {
      padding: 2,
      borderRadius: sizeConfig.iconSize / 2,
    },
    deleteText: {
      fontSize: sizeConfig.iconSize - 4,
      color: colorConfig.textColor,
      fontWeight: 'bold',
    },
  });

  const handlePress = () => {
    if (!disabled && onPress) {
      onPress();
    }
  };

  const handleDelete = () => {
    if (!disabled && onDelete) {
      onDelete();
    }
  };

  const renderContent = () => (
    <>
      {avatar && <View style={styles.avatar}>{avatar}</View>}
      {icon && <View style={styles.icon}>{icon}</View>}
      
      <Text style={[styles.text, textStyle]} numberOfLines={1}>
        {displayText}
      </Text>
      
      {(deleteIcon || onDelete) && (
        <TouchableOpacity
          style={[styles.deleteIcon, styles.deleteButton]}
          onPress={handleDelete}
          disabled={disabled}
          accessible={accessible}
          accessibilityRole="button"
          accessibilityLabel="删除标签"
          hitSlop={{ top: 8, bottom: 8, left: 8, right: 8 }}
        >
          {deleteIcon || <Text style={styles.deleteText}>×</Text>}
        </TouchableOpacity>
      )}
    </>
  );

  if (onPress) {
    return (
      <TouchableOpacity
        style={[styles.container, style]}
        onPress={handlePress}
        disabled={disabled}
        accessible={accessible}
        accessibilityRole="button"
        accessibilityLabel={`标签: ${displayText}`}
        accessibilityState={{ selected, disabled }}
        testID={testID}
      >
        {renderContent()}
      </TouchableOpacity>
    );
  }

  return (
    <View
      style={[styles.container, style]}
      accessible={accessible}
      accessibilityRole="text"
      accessibilityLabel={`标签: ${displayText}`}
      testID={testID}
    >
      {renderContent()}
    </View>
  );
};

export default Chip; 