import React, { useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ActivityIndicator,
  StatusBar,
} from 'react-native';
import { colors, fonts, spacing } from '../constants/theme';

interface SplashScreenProps {
  onFinish: () => void;
}

export const SplashScreen: React.FC<SplashScreenProps> = ({ onFinish }) => {
  useEffect(() => {
    // 模拟启动加载时间
    const timer = setTimeout(() => {
      onFinish();
    }, 2000);

    return () => clearTimeout(timer);
  }, [onFinish]);

  return (
    <View style={styles.container}>
      <StatusBar barStyle="light-content" backgroundColor={colors.primary} />

      {/* Logo区域 */}
      <View style={styles.logoContainer}>
        <View style={styles.logoPlaceholder}>
          <Text style={styles.logoText}>索克生活</Text>
          <Text style={styles.logoSubtext}>Suoke Life</Text>
        </View>
      </View>

      {/* 加载指示器 */}
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color={colors.white} />
        <Text style={styles.loadingText}>正在启动...</Text>
      </View>

      {/* 版本信息 */}
      <View style={styles.versionContainer}>
        <Text style={styles.versionText}>v1.0.0</Text>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.primary,
    justifyContent: 'center',
    alignItems: 'center',
  },
  logoContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  logoPlaceholder: {
    width: 120,
    height: 120,
    borderRadius: 60,
    backgroundColor: colors.white,
    justifyContent: 'center',
    alignItems: 'center',
    shadowColor: colors.black,
    shadowOffset: {
      width: 0,
      height: 4,
    },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 8,
  },
  logoText: {
    fontSize: 24,
    fontWeight: 'bold',
    color: colors.primary,
    fontFamily: fonts.family.bold,
  },
  logoSubtext: {
    fontSize: 12,
    color: colors.textSecondary,
    marginTop: 4,
    fontFamily: fonts.family.regular,
  },
  loadingContainer: {
    position: 'absolute',
    bottom: 120,
    alignItems: 'center',
  },
  loadingText: {
    color: colors.white,
    fontSize: 16,
    marginTop: spacing.md,
    fontFamily: fonts.family.regular,
  },
  versionContainer: {
    position: 'absolute',
    bottom: spacing.xl,
  },
  versionText: {
    color: colors.white,
    fontSize: 14,
    opacity: 0.8,
    fontFamily: fonts.family.regular,
  },
});
