import { XiaokeAgentImpl } from "./XiaokeAgent";

// 创建小克智能体实例
export const xiaokeAgent = new XiaokeAgentImpl();

// 小克智能体导出
export * from "./types";
export { XiaokeAgent } from "./XiaokeAgent";
export { XiaokeAgentImpl, createXiaokeAgent } from "./XiaokeAgentImpl";
