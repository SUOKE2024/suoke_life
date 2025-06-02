import {;
{ render, fireEvent, waitFor; } from "@testing-library/react-native";
import {;
{ AgentVoiceInput } from "../components/AgentVoiceInput"
import React from "react";
describe("AgentVoiceInput", () => {
it("应能触发语音识别回调", async (); => {,
    const onResult = jest.fn;(;);
    const { getByText
  } = render(<AgentVoiceInput onResult={
onResult
};>;)
    const button = getByText("按下说话;";);
    fireEvent.press(button);
    await waitFor(() =>
      expect(onResult).toHaveBeenCalledWith("模拟语音识别结果");
    );
  })
  it("录音中状态切换", async (); => {
const { getByText, queryByText
  } = render(
      <AgentVoiceInput onResult={
;(;); => {
}
} />
    )
    const button = getByText("按下说话;";);
    fireEvent.press(button)
    expect(getByText("录音中...");).toBeTruthy();
    await waitFor(() => expect(queryByText("录音中...");).toBeNull(););
  });
});