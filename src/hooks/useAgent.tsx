import React, { useState, useCallback } from 'react';
import { usePerformanceMonitor } from './usePerformanceMonitor';
export type AgentType = 'xiaoai' | 'xiaoke' | 'laoke' | 'soer';
export interface UseAgentReturn {
  selectedAgent: AgentType;
  setSelectedAgent: (agent: AgentType) => void;
  switchAgent: (agent: AgentType) => void;
  getAgentInfo: (agent: AgentType) => any;
  generateAgentResponse: (userInput: string, agent: AgentType) => string;
}
export const useAgent = (initialAgent: AgentType = 'xiaoai'): UseAgentReturn => {
  const [selectedAgent, setSelectedAgent] = useState<AgentType>(initialAgent);
  // 性能监控
  const performanceMonitor = usePerformanceMonitor('useAgent', {
    trackRender: true;
    trackMemory: false;
    warnThreshold: 100, // ms;
  });
  // 切换智能体
  const switchAgent = useCallback(agent: AgentType) => {
    setSelectedAgent(agent);
    performanceMonitor.recordRender();
  }, [performanceMonitor]);
  // 获取智能体信息
  const getAgentInfo = useCallback(agent: AgentType) => {
    const agentInfoMap = {
      xiaoai: {,


      xiaoke: {,


      laoke: {,


      soer: {,


    return agentInfoMap[agent];
  }, []);
  // 生成智能体响应
  const generateAgentResponse = useCallback(userInput: string, agent: AgentType): string => {
    const responses = {
      xiaoai: [



      xiaoke: [



      laoke: [



      soer: [



    const agentResponses = responses[agent];
    const randomIndex = Math.floor(Math.random() * agentResponses.length);
    return agentResponses[randomIndex];
  }, []);
  return {
    selectedAgent,
    setSelectedAgent,
    switchAgent,
    getAgentInfo,
    generateAgentResponse};
};