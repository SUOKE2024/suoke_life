import { SafeAreaView } from 'react-native-safe-area-context';
import Icon from '../../components/common/Icon';
import { colors, spacing, fonts } from '../../constants/theme';


import React from 'react';
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  StatusBar,
  ViewStyle,
} from 'react-native';

interface ScreenHeaderProps {
  title: string;
  subtitle?: string;
  leftIcon?: string;
  rightIcon?: string;
  onLeftPress?: () => void;
  onRightPress?: () => void;
  backgroundColor?: string;
  textColor?: string;
  showBackButton?: boolean;
  style?: ViewStyle;
  centerComponent?: React.ReactNode;
  rightComponent?: React.ReactNode;
}

export const ScreenHeader: React.FC<ScreenHeaderProps> = ({
  title,
  subtitle,
  leftIcon,
  rightIcon,
  onLeftPress,
  onRightPress,
  backgroundColor = colors.surface,
  textColor = colors.text,
  showBackButton = false,
  style,
  centerComponent,
  rightComponent,
}) => {
  const isDark = backgroundColor === colors.primary || backgroundColor === colors.primaryDark;

  return (
    <SafeAreaView style={[styles.container, { backgroundColor }, style]}>
      <StatusBar
        barStyle={isDark ? 'light-content' : 'dark-content'}
        backgroundColor={backgroundColor}
      />
      
      <View style={styles.header}>
        {/* 左侧按钮 */}
        <View style={styles.leftSection}>
          {(showBackButton || leftIcon || onLeftPress) && (
            <TouchableOpacity
              style={styles.iconButton}
              onPress={onLeftPress}
              activeOpacity={0.7}
            >
              <Icon
                name={leftIcon || (showBackButton ? 'arrow-left' : 'menu')}
                size={24}
                color={isDark ? colors.white : textColor}
              />
            </TouchableOpacity>
          )}
        </View>

        {/* 中间内容 */}
        <View style={styles.centerSection}>
          {centerComponent || (
            <View style={styles.titleContainer}>
              <Text
                style={[
                  styles.title,
                  { color: isDark ? colors.white : textColor },
                ]}
                numberOfLines={1}
              >
                {title}
              </Text>
              {subtitle && (
                <Text
                  style={[
                    styles.subtitle,
                    { color: isDark ? colors.white : colors.textSecondary },
                  ]}
                  numberOfLines={1}
                >
                  {subtitle}
                </Text>
              )}
            </View>
          )}
        </View>

        {/* 右侧按钮 */}
        <View style={styles.rightSection}>
          {rightComponent || (
            (rightIcon || onRightPress) && (
              <TouchableOpacity
                style={styles.iconButton}
                onPress={onRightPress}
                activeOpacity={0.7}
              >
                <Icon
                  name={rightIcon || 'dots-vertical'}
                  size={24}
                  color={isDark ? colors.white : textColor}
                />
              </TouchableOpacity>
            )
          )}
        </View>
      </View>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    shadowColor: colors.black,
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 3,
    elevation: 4,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    minHeight: 56,
  },
  leftSection: {
    width: 48,
    alignItems: 'flex-start',
  },
  centerSection: {
    flex: 1,
    alignItems: 'center',
    paddingHorizontal: spacing.sm,
  },
  rightSection: {
    width: 48,
    alignItems: 'flex-end',
  },
  iconButton: {
    width: 40,
    height: 40,
    borderRadius: 20,
    justifyContent: 'center',
    alignItems: 'center',
  },
  titleContainer: {
    alignItems: 'center',
  },
  title: {
    fontSize: fonts.size.lg,
    fontWeight: 'bold',
    textAlign: 'center',
  },
  subtitle: {
    fontSize: fonts.size.sm,
    textAlign: 'center',
    marginTop: 2,
  },
}); 