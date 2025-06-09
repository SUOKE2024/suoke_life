import React from 'react';
import { View, StyleSheet, Animated, Dimensions } from 'react-native';
const { width: screenWidth } = Dimensions.get('window');
interface SkeletonLoaderProps {
  type?: 'list' | 'card' | 'profile' | 'chat' | 'custom';
  count?: number;
  height?: number;
  width?: number;
  style?: any;
  children?: React.ReactNode;
}
// 骨架屏动画组件
const SkeletonItem: React.FC<{,
  width: number;
  height: number;
  borderRadius?: number;
  style?: any;
}> = ({ width, height, borderRadius = 4, style }) => {
  const animatedValue = React.useRef(new Animated.Value(0)).current;
  React.useEffect() => {
    const animation = Animated.loop()
      Animated.sequence([)
        Animated.timing(animatedValue, {
          toValue: 1,
          duration: 1000,
          useNativeDriver: false}),
        Animated.timing(animatedValue, {
          toValue: 0,
          duration: 1000,
          useNativeDriver: false})])
    );
    animation.start();
    return () => animation.stop();
  }, [animatedValue]);
  const backgroundColor = animatedValue.interpolate({
    inputRange: [0, 1],
    outputRange: ["#E1E9EE",#F2F8FC']});
  return (
  <Animated.View;
      style={[
        {
          width,
          height,
          backgroundColor,
          borderRadius}},
        style]}
    />
  );
};
// 聊天列表骨架屏
const ChatListSkeleton: React.FC<{ count: number }> = ({ count }) => {
  return (
  <View style={styles.container}>
      {Array.from({ length: count }).map(_, index) => ())
        <View key={index} style={styles.chatItem}>
          {}
          <SkeletonItem width={50} height={50} borderRadius={25} />
                    <View style={styles.chatContent}>
            {}
            <SkeletonItem width={120} height={16} style={ marginBottom: 8 }} />
            {}
            <SkeletonItem width={200} height={14} />
          </View>
                    <View style={styles.chatMeta}>
            {}
            <SkeletonItem width={40} height={12} style={ marginBottom: 8 }} />
            {}
            <SkeletonItem width={20} height={20} borderRadius={10} />
          </View>
        </View>
      ))}
    </View>
  );
};
// 卡片列表骨架屏
const CardListSkeleton: React.FC<{ count: number }> = ({ count }) => {
  return (
  <View style={styles.container}>
      {Array.from({ length: count }).map(_, index) => ())
        <View key={index} style={styles.cardItem}>
          {}
          <SkeletonItem width={screenWidth - 32} height={120} style={ marginBottom: 12 }} />
                    {}
          <SkeletonItem width={screenWidth - 64} height={18} style={ marginBottom: 8 }} />
                    {}
          <SkeletonItem width={screenWidth - 80} height={14} style={ marginBottom: 4 }} />
          <SkeletonItem width={screenWidth - 120} height={14} />
        </View>
      ))}
    </View>
  );
};
// 个人资料骨架屏
const ProfileSkeleton: React.FC = () => {
  return (
  <View style={styles.container}>
      <View style={styles.profileHeader}>
        {}
        <SkeletonItem width={80} height={80} borderRadius={40} style={ marginBottom: 16 }} />
                {}
        <SkeletonItem width={120} height={20} style={ marginBottom: 8 }} />
                {}
        <SkeletonItem width={200} height={16} />
      </View>
            {}
      <View style={styles.profileStats}>
        {Array.from({ length: 3 }).map(_, index) => ())
          <View key={index} style={styles.statItem}>
            <SkeletonItem width={40} height={24} style={ marginBottom: 4 }} />
            <SkeletonItem width={60} height={14} />
          </View>
        ))}
      </View>
            {}
      {Array.from({ length: 5 }).map(_, index) => ())
        <View key={index} style={styles.menuItem}>
          <SkeletonItem width={24} height={24} />
          <SkeletonItem width={100} height={16} style={ marginLeft: 12 }} />
        </View>
      ))}
    </View>
  );
};
// 列表骨架屏
const ListSkeleton: React.FC<{ count: number; height: number }> = ({ count, height }) => {
  return (
  <View style={styles.container}>
      {Array.from({ length: count }).map(_, index) => ())
        <View key={index} style={[styles.listItem, { height }}]}>
          <SkeletonItem width={screenWidth - 32} height={height - 16} />
        </View>
      ))}
    </View>
  );
};
// 主骨架屏组件
const SkeletonLoader: React.FC<SkeletonLoaderProps> = ({
  type = 'list',
  count = 5,
  height = 60,
  width = screenWidth - 32,
  style,
  children}) => {
  if (children) {
    return <View style={[styles.container, style]}>{children}</View>;
  }
  switch (type) {
    case 'chat':
      return <ChatListSkeleton count={count} />;
    case 'card':
      return <CardListSkeleton count={count} />;
    case 'profile':
      return <ProfileSkeleton />;
    case 'list':
    default:
      return <ListSkeleton count={count} height={height} />;
  }
};
const styles = StyleSheet.create({
  container: {,
  flex: 1,
    padding: 16},
  chatItem: {,
  flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#F0F0F0'},
  chatContent: {,
  flex: 1,
    marginLeft: 12},
  chatMeta: {,
  alignItems: 'flex-end'},
  cardItem: {,
  marginBottom: 20,
    padding: 16,
    backgroundColor: '#FFFFFF',
    borderRadius: 8,
    shadowColor: '#000',
    shadowOffset: {,
  width: 0,
      height: 2},
    shadowOpacity: 0.1,
    shadowRadius: 3.84,
    elevation: 5},
  profileHeader: {,
  alignItems: 'center',
    paddingVertical: 24},
  profileStats: {,
  flexDirection: 'row',
    justifyContent: 'space-around',
    paddingVertical: 20,
    borderBottomWidth: 1,
    borderBottomColor: '#F0F0F0'},
  statItem: {,
  alignItems: 'center'},
  menuItem: {,
  flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#F0F0F0'},
  listItem: {,
  marginBottom: 8,
    padding: 8}});
export default SkeletonLoader;