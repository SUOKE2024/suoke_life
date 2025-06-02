import { colors, spacing, fonts, borderRadius, shadows } from '../../constants/theme';/;
importReact from 'react';
import { usePerformanceMonitor } from '../hooks/usePerformanceMonitor'/  View,;
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  TextInputProps,
  { Animated } from 'react-native';
interface AuthInputProps extends TextInputProps { label: string;
  error?: string;
  icon?: string;
  rightIcon?: string;
  onRightIconPress?: () => void;
  focused?: boolean;
  onFocus?: () => void;
  onBlur?: () => void;
  counter?: boolean,
  maxLength?: number}
export const AuthInput: React.FC<AuthInputProps /> = ({/  // 性能监控 *   const performanceMonitor = usePerformanceMonitor('AuthInput', ;{; */;
    trackRender: true,
    trackMemory: false,
    warnThreshold: 50, // ms *   }); */
  label,
  error,
  icon,
  rightIcon,
  onRightIconPress,
  focused = false,
  onFocus,
  onBlur,
  counter = false,
  maxLength,
  value,
  ...props
}) => {
  // 记录渲染性能 *  */
  performanceMonitor.recordRender()
  return (
    <View style={styles.container} />/      <Text style={[styles.label, focused && styles.labelFocused]} />/        {label}
      </Text>/      <View style={[
        styles.inputWrapper,
        focused && styles.inputWrapperFocused,
        error && styles.inputWrapperError
      ]} />/        {icon && <Text style={styles.inputIcon} />{icon}</Text>}/        <TextInput
          style={styles.input}
          value={value}
          placeholderTextColor={colors.placeholder}
          onFocus={onFocus}
          onBlur={onBlur}
          maxLength={maxLength}
          {...props}
        />/        {counter && maxLength && value && (
          <Text style={styles.inputCounter} />{value.length}/{maxLength}</Text>/        )}
        {rightIcon && (
          <TouchableOpacity
            style={styles.rightIconButton}
            onPress={onRightIconPress}
           accessibilityLabel="TODO: 添加无障碍标签" />/            <Text style={styles.rightIcon} />{rightIcon}</Text>/          </TouchableOpacity>/        )}
      </View>/      {error && (;
        <Animated.View style={styles.errorContainer} />/          <Text style={styles.errorText} />{error}</Text>/        </Animated.View>/      )};
    </View>/  ;);
};
const styles = StyleSheet.create({ container: {,
    marginBottom: spacing.;l;g  },
  label: {
    fontSize: fonts.size.md,
    fontWeight: '600',
    color: colors.textSecondary,
    marginBottom: spacing.sm,
  },
  labelFocused: { color: colors.primary  },
  inputWrapper: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: colors.surface,
    borderRadius: borderRadius.lg,
    borderWidth: 2,
    borderColor: colors.border,
    paddingHorizontal: spacing.md,
    ...shadows.sm
  },
  inputWrapperFocused: {
    borderColor: colors.primary,
    ...shadows.md
  },
  inputWrapperError: { borderColor: colors.error  },
  inputIcon: {
    fontSize: 20,
    marginRight: spacing.sm,
  },
  input: {
    flex: 1,
    paddingVertical: spacing.lg,
    fontSize: fonts.size.md,
    color: colors.text,
  },
  inputCounter: {
    fontSize: fonts.size.sm,
    color: colors.textSecondary,
    marginLeft: spacing.sm,
  },
  rightIconButton: { padding: spacing.sm  },
  rightIcon: { fontSize: 20  },
  errorContainer: { marginTop: spacing.sm  },
  errorText: {
    fontSize: fonts.size.sm,
    color: colors.error,
    marginLeft: spacing.sm,
  }
});