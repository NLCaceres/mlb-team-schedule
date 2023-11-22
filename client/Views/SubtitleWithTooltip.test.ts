import SubtitleWithTooltip from "./SubtitleWithTooltip.svelte";
import { render, screen } from "@testing-library/svelte";

describe("renders a subtitle with a tooltip noting which games are at home with promotions", () => {
  test("depending on a subtitle prop to render its heading", () => {
    const { rerender } = render(SubtitleWithTooltip, { subtitle: "March 2023" });
    expect(screen.getByText("March 2023")).toBeInTheDocument();

    rerender({ subtitle: "Foobar 2121 "})
    //* WHEN the subtitle prop is filled, the heading tag in the component is filled with that prop value
    expect(screen.getByRole("heading", { name: "Foobar 2121" })).toBeInTheDocument();
  })
  test("depending on the viewWidth to place the tooltip hint", () => {
    //* WHEN the innerWidth > 991
    global.innerWidth = 1024;
    const { rerender } = render(SubtitleWithTooltip, { subtitle: "March 2023" });
    //* THEN place the tooltip hint to the right of the main element
    expect(screen.getByText(/indicates a home game with promotions/i).parentElement).toHaveClass("right-placed");

    //* WHEN the innerWidth <= 991
    global.innerWidth = 991;
    rerender({ subtitle: "March 2023" });
    //* THEN place the tooltip hint to the right of the main element
    expect(screen.getByText(/indicates a home game with promotions/i).parentElement).toHaveClass("top-placed");
    //* WHEN the innerWidth < 991
    global.innerWidth = 768;
    rerender({ subtitle: "March 2023" });
    //* THEN place the tooltip hint above the main element
    expect(screen.getByText(/indicates a home game with promotions/i).parentElement).toHaveClass("top-placed");
    //* WHEN the innerWidth < 991
    global.innerWidth = 575;
    rerender({ subtitle: "March 2023" });
    //* THEN place the tooltip hint above the main element
    expect(screen.getByText(/indicates a home game with promotions/i).parentElement).toHaveClass("top-placed");
    global.innerWidth = 1024;
  })
})
