import QuestionMark from "./QuestionMark.svelte";
import { render, screen } from "@testing-library/svelte";

describe("render an SVG question mark", () => {
  test("with dynamic height and width", () => {
    const { rerender } = render(QuestionMark, { width: 40, height: 40 });
    const questionMarkIcon = screen.getByRole("img", { name: "Question Mark Icon" });
    //* WHEN the width and height are set to 40, THEN the SVG grows to 40 width, 40 height
    expect(questionMarkIcon).toHaveAttribute("width", "40");
    expect(questionMarkIcon).toHaveAttribute("height", "40");

    rerender({ width: 20, height: 80 });
    //* WHEN the width is set to 20 and height is set to 80
    const resizedIcon = screen.getByRole("img", { name: "Question Mark Icon" });
    expect(resizedIcon).toHaveAttribute("width", "20"); //* THEN the SVG shrinks to 20 width
    expect(resizedIcon).toHaveAttribute("height", "80"); //* AND grows to 80 height
  });
  test("with dynamic outline and fill color", () => {
    const { rerender } = render(QuestionMark, { width: 40, height: 40 });
    const questionMarkIcon = screen.getByRole("img", { name: "Question Mark Icon" });
    //* WHEN no outline or fill color strings are added
    const circle = questionMarkIcon.children[1];
    //* THEN the stroke attribute will not appear in the component
    expect(circle).not.toHaveAttribute("stroke");
    const path = questionMarkIcon.lastElementChild;
    expect(path).not.toHaveAttribute("stroke");
    //* NOR will the fill attribute appear in the component
    expect(path).not.toHaveAttribute("fill");

    //* WHEN BOTH the outline and fill color strings are added
    rerender({ width: 40, height: 40, outlineColor: "foo", fillColor: "bar" });
    const outlinedAndFilledIcon = screen.getByRole("img", { name: "Question Mark Icon" });
    //* THEN the stroke attribute will appear with the used value
    expect(outlinedAndFilledIcon.children[1]).toHaveAttribute("stroke", "foo");
    expect(outlinedAndFilledIcon.lastElementChild).toHaveAttribute("stroke", "foo");
    //* AND the fill attribute will appear with its respective value
    expect(outlinedAndFilledIcon.lastElementChild).toHaveAttribute("fill", "bar");

    //* WHEN ONLY the outline but NOT the fill color string is added
    rerender({ width: 40, height: 40, outlineColor: "red" });
    const outlinedIcon = screen.getByRole("img", { name: "Question Mark Icon" });
    //* THEN the stroke attribute will appear with the used value
    expect(outlinedIcon.children[1]).toHaveAttribute("stroke", "red");
    expect(outlinedIcon.lastElementChild).toHaveAttribute("stroke", "red");
    //* BUT the fill attribute will NOT appear
    expect(outlinedIcon.lastElementChild).not.toHaveAttribute("fill", "bar");

    //* WHEN ONLY the fill but NOT the outline color string is added
    rerender({ width: 40, height: 40, fillColor: "blue" });
    const filledIcon = screen.getByRole("img", { name: "Question Mark Icon" });
    //* THEN the stroke attribute will NOT appear
    expect(filledIcon.children[1]).not.toHaveAttribute("stroke", "red");
    expect(filledIcon.lastElementChild).not.toHaveAttribute("stroke", "red");
    //* BUT the fill attribute will appear with its added value
    expect(filledIcon.lastElementChild).toHaveAttribute("fill", "blue");
  });
});
