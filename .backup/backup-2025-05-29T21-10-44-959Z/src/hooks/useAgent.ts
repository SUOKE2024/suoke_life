import { AgentType, AGENTS } from "../screens/components/AgentCard";
import { useState, useCallback } from "react";


export interface UseAgentReturn {
  selectedAgent: AgentType;
  setSelectedAgent: (agent: AgentType) => void;
  switchAgent: (agent: AgentType) => void;
  getAgentInfo: (agent: AgentType) => (typeof AGENTS)[AgentType];
  generateAgentResponse: (userInput: string, agent: AgentType) => string;
}

export const useAgent = (
  initialAgent: AgentType = "xiaoai"
): UseAgentReturn => {
  const [selectedAgent, setSelectedAgent] = useState<AgentType>(initialAgent);

  const switchAgent = useCallback((agent: AgentType) => {
    setSelectedAgent(agent);
  }, []) // TODO: 检查依赖项; // TODO: 检查依赖项; // TODO: 检查依赖项;

  const getAgentInfo = useCallback((agent: AgentType) => {
    return AGENTS[agent];
  }, []) // TODO: 检查依赖项; // TODO: 检查依赖项; // TODO: 检查依赖项;

  const generateAgentResponse = useCallback(
    (userInput: string, agent: AgentType): string => {
      const responses = {
        xiaoai: [
          "我理解您的关注。让我为您分析一下健康状况。",
          "根据您的描述，我建议您注意以下几点...",
          "这是一个很好的问题！让我为您详细解答。",
          "基于AI分析，您的健康指标显示...",
          "我建议您进行以下健康管理措施...",
        ],
        xiaoke: [
          "从医学角度来看，您的症状需要进一步评估。",
          "建议您进行相关检查，我可以为您制定诊断方案。",
          "这种情况在临床上比较常见，不用过于担心。",
          "根据中医五诊的结果，我建议...",
          "让我为您进行专业的健康评估...",
        ],
        laoke: [
          "从中医的角度来看，这可能与您的体质有关。",
          "建议您调理气血，注意饮食起居。",
          "中医讲究辨证论治，让我为您分析一下证型。",
          "根据传统中医理论，您的情况属于...",
          "建议您采用中医调理的方法...",
        ],
        soer: [
          "生活中的小细节很重要呢！让我给您一些建议。",
          "我觉得您可以尝试这样的生活方式调整。",
          "健康的生活习惯是最好的良药哦！",
          "让我为您推荐一些健康的生活方式...",
          "从营养学角度来看，您可以这样改善...",
        ],
      };

      const agentResponses = responses[agent];
      const randomIndex = Math.floor(Math.random() * agentResponses.length);
      return agentResponses[randomIndex];
    },
    []
  );

  return {
    selectedAgent,
    setSelectedAgent,
    switchAgent,
    getAgentInfo,
    generateAgentResponse,
  };
};
