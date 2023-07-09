import { render, screen } from "@testing-library/svelte"
import Modal from "./Modal.svelte"

describe("renders a modal", () => {
  test("accepts a modal ID for accessibility and to use as the title's 'ID'", () => {
    const { rerender } = render(Modal, { modalID: "foo" });
    const modalContainer = screen.getByTestId("modal");
    expect(modalContainer).toHaveAttribute("id", "foo");
    expect(modalContainer).toHaveAttribute("aria-labelledby", "foo");

    //* When title rendered, use the id as its ID, i.e `${id}Label`
    rerender({ modalID: "fizz", modalTitle: "foo" });
    const rerenderedTitle = screen.getByText("foo");
    expect(rerenderedTitle).toHaveAttribute("id", "fizzLabel");
  })
  test("renders a modal title if 'modalTitle' prop or the title slot filled", () => {
    const { rerender } = render(Modal, { modalTitle: "foo" });
    const modalTitle = screen.getByText("foo");
    expect(modalTitle).toBeInTheDocument();
    expect(modalTitle).toHaveAttribute("id", "Label");
    
    //* No title or slot, no header
    rerender({ modalTitle: "" });
    expect(screen.queryByText("foo")).not.toBeInTheDocument();
    
    //todo Due to Svelte Client Component API limitations, slots are difficult to test
    //todo Need to therefore make simple test components in a different file to actually pass elems into the slots
    //todo Make a test component that fills the title slot to show the title reappear
  })
  test("renders a close button if 'closeable' prop set to true", () => {
    const { rerender } = render(Modal, { modalID: "foo", closeable: true });
    expect(screen.getByLabelText("Close")).toBeInTheDocument();

    rerender({ modalID: "foo", closeable: false });
    expect(screen.queryByLabelText("Close")).not.toBeInTheDocument();
  })

  describe("uses props to handle CSS styling", () => {
    test("for the content section's classes", () => {
      const { rerender } = render(Modal, { modalID: "foo", modalContentClasses: "foo bar" });
      const modalContainer = screen.getByTestId("modal");
      const modalContent = modalContainer.firstElementChild?.firstElementChild;
      expect(modalContent).toHaveClass("foo bar modal-content");

      rerender({ modalID: "foo", modalContentClasses: "" });
      const rerenderedModalContainer = screen.getByTestId("modal");
      const rerenderedModalContent = rerenderedModalContainer.firstElementChild?.firstElementChild;
      expect(rerenderedModalContent).toHaveClass("modal-content");
      expect(rerenderedModalContent).not.toHaveClass("foo bar");
    })
    test("for the header section's classes", () => {
      const { rerender } = render(Modal, { modalID: "foo", modalHeaderClasses: "foo bar" });
      const modalContainer = screen.getByTestId("modal");
      const modalHeader = modalContainer.firstElementChild?.firstElementChild?.firstElementChild;
      expect(modalHeader).toHaveClass("foo bar modal-header");

      rerender({ modalID: "foo", modalHeaderClasses: "" });
      const rerenderedModalContainer = screen.getByTestId("modal");
      const rerenderedModalHeader = rerenderedModalContainer.firstElementChild?.firstElementChild?.firstElementChild;
      expect(rerenderedModalHeader).toHaveClass("modal-header");
      expect(rerenderedModalHeader).not.toHaveClass("foo bar");
    })
  })
})