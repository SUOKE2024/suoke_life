import React from "react";
import { render, fireEvent } from "@testing-library/react-native";
import { AgentChatBubble } from "../components/AgentChatBubble";

describe("AgentChatBubble", () => {
  it("应渲染文本消息", () => {
    const { getByText } = render(
      <AgentChatBubble agentType="xiaoai" message="你好" />
    );
    expect(getByText("你好")).toBeTruthy();
  });

  it("应渲染语音消息并触发播放", () => {
    const onPlayVoice = jest.fn();
    const { getByText } = render(
      <AgentChatBubble
        agentType="xiaoai"
        message="语音消息"
        isVoice
        onPlayVoice={onPlayVoice}
      />
    );
    fireEvent.press(getByText("点击播放语音"));
    expect(onPlayVoice).toHaveBeenCalled();
  });
});