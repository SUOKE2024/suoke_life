import { renderHook, act } from "@testing-library/react-native";
import { Alert } from "react-native";
import { useProfile } from "../../hooks/useProfile";
import { HealthAchievement } from "../../types/profile";


// Mock Alert
jest.mock("react-native", () => ({
  Alert: {
    alert: jest.fn(),
  },
}));

const mockAlert = Alert.alert as jest.MockedFunction<typeof Alert.alert>;

describe("useProfile", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it("应该初始化默认状态", () => {
    const { result } = renderHook(() => useProfile());

    expect(result.current.userProfile).toBeDefined();
    expect(result.current.agentInteractions).toHaveLength(4);
    expect(result.current.achievements).toBeDefined();
    expect(result.current.benefits).toBeDefined();
    expect(result.current.activeTab).toBe("agents");
    expect(result.current.loading).toBe(false);
  });

  it("应该正确切换活动标签", () => {
    const { result } = renderHook(() => useProfile());

    act(() => {
      result.current.setActiveTab("achievements");
    });

    expect(result.current.activeTab).toBe("achievements");

    act(() => {
      result.current.setActiveTab("benefits");
    });

    expect(result.current.activeTab).toBe("benefits");
  });

  it("应该正确处理与智能体聊天", () => {
    const { result } = renderHook(() => useProfile());
    const agent = result.current.agentInteractions[0];

    act(() => {
      result.current.chatWithAgent(agent);
    });

    expect(mockAlert).toHaveBeenCalledWith(
      `与${agent.agentName}聊天`,
      expect.stringContaining(agent.agentName),
      expect.any(Array)
    );
  });

  it("应该正确查看成就详情", () => {
    const { result } = renderHook(() => useProfile());
    const achievement = result.current.achievements[0];

    act(() => {
      result.current.viewAchievement(achievement);
    });

    expect(mockAlert).toHaveBeenCalledWith(
      achievement.title,
      expect.stringContaining(achievement.description),
      expect.any(Array)
    );
  });

  it("应该正确使用会员特权", () => {
    const { result } = renderHook(() => useProfile());
    const benefit = result.current.benefits[0];

    act(() => {
      result.current.useBenefit(benefit);
    });

    expect(mockAlert).toHaveBeenCalled();
  });

  it("应该正确处理设置项点击", () => {
    const { result } = renderHook(() => useProfile());

    // 测试退出登录
    act(() => {
      result.current.handleSettingPress("logout");
    });

    expect(mockAlert).toHaveBeenCalledWith(
      "退出登录",
      "确定要退出登录吗？",
      expect.any(Array)
    );
  });

  it("应该正确更新用户资料", async () => {
    const { result } = renderHook(() => useProfile());
    const updates = { name: "新用户名" };

    await act(async () => {
      await result.current.updateProfile(updates);
    });

    expect(result.current.userProfile.name).toBe("新用户名");
    expect(mockAlert).toHaveBeenCalledWith("更新成功", "个人资料已更新");
  });

  it("应该正确获取健康分数颜色", () => {
    const { result } = renderHook(() => useProfile());

    expect(result.current.getHealthScoreColor(90)).toBe("#34C759");
    expect(result.current.getHealthScoreColor(70)).toBe("#FF9500");
    expect(result.current.getHealthScoreColor(50)).toBe("#FF3B30");
  });

  it("应该正确获取会员等级文本", () => {
    const { result } = renderHook(() => useProfile());

    expect(result.current.getMemberLevelText("gold")).toBe("黄金会员");
    expect(result.current.getMemberLevelText("silver")).toBe("白银会员");
    expect(result.current.getMemberLevelText("unknown")).toBe("普通会员");
  });

  it("应该正确计算统计数据", () => {
    const { result } = renderHook(() => useProfile());

    expect(result.current.stats.totalAchievements).toBeGreaterThan(0);
    expect(result.current.stats.unlockedAchievements).toBeGreaterThanOrEqual(0);
    expect(result.current.stats.achievementProgress).toBeGreaterThanOrEqual(0);
    expect(result.current.stats.availableBenefits).toBeGreaterThanOrEqual(0);
  });

  it("应该正确过滤成就", () => {
    const { result } = renderHook(() => useProfile());

    // 过滤已解锁的成就
    const unlockedAchievements = result.current.filterAchievements(
      undefined,
      true
    );
    expect(
      unlockedAchievements.every((a: HealthAchievement) => a.unlocked)
    ).toBe(true);

    // 过滤未解锁的成就
    const lockedAchievements = result.current.filterAchievements(
      undefined,
      false
    );
    expect(
      lockedAchievements.every((a: HealthAchievement) => !a.unlocked)
    ).toBe(true);

    // 按分类过滤
    const healthAchievements = result.current.filterAchievements("health");
    expect(
      healthAchievements.every(
        (a: HealthAchievement) => a.category === "health"
      )
    ).toBe(true);
  });

  it("应该正确获取推荐操作", () => {
    const { result } = renderHook(() => useProfile());

    const recommendations = result.current.getRecommendedActions();
    expect(Array.isArray(recommendations)).toBe(true);
  });
});
