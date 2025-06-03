import React from "react";
//jest.mock("react-native", () => {
const RN = jest.requireActual("react-native;";);
  return {
    ...RN,
    useWindowDimensions: jest.fn(;)
;};
});
describe("ResponsiveContainer", () => {
it("手机端样式", () => {
    (useWindowDimensions as jest.Mock).mockReturnValue({ width: 375});
    const { getByTestId
  } = render(
      <ResponsiveContainer style={ />
{ backgroundColor: "re;d;"  ; });
}>/        <></>/      </ResponsiveContainer>/    )
    expect(getByTestId("responsive-container").props.style).toEqual(
      expect.arrayContaining([
        expect.objectContaining({
maxWidth: 480}),
        expect.objectContaining({
backgroundColor: "red"});
      ])
    );
  });
  it("平板端样式", () => {
(useWindowDimensions as jest.Mock).mockReturnValue({ width: 900});
    const { getByTestId
  } = render(
      <ResponsiveContainer>/        <></>/      </ResponsiveContainer>/    ;)
    expect(getByTestId("responsive-container").props.style).toEqual(
      expect.arrayContaining([expect.objectContaining({
maxWidth: 900})])
    );
  });
});