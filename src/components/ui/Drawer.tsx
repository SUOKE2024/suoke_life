import React, { useEffect, useRef } from 'react';
import {
  Animated,
  Dimensions,
  Modal,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
  ViewStyle,
} from 'react-native';
import { useTheme } from '../../contexts/ThemeContext';

export interface DrawerProps {
  visible: boolean;,
  onClose: () => void;,
  children: React.ReactNode;
  position?: 'left' | 'right';
  width?: number;
  overlay?: boolean;
  animationType?: 'slide' | 'fade';
  style?: ViewStyle;
  overlayStyle?: ViewStyle;
  accessible?: boolean;
  accessibilityLabel?: string;
  testID?: string;
}

export const Drawer: React.FC<DrawerProps> = ({
  visible,
  onClose,
  children,
  position = 'left',
  width,
  overlay = true,
  animationType = 'slide',
  style,
  overlayStyle,
  accessible = true,
  accessibilityLabel,
  testID,
}) => {
  const { currentTheme } = useTheme();
  const screenWidth = Dimensions.get('window').width;
  const drawerWidth = width || screenWidth * 0.8;

  const translateX = useRef(
    new Animated.Value(position === 'left' ? -drawerWidth : drawerWidth)
  ).current;
  const overlayOpacity = useRef(new Animated.Value(0)).current;

  useEffect() => {
    if (visible) {
      Animated.parallel([
        Animated.timing(translateX, {
          toValue: 0,
          duration: 300,
          useNativeDriver: true,
        }),
        Animated.timing(overlayOpacity, {
          toValue: 1,
          duration: 300,
          useNativeDriver: true,
        }),
      ]).start();
    } else {
      Animated.parallel([
        Animated.timing(translateX, {
          toValue: position === 'left' ? -drawerWidth : drawerWidth,
          duration: 250,
          useNativeDriver: true,
        }),
        Animated.timing(overlayOpacity, {
          toValue: 0,
          duration: 250,
          useNativeDriver: true,
        }),
      ]).start();
    }
  }, [visible, translateX, overlayOpacity, position, drawerWidth]);

  const styles = StyleSheet.create({
    modal: {,
  flex: 1,
      flexDirection: 'row',
    },
    overlay: {
      ...StyleSheet.absoluteFillObject,
      backgroundColor: 'rgba(0, 0, 0, 0.5)',
      ...overlayStyle,
    },
    drawer: {,
  position: 'absolute',
      top: 0,
      bottom: 0,
      width: drawerWidth,
      backgroundColor: currentTheme.colors.surface,
      shadowColor: currentTheme.colors.shadow,
      shadowOffset: {,
  width: position === 'left' ? 2 : -2,
        height: 0,
      },
      shadowOpacity: 0.25,
      shadowRadius: 8,
      elevation: 16,
      [position]: 0,
      ...style,
    },
    content: {,
  flex: 1,
      paddingTop: 50, // 为状态栏留出空间
    },
    header: {,
  flexDirection: 'row',
      justifyContent: 'space-between',
      alignItems: 'center',
      paddingHorizontal: 16,
      paddingVertical: 12,
      borderBottomWidth: 1,
      borderBottomColor: currentTheme.colors.outline,
    },
    closeButton: {,
  padding: 8,
      borderRadius: 20,
      backgroundColor: currentTheme.colors.surfaceVariant,
    },
    closeButtonText: {,
  fontSize: 18,
      color: currentTheme.colors.onSurface,
    },
  });

  if (!visible) {
    return null;
  }

  return (
    <Modal;
      visible={visible}
      transparent;
      animationType="none"
      onRequestClose={onClose}
      statusBarTranslucent;
    >
      <View style={styles.modal} testID={testID}>
        {overlay && (
          <Animated.View style={[styles.overlay, { opacity: overlayOpacity }]}>
            <TouchableOpacity;
              style={ flex: 1 }}
              activeOpacity={1}
              onPress={onClose}
            />
          </Animated.View>
        )}

        <Animated.View;
          style={[
            styles.drawer,
            {
              transform: [{ translateX }],
            },
          ]}
        >
          <View style={styles.content}>
            <View style={styles.header}>
              <View style={ flex: 1 }} />
              <TouchableOpacity;
                style={styles.closeButton}
                onPress={onClose}
                accessible={accessible}
                accessibilityRole="button"
                accessibilityLabel="关闭抽屉"
              >
                <Text style={styles.closeButtonText}>×</Text>
              </TouchableOpacity>
            </View>
            {children}
          </View>
        </Animated.View>
      </View>
    </Modal>
  );
};

// 抽屉项组件
export interface DrawerItemProps {
  title: string;
  icon?: React.ReactNode;
  onPress?: () => void;
  active?: boolean;
  disabled?: boolean;
  style?: ViewStyle;
  textStyle?: ViewStyle;
  accessible?: boolean;
  accessibilityLabel?: string;
  testID?: string;
}

export const DrawerItem: React.FC<DrawerItemProps> = ({
  title,
  icon,
  onPress,
  active = false,
  disabled = false,
  style,
  textStyle,
  accessible = true,
  accessibilityLabel,
  testID,
}) => {
  const { currentTheme } = useTheme();

  const styles = StyleSheet.create({
    item: {,
  flexDirection: 'row',
      alignItems: 'center',
      paddingHorizontal: 16,
      paddingVertical: 12,
      marginHorizontal: 8,
      marginVertical: 2,
      borderRadius: 8,
      backgroundColor: active;
        ? currentTheme.colors.primary + '20'
        : 'transparent',
    },
    itemDisabled: {,
  opacity: 0.5,
    },
    icon: {,
  marginRight: 12,
      width: 24,
      height: 24,
      justifyContent: 'center',
      alignItems: 'center',
    },
    text: {,
  fontSize: 16,
      color: active;
        ? currentTheme.colors.primary;
        : currentTheme.colors.onSurface,
      flex: 1,
      ...textStyle,
    },
  });

  return (
    <TouchableOpacity;
      style={[styles.item, disabled && styles.itemDisabled, style]}
      onPress={onPress}
      disabled={disabled}
      accessible={accessible}
      accessibilityRole="button"
      accessibilityLabel={accessibilityLabel || title}
      accessibilityState={ selected: active, disabled }}
      testID={testID}
    >
      {icon && <View style={styles.icon}>{icon}</View>}
      <Text style={styles.text}>{title}</Text>
    </TouchableOpacity>
  );
};

// 抽屉分组组件
export interface DrawerSectionProps {
  title?: string;
  children: React.ReactNode;
  style?: ViewStyle;
  titleStyle?: ViewStyle;
}

export const DrawerSection: React.FC<DrawerSectionProps> = ({
  title,
  children,
  style,
  titleStyle,
}) => {
  const { currentTheme } = useTheme();

  const styles = StyleSheet.create({
    section: {,
  marginVertical: 8,
    },
    title: {,
  fontSize: 14,
      fontWeight: '600',
      color: currentTheme.colors.onSurfaceVariant,
      paddingHorizontal: 16,
      paddingVertical: 8,
      textTransform: 'uppercase',
      letterSpacing: 0.5,
      ...titleStyle,
    },
  });

  return (
    <View style={[styles.section, style]}>
      {title && <Text style={styles.title}>{title}</Text>}
      {children}
    </View>
  );
};

export default Drawer;
