import { HealthData } from "../screens/components/HealthCard";
import { useState, useCallback, useEffect } from "react";



export interface UseHealthDataReturn {
  healthData: HealthData[];
  loading: boolean;
  error: string | null;
  refreshData: () => Promise<void>;
  updateHealthData: (id: string, data: Partial<HealthData>) => void;
  addHealthData: (data: HealthData) => void;
  removeHealthData: (id: string) => void;
  getHealthDataById: (id: string) => HealthData | undefined;
}

// 模拟健康数据
const mockHealthData: HealthData[] = [
  {
    id: "1",
    title: "心率",
    value: 72,
    unit: "bpm",
    icon: "heart-pulse",
    color: "#FF6B6B",
    trend: "stable",
    trendValue: "±2",
    description: "正常范围内",
    status: "normal",
  },
  {
    id: "2",
    title: "血压",
    value: "120/80",
    unit: "mmHg",
    icon: "gauge",
    color: "#4ECDC4",
    trend: "down",
    trendValue: "-5",
    description: "血压有所改善",
    status: "good",
  },
  {
    id: "3",
    title: "体重",
    value: 65.5,
    unit: "kg",
    icon: "scale-bathroom",
    color: "#45B7D1",
    trend: "down",
    trendValue: "-0.5kg",
    description: "体重控制良好",
    status: "good",
  },
  {
    id: "4",
    title: "血糖",
    value: 5.8,
    unit: "mmol/L",
    icon: "water",
    color: "#F7DC6F",
    trend: "up",
    trendValue: "+0.2",
    description: "需要注意饮食",
    status: "warning",
  },
  {
    id: "5",
    title: "睡眠质量",
    value: 85,
    unit: "%",
    icon: "sleep",
    color: "#BB8FCE",
    trend: "up",
    trendValue: "+5%",
    description: "睡眠质量有所提升",
    status: "good",
  },
  {
    id: "6",
    title: "步数",
    value: 8500,
    unit: "步",
    icon: "walk",
    color: "#58D68D",
    trend: "up",
    trendValue: "+500",
    description: "接近目标步数",
    status: "normal",
  },
];

export const useHealthData = (): UseHealthDataReturn => {
  const [healthData, setHealthData] = useState<HealthData[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const refreshData = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      // 模拟API调用
      await new Promise<void>((resolve) => setTimeout(() => resolve(), 1000));

      // 随机更新一些数据以模拟实时变化
      const updatedData = mockHealthData.map((item) => ({
        ...item,
        value:
          typeof item.value === "number"
            ? Math.max(0, item.value + (Math.random() - 0.5) * 2)
            : item.value,
      }));

      setHealthData(updatedData);
    } catch (err) {
      setError("获取健康数据失败");
      console.error("获取健康数据失败:", err);
    } finally {
      setLoading(false);
    }
  }, []);

  const updateHealthData = useCallback(
    (id: string, data: Partial<HealthData>) => {
      setHealthData((prev) =>
        prev.map((item) => (item.id === id ? { ...item, ...data } : item))
      );
    },
    []
  );

  const addHealthData = useCallback((data: HealthData) => {
    setHealthData((prev) => [...prev, data]);
  }, []) // TODO: 检查依赖项; // TODO: 检查依赖项; // TODO: 检查依赖项; // TODO: 检查依赖项;

  const removeHealthData = useCallback((id: string) => {
    setHealthData((prev) => prev.filter((item) => item.id !== id));
  }, []) // TODO: 检查依赖项; // TODO: 检查依赖项; // TODO: 检查依赖项; // TODO: 检查依赖项;

  const getHealthDataById = useCallback(
    (id: string) => {
      return healthData.find((item) => item.id === id);
    },
    [healthData]
  );

  // 初始化数据
  useEffect(() => {
    refreshData();
  }, [refreshData]);

  return {
    healthData,
    loading,
    error,
    refreshData,
    updateHealthData,
    addHealthData,
    removeHealthData,
    getHealthDataById,
  };
};
