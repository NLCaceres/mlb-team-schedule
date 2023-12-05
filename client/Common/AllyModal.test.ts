import AllyModal from "./AllyModal.svelte";
import { render, screen } from "@testing-library/svelte";

describe("renders a modal based on the `a11y-dialog`", () => {
  test("accepts a visibility prop to control whether it is displayed and accessible", () => {
    const { rerender } = render(AllyModal, { modalID: "foo" });
    const hiddenModalContent = screen.queryByRole("document");
    expect(hiddenModalContent).not.toBeInTheDocument();

    rerender({ visible: true, modalID: "foo" });
    const modalContent = screen.getByRole("document");
    expect(modalContent).toBeInTheDocument();
    //* WHEN visible is true, THEN the dialog is no longer hidden and therefore accessible to users
    expect(modalContent.parentElement).toHaveAttribute("aria-hidden", "false");
  });
  test("accepts a modal ID for accessibility and to use as the title's 'ID'", () => {
    const { rerender } = render(AllyModal, { visible: true, modalID: "foo" });
    const modalContainer = screen.getByRole("document").parentElement;
    expect(modalContainer).toHaveAttribute("id", "foo");
    expect(modalContainer).toHaveAttribute("aria-labelledby", "fooLabel");

    //* WHEN title rendered, THEN use the id as its ID, i.e `${id}Label`
    rerender({ visible: true, modalID: "fizz", modalTitle: "foo" });
    const rerenderedTitle = screen.getByText("foo");
    expect(rerenderedTitle).toHaveAttribute("id", "fizzLabel");
  });
  test("renders a modal title if 'modalTitle' prop or the title slot filled", () => {
    const { rerender } = render(AllyModal, { visible: true, modalID: "foo", modalTitle: "foo" });
    const modalTitle = screen.getByText("foo");
    expect(modalTitle).toBeInTheDocument();
    expect(modalTitle).toHaveAttribute("id", "fooLabel");

    //* WHEN no title or slot, THEN no header rendered
    rerender({ visible: true, modalID: "foo", modalTitle: "" });
    expect(screen.queryByText("foo")).not.toBeInTheDocument();

    //todo Due to Svelte Client Component API limitations, slots are difficult to test
    //todo Need to therefore make simple test components in a different file to actually pass elems into the slots
    //todo Make a test component that fills the title slot to show the title reappear
  });
  test("renders a close button if 'closeable' prop set to true", () => {
    const { rerender } = render(AllyModal, { visible: true, modalID: "foo", closeable: true });
    expect(screen.getByLabelText("Close dialog")).toBeInTheDocument();

    //* WHEN closeable is false, THEN the close button is not rendered
    rerender({ visible: true, modalID: "foo", closeable: false });
    expect(screen.queryByLabelText("Close dialog")).not.toBeInTheDocument();
  });

  describe("uses props to handle CSS styling", () => {
    test("for the content section's classes", () => {
      const { rerender } = render(AllyModal, { visible: true, modalID: "foo", modalContentClasses: "foo bar" });
      const modalContent = screen.getByRole("document");
      expect(modalContent).toHaveClass("foo bar dialog-content modal-dialog");

      rerender({ visible: true, modalID: "foo", modalContentClasses: "" });
      const rerenderedModalContent = screen.getByRole("document");
      expect(rerenderedModalContent).toHaveClass("dialog-content modal-dialog");
      expect(rerenderedModalContent).not.toHaveClass("foo bar");
    });
    test("for the header section's classes", () => {
      const { rerender } = render(AllyModal, { visible: true, modalID: "foo", modalHeaderClasses: "foo bar" });
      const modalContent = screen.getByRole("document");
      const modalHeader = modalContent.firstElementChild;
      expect(modalHeader).toHaveClass("foo bar modal-header");

      rerender({ visible: true, modalID: "foo", modalHeaderClasses: "" });
      const rerenderedModalContent = screen.getByRole("document");
      const rerenderedModalHeader = rerenderedModalContent.firstElementChild;
      expect(rerenderedModalHeader).toHaveClass("modal-header");
      expect(rerenderedModalHeader).not.toHaveClass("foo bar");
    });
    test("for the body section's classes", () => {
      const { rerender } = render(AllyModal, { visible: true, modalID: "foo", modalBodyClasses: "foo bar" });
      const modalContent = screen.getByRole("document");
      const modalBody = modalContent.lastElementChild;
      expect(modalBody).toHaveClass("foo bar modal-body");

      rerender({ visible: true, modalID: "foo", modalBodyClasses: "" });
      const rerenderedModalContent = screen.getByRole("document");
      const rerenderedModalBody = rerenderedModalContent.lastElementChild;
      expect(rerenderedModalBody).toHaveClass("modal-body");
      expect(rerenderedModalBody).not.toHaveClass("foo bar");
    });
  });
});