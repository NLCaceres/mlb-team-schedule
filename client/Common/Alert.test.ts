import Alert from "./Alert.svelte";
import { render, screen } from "@testing-library/svelte";

describe("renders a simple Alert", () => {
  test("requires an 'id' prop to keep alerts unique + accessible", () => {
    const { rerender } = render(Alert, { invisible: false, alertID: "123" });
    expect(screen.getByRole("alert")).toHaveAttribute("id", "123");

    rerender({ invisible: false, alertID: "abc" });
    expect(screen.getByRole("alert")).toHaveAttribute("id", "abc");
  });
  test("hiding the body if passed a true 'invisible' prop", () => {
    const { rerender } = render(Alert, { invisible: false, alertID: "" }); //? Need to set any props without default values
    const body = screen.getByText("Alert!");
    expect(body).toBeInTheDocument(); //* Alert body visible

    rerender({ invisible: true, alertID: "" });
    expect(body).not.toBeInTheDocument(); //* Alert now invisible so body is gone

    rerender({ invisible: null, alertID: "" }); //* Null acts like true, causing alert to reappear
    expect(screen.getByText("Alert!")).toBeInTheDocument();
  });
  test("controlling the close button via both the 'invisible' and 'fading' props", () => {
    const { rerender } = render(Alert, { invisible: false, alertID: "" }); //* Invis: false, fading: false
    const closeButton = screen.getByLabelText("Close");
    expect(closeButton).toBeInTheDocument(); //* Close button visible by default

    rerender({ invisible: true, alertID: "" }); //* Invis: true, fade: false
    expect(closeButton).not.toBeInTheDocument(); //* Alert now invisible so close button is gone

    //* Invis: null, fade: false
    rerender({ invisible: null, alertID: "" }); //* Alert reappears but the button is gone
    expect(screen.queryByLabelText("Close")).not.toBeInTheDocument();

    //* Invis: null, fade: true
    rerender({ invisible: null, fading: true, alertID: "" }); //* Button reappears due to the 'fading' prop
    expect(screen.getByLabelText("Close")).toBeInTheDocument();

    //* Invis: true, fade: true
    rerender({ invisible: true, fading: true, alertID: "" }); //* Button disappeared again
    expect(screen.queryByLabelText("Close")).not.toBeInTheDocument();

    //* Invis: false, fade: true
    rerender({ invisible: false, fading: true, alertID: "" }); //* Alert reappears + button visible thanks to both props
    expect(screen.getByLabelText("Close")).toBeInTheDocument();

    //* Invis: false, fade: false
    rerender({ invisible: false, fading: false, alertID: "" }); //* Button remains since 'fading' prop is explicitly false
    expect(screen.getByLabelText("Close")).toBeInTheDocument(); //* BUT 'invisible' takes priority keeping the close button visible
  });
  describe("uses props to handle CSS styling", () => {
    test("dynamically adding in CSS classes", () => {
      const { rerender } = render(Alert, { invisible: false, alertID: "" });
      expect(screen.getByRole("alert")).toHaveClass("alert align-middle");

      rerender({ invisible: false, alertClasses: "foo bar", alertID: "" });
      expect(screen.getByRole("alert")).toHaveClass("alert align-middle foo bar");
    });
  });
});