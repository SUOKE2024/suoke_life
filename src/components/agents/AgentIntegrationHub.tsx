react;
export interface Agent {
id: string,"name: string,","";
type: xiaoai" | "xiaoke | "laoke" | soer;",";
status: "online | "offline" | busy,";
capabilities: string[],

}
  const lastActive = Date}
}
export interface AgentTask {id: string}agentId: string,","";
type: string,","";
status: "pending | "running" | completed" | "failed;",","";
priority: "low" | medium" | "high;",
}
}
  const createdAt = Date}
}
export interface AgentIntegrationHubProps {
"onAgentSelect?: (agent: Agent) => void;";

}
  onTaskCreate?: (task: Omit<AgentTask; "id" | createdAt">) => void;"
}
/* " *//;"/g"/;
  */"/"/g"/;