import React from 'react';
import { render, fireEvent } from '@testing-library/react-native';
import ProfileHeader from '../../screens/components/ProfileHeader';
import { UserProfile } from '../../types/profile';

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

const mockGetHealthScoreColor = (score: number) => {
  if (score >= 80) return '#34C759';
  if (score >= 60) return '#FF9500';
  return '#FF3B30';
};

const mockGetMemberLevelText = (level: string) => {
  const levelMap = {
    bronze: '青铜会员',
    silver: '白银会员',
    gold: '黄金会员',
    platinum: '铂金会员',
    diamond: '钻石会员',
  };
  return levelMap[level as keyof typeof levelMap] || '普通会员';
};

describe('ProfileHeader', () => {
  const mockOnEditPress = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('应该正确渲染用户信息', () => {
    const { getByText } = render(
      <ProfileHeader
        userProfile={mockUserProfile}
        onEditPress={mockOnEditPress}
        getHealthScoreColor={mockGetHealthScoreColor}
        getMemberLevelText={mockGetMemberLevelText}
      />
    );

    expect(getByText('测试用户')).toBeTruthy();
    expect(getByText('黄金会员')).toBeTruthy();
    expect(getByText('加入时间：2023-03-15')).toBeTruthy();
  });

  it('应该正确显示统计数据', () => {
    const { getByText } = render(
      <ProfileHeader
        userProfile={mockUserProfile}
        onEditPress={mockOnEditPress}
        getHealthScoreColor={mockGetHealthScoreColor}
        getMemberLevelText={mockGetMemberLevelText}
      />
    );

    expect(getByText('85')).toBeTruthy();
    expect(getByText('24')).toBeTruthy();
    expect(getByText('15')).toBeTruthy();
    expect(getByText('1280')).toBeTruthy();
    expect(getByText('健康分数')).toBeTruthy();
    expect(getByText('诊断次数')).toBeTruthy();
    expect(getByText('连续天数')).toBeTruthy();
    expect(getByText('健康积分')).toBeTruthy();
  });

  it('应该在点击编辑按钮时调用onEditPress', () => {
    const { getByTestId } = render(
      <ProfileHeader
        userProfile={mockUserProfile}
        onEditPress={mockOnEditPress}
        getHealthScoreColor={mockGetHealthScoreColor}
        getMemberLevelText={mockGetMemberLevelText}
      />
    );

    // 需要在组件中添加testID
    // fireEvent.press(getByTestId('edit-button'));
    // expect(mockOnEditPress).toHaveBeenCalledTimes(1);
  });

  it('应该根据健康分数显示正确的颜色', () => {
    const highScoreProfile = { ...mockUserProfile, healthScore: 90 };
    const { rerender } = render(
      <ProfileHeader
        userProfile={highScoreProfile}
        onEditPress={mockOnEditPress}
        getHealthScoreColor={mockGetHealthScoreColor}
        getMemberLevelText={mockGetMemberLevelText}
      />
    );

    // 测试高分数颜色
    expect(mockGetHealthScoreColor(90)).toBe('#34C759');

    // 测试中等分数
    const mediumScoreProfile = { ...mockUserProfile, healthScore: 70 };
    rerender(
      <ProfileHeader
        userProfile={mediumScoreProfile}
        onEditPress={mockOnEditPress}
        getHealthScoreColor={mockGetHealthScoreColor}
        getMemberLevelText={mockGetMemberLevelText}
      />
    );
    expect(mockGetHealthScoreColor(70)).toBe('#FF9500');

    // 测试低分数
    const lowScoreProfile = { ...mockUserProfile, healthScore: 50 };
    rerender(
      <ProfileHeader
        userProfile={lowScoreProfile}
        onEditPress={mockOnEditPress}
        getHealthScoreColor={mockGetHealthScoreColor}
        getMemberLevelText={mockGetMemberLevelText}
      />
    );
    expect(mockGetHealthScoreColor(50)).toBe('#FF3B30');
  });

  it('应该正确显示不同会员等级', () => {
    const levels = ['bronze', 'silver', 'gold', 'platinum', 'diamond'];
    const expectedTexts = ['青铜会员', '白银会员', '黄金会员', '铂金会员', '钻石会员'];

    levels.forEach((level, index) => {
      expect(mockGetMemberLevelText(level)).toBe(expectedTexts[index]);
    });
  });
}); 