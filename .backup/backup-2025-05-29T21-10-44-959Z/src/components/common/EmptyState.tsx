import {
import Icon from './Icon';
import { colors, spacing, fonts } from '../../constants/theme';



import React, { memo } from 'react';
  View,
  Text,
  StyleSheet,
} from 'react-native';

interface EmptyStateProps {
  icon: string;
  title: string;
  subtitle?: string;
  style?: any;
}

export const EmptyState = memo<EmptyStateProps>(({
  icon,
  title,
  subtitle,
  style,
}) => {
  return (
    <View style={[styles.container, style]}>
      <Icon name={icon} size={64} color={colors.textSecondary} />
      <Text style={styles.title}>{title}</Text>
      {subtitle && <Text style={styles.subtitle}>{subtitle}</Text>}
    </View>
  );
});

EmptyState.displayName = 'EmptyState';

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: spacing.xl,
    paddingVertical: spacing.xxl,
  },
  title: {
    fontSize: fonts.size.lg,
    fontWeight: '600',
    color: colors.text,
    textAlign: 'center',
    marginTop: spacing.lg,
    marginBottom: spacing.sm,
  },
  subtitle: {
    fontSize: fonts.size.md,
    color: colors.textSecondary,
    textAlign: 'center',
    lineHeight: fonts.lineHeight.md,
  },
}); 