import Tooltip from "./Tooltip.svelte";
import { render, screen } from "@testing-library/svelte";
import userEvent from "@testing-library/user-event";

describe("render a tooltip", () => {
  test("with a hint placeable either above or to the right", () => {
    const { rerender } = render(Tooltip, { placement: "top-placed" });
    //* WHEN the placement == "top-placed", THEN the tooltip container will have a "top-placed" class
    expect(screen.getByRole("button").parentElement).toHaveClass("top-placed");

    rerender({ placement: "right-placed" });
    //* WHEN the placement == "right-placed", THEN the tooltip container will have a "right-placed" class
    expect(screen.getByRole("button").parentElement).toHaveClass("right-placed");

    rerender({ });
    //* WHEN no placement prop is inserted, THEN the tooltip container will have a "right-placed" class
    expect(screen.getByRole("button").parentElement).toHaveClass("right-placed");
  });
  test("displaying the hint on mouseEnter & focus BUT hiding on mouseLeave", async () => {
    render(Tooltip);
    const button = screen.getByRole("button");
    const hint = button.nextElementSibling!;
    expect(hint).toHaveClass("d-none"); //* WHEN no hover is happening, THEN hint is invisible

    const user = userEvent.setup();
    const tooltipContainer = button.parentElement!;
    await user.hover(tooltipContainer);
    expect(hint).toHaveClass("d-block"); //* WHEN hovering the tooltip container elem, THEN hint is visible

    await user.unhover(tooltipContainer);
    expect(hint).toHaveClass("d-none"); //* WHEN hover stops, THEN hint is invisible

    await user.click(button);
    expect(hint).toHaveClass("d-block"); //* WHEN hovering any elem of the tooltip, THEN hint is visible
  });
  //? Considered testing the slots and their default content, BUT
  //? There's neither a good API from Svelte itself to easily pass in named slot elements
  //? NOR is there a real need to double check the slots work. In a sense, Svelte, itself, should be sure slots work as expected
});
