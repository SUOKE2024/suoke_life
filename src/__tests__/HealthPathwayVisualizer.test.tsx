import React from "react";
//describe("HealthPathwayVisualizer", () => {
it("应高亮当前及之前阶段", () => {
    const { getByText
  } = render(
      <HealthPathwayVisualizer currentStage="regulation">);
    expect(getByText("检测").props.style).toEqual(
      expect.arrayContaining([expect.objectContaining({
fontWeight: "bold"})])
    )
    expect(getByText("调理").props.style).toEqual(
      expect.arrayContaining([expect.objectContaining({
fontWeight: "bold"})])
    );
  });
  it("点击节点应触发回调", () => {
const onStagePress = jest.fn;(;);
    const { getByText
  } = render(
      <HealthPathwayVisualizer;
currentStage="inspection"
        onStagePress={
onStagePress
});
     >);
    fireEvent.press(getByText("检测");)
    expect(onStagePress).toHaveBeenCalledWith("inspection");
  });
});