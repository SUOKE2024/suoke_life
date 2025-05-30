import { renderHook, act } from "@testing-library/react-native";
import { Alert } from "react-native";
import { useLife } from "../../hooks/useLife";
import { LifeSuggestion, LifePlan } from "../../types/life";


// Mock Alert
jest.mock("react-native", () => ({
  Alert: {
    alert: jest.fn(),
  },
}));

const mockAlert = Alert.alert as jest.MockedFunction<typeof Alert.alert>;

describe("useLife", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it("应该初始化默认状态", () => {
    const { result } = renderHook(() => useLife());

    expect(result.current.suggestions).toBeDefined();
    expect(result.current.healthMetrics).toBeDefined();
    expect(result.current.lifePlans).toBeDefined();
    expect(result.current.habits).toBeDefined();
    expect(result.current.goals).toBeDefined();
    expect(result.current.activeTab).toBe("suggestions");
    expect(result.current.loading).toBe(false);
    expect(result.current.refreshing).toBe(false);
  });

  it("应该正确切换活动标签", () => {
    const { result } = renderHook(() => useLife());

    act(() => {
      result.current.setActiveTab("metrics");
    });

    expect(result.current.activeTab).toBe("metrics");

    act(() => {
      result.current.setActiveTab("plans");
    });

    expect(result.current.activeTab).toBe("plans");
  });

  it("应该正确完成建议", () => {
    const { result } = renderHook(() => useLife());
    const suggestion = result.current.suggestions[0];

    act(() => {
      result.current.completeSuggestion(suggestion);
    });

    const updatedSuggestion = result.current.suggestions.find(
      (s) => s.id === suggestion.id
    );
    expect(updatedSuggestion?.completed).toBe(true);
    expect(mockAlert).toHaveBeenCalledWith(
      "建议已完成！",
      expect.stringContaining(suggestion.title),
      expect.any(Array)
    );
  });

  it("应该正确查看建议详情", () => {
    const { result } = renderHook(() => useLife());
    const suggestion = result.current.suggestions[0];

    act(() => {
      result.current.viewSuggestionDetail(suggestion);
    });

    expect(mockAlert).toHaveBeenCalledWith(
      suggestion.title,
      expect.stringContaining(suggestion.description),
      expect.any(Array)
    );
  });

  it("应该正确查看计划详情", () => {
    const { result } = renderHook(() => useLife());
    const plan = result.current.lifePlans[0];

    act(() => {
      result.current.viewPlanDetail(plan);
    });

    expect(mockAlert).toHaveBeenCalledWith(
      plan.title,
      expect.stringContaining(plan.description),
      expect.any(Array)
    );
  });

  it("应该正确执行计划行动", () => {
    const { result } = renderHook(() => useLife());
    const plan = result.current.lifePlans[0];
    const initialProgress = plan.progress;

    act(() => {
      result.current.executePlanAction(plan);
    });

    expect(mockAlert).toHaveBeenCalledWith(
      "执行行动",
      expect.stringContaining(plan.nextAction),
      expect.any(Array)
    );
  });

  it("应该正确获取分类文本", () => {
    const { result } = renderHook(() => useLife());

    expect(result.current.getCategoryText("diet")).toBe("饮食");
    expect(result.current.getCategoryText("exercise")).toBe("运动");
    expect(result.current.getCategoryText("sleep")).toBe("睡眠");
    expect(result.current.getCategoryText("unknown")).toBe("unknown");
  });

  it("应该正确获取优先级文本和颜色", () => {
    const { result } = renderHook(() => useLife());

    expect(result.current.getPriorityText("high")).toBe("高");
    expect(result.current.getPriorityText("medium")).toBe("中");
    expect(result.current.getPriorityText("low")).toBe("低");

    expect(result.current.getPriorityColor("high")).toBe("#FF3B30");
    expect(result.current.getPriorityColor("medium")).toBe("#FF9500");
    expect(result.current.getPriorityColor("low")).toBe("#34C759");
  });

  it("应该正确获取趋势图标", () => {
    const { result } = renderHook(() => useLife());

    expect(result.current.getTrendIcon("up")).toBe("trending-up");
    expect(result.current.getTrendIcon("down")).toBe("trending-down");
    expect(result.current.getTrendIcon("stable")).toBe("trending-neutral");
    expect(result.current.getTrendIcon("unknown")).toBe("trending-neutral");
  });

  it("应该正确刷新数据", async () => {
    const { result } = renderHook(() => useLife());

    await act(async () => {
      await result.current.refreshData();
    });

    expect(mockAlert).toHaveBeenCalledWith("刷新成功", "数据已更新");
  });

  it("应该正确过滤建议", () => {
    const { result } = renderHook(() => useLife());

    // 按分类过滤
    const dietSuggestions = result.current.filterSuggestions("diet");
    expect(
      dietSuggestions.every((s: LifeSuggestion) => s.category === "diet")
    ).toBe(true);

    // 按优先级过滤
    const highPrioritySuggestions = result.current.filterSuggestions(
      undefined,
      "high"
    );
    expect(
      highPrioritySuggestions.every(
        (s: LifeSuggestion) => s.priority === "high"
      )
    ).toBe(true);

    // 按完成状态过滤
    const completedSuggestions = result.current.filterSuggestions(
      undefined,
      undefined,
      true
    );
    expect(
      completedSuggestions.every((s: LifeSuggestion) => s.completed === true)
    ).toBe(true);
  });

  it("应该正确获取今日建议", () => {
    const { result } = renderHook(() => useLife());

    const todaySuggestions = result.current.getTodaySuggestions();
    expect(Array.isArray(todaySuggestions)).toBe(true);
    expect(todaySuggestions.length).toBeLessThanOrEqual(3);
    expect(
      todaySuggestions.every(
        (s: LifeSuggestion) => !s.completed && s.priority === "high"
      )
    ).toBe(true);
  });

  it("应该正确获取推荐行动", () => {
    const { result } = renderHook(() => useLife());

    const recommendations = result.current.getRecommendedActions();
    expect(Array.isArray(recommendations)).toBe(true);
  });

  it("应该正确更新健康指标", () => {
    const { result } = renderHook(() => useLife());
    const metric = result.current.healthMetrics[0];
    const newValue = 95;

    act(() => {
      result.current.updateHealthMetric(metric.id, newValue);
    });

    const updatedMetric = result.current.healthMetrics.find(
      (m) => m.id === metric.id
    );
    expect(updatedMetric?.value).toBe(newValue);
  });

  it("应该正确计算统计数据", () => {
    const { result } = renderHook(() => useLife());

    expect(result.current.stats.totalSuggestions).toBeGreaterThan(0);
    expect(result.current.stats.completedSuggestions).toBeGreaterThanOrEqual(0);
    expect(result.current.stats.completionRate).toBeGreaterThanOrEqual(0);
    expect(result.current.stats.activePlans).toBeGreaterThanOrEqual(0);
    expect(result.current.stats.completedPlans).toBeGreaterThanOrEqual(0);
  });
});
