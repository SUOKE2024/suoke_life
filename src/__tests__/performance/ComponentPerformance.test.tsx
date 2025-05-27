import React from 'react';
import { render } from '@testing-library/react-native';
import ProfileHeader from '../../screens/components/ProfileHeader';
import HealthMetricCard from '../../screens/components/HealthMetricCard';
import { UserProfile } from '../../types/profile';
import { HealthMetric } from '../../types/life';

// Mock数据
const mockUserProfile: UserProfile = {
  id: 'test_user',
  name: '测试用户',
  avatar: '👤',
  age: 28,
  gender: 'male',
  constitution: '气虚质',
  memberLevel: 'gold',
  joinDate: '2023-03-15',
  healthScore: 85,
  totalDiagnosis: 24,
  consecutiveDays: 15,
  healthPoints: 1280,
  email: 'test@example.com',
  phone: '+86 138 0013 8000',
  location: '北京市朝阳区',
  bio: '测试用户简介',
};

const mockHealthMetric: HealthMetric = {
  id: 'mood',
  name: '心情指数',
  value: 85,
  unit: '分',
  target: 80,
  icon: 'emoticon-happy',
  color: '#FF9500',
  trend: 'up',
  suggestion: '保持积极心态，今天心情不错！',
};

const mockGetHealthScoreColor = (score: number) => '#34C759';
const mockGetMemberLevelText = (level: string) => '黄金会员';
const mockGetTrendIcon = (trend: string) => 'trending-up';

describe('Component Performance Tests', () => {
  const measureRenderTime = (renderFn: () => void): number => {
    const start = Date.now();
    renderFn();
    const end = Date.now();
    return end - start;
  };

  it('ProfileHeader应该在合理时间内渲染', () => {
    const renderTime = measureRenderTime(() => {
      render(
        <ProfileHeader
          userProfile={mockUserProfile}
          onEditPress={() => {}}
          getHealthScoreColor={mockGetHealthScoreColor}
          getMemberLevelText={mockGetMemberLevelText}
        />
      );
    });

    // 期望渲染时间小于150ms（考虑到测试环境的性能差异）
    expect(renderTime).toBeLessThan(150);
  });

  it('HealthMetricCard应该在合理时间内渲染', () => {
    const renderTime = measureRenderTime(() => {
      render(
        <HealthMetricCard
          metric={mockHealthMetric}
          getTrendIcon={mockGetTrendIcon}
        />
      );
    });

    // 期望渲染时间小于50ms
    expect(renderTime).toBeLessThan(50);
  });

  it('多个ProfileHeader组件应该高效渲染', () => {
    const renderTime = measureRenderTime(() => {
      for (let i = 0; i < 10; i++) {
        render(
          <ProfileHeader
            userProfile={mockUserProfile}
            onEditPress={() => {}}
            getHealthScoreColor={mockGetHealthScoreColor}
            getMemberLevelText={mockGetMemberLevelText}
          />
        );
      }
    });

    // 期望10个组件的渲染时间小于500ms
    expect(renderTime).toBeLessThan(500);
  });

  it('多个HealthMetricCard组件应该高效渲染', () => {
    const renderTime = measureRenderTime(() => {
      for (let i = 0; i < 20; i++) {
        render(
          <HealthMetricCard
            metric={{
              ...mockHealthMetric,
              id: `metric_${i}`,
              name: `指标${i}`,
            }}
            getTrendIcon={mockGetTrendIcon}
          />
        );
      }
    });

    // 期望20个组件的渲染时间小于800ms
    expect(renderTime).toBeLessThan(800);
  });

  it('组件重新渲染应该高效', () => {
    const { rerender } = render(
      <ProfileHeader
        userProfile={mockUserProfile}
        onEditPress={() => {}}
        getHealthScoreColor={mockGetHealthScoreColor}
        getMemberLevelText={mockGetMemberLevelText}
      />
    );

    const rerenderTime = measureRenderTime(() => {
      for (let i = 0; i < 5; i++) {
        rerender(
          <ProfileHeader
            userProfile={{
              ...mockUserProfile,
              healthScore: 85 + i,
            }}
            onEditPress={() => {}}
            getHealthScoreColor={mockGetHealthScoreColor}
            getMemberLevelText={mockGetMemberLevelText}
          />
        );
      }
    });

    // 期望5次重新渲染时间小于100ms
    expect(rerenderTime).toBeLessThan(100);
  });

  it('组件卸载应该正常工作', () => {
    // 测试组件的正常卸载
    const components = [];
    
    // 渲染大量组件
    for (let i = 0; i < 50; i++) {
      const { unmount } = render(
        <ProfileHeader
          userProfile={mockUserProfile}
          onEditPress={() => {}}
          getHealthScoreColor={mockGetHealthScoreColor}
          getMemberLevelText={mockGetMemberLevelText}
        />
      );
      components.push(unmount);
    }

    // 卸载所有组件
    components.forEach(unmount => {
      expect(() => unmount()).not.toThrow();
    });

    // 验证组件数量
    expect(components.length).toBe(50);
  });
}); 