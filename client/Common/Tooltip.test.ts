import Tooltip from "./Tooltip.svelte";
import { render, screen } from "@testing-library/svelte";

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
  test("displaying the hint on mouseEnter & focus BUT hiding on mouseLeave", () => {
    render(Tooltip);
    const hint = screen.getByRole("button").nextElementSibling;
    expect(hint).toHaveClass("d-none");
    //TODO: Add user-event library to test hover events
  });
  //? Considered testing the slots and their default content, BUT
  //? There's neither a good API from Svelte itself to easily pass in named slot elements
  //? NOR is there a real need to double check the slots work. In a sense, Svelte, itself, should be sure slots work as expected
});
