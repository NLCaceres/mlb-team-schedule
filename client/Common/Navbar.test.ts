import Navbar from "./NavbarTest.svelte"; //? Need to use a Test component because Svelte-Routing's <Link> component needs a parent <Router>
import { render, screen } from "@testing-library/svelte";
import userEvent from "@testing-library/user-event";
import { vi, type MockInstance } from "vitest";
import { readable } from "svelte/store";
import * as SvelteRouting from "svelte-routing";
import * as UseExpandable from "../Actions/UseExpandable";

describe("renders a Navbar", () => {
  let LocationSpy: MockInstance;
  let UseExpandableSpy: MockInstance;
  beforeEach(() => {
    LocationSpy = vi.spyOn(SvelteRouting, "useLocation");
    LocationSpy.mockReturnValue(readable({ pathname: "/March" }));
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    const mockFunction = (node: HTMLElement, willExpand: boolean) => { return { update(isExpanded: boolean) { return; } }; };
    UseExpandableSpy = vi.spyOn(UseExpandable, "expandable").mockImplementation(mockFunction); //? Mock use:expandable to skip animations
  });
  afterEach(() => {
    vi.restoreAllMocks();
  });
  describe("with a set of links", () => {
    test("dynamic in nature", () => {
      const { rerender } = render(Navbar, { links: ["foo"], currentYear: "2023" });
      const initialLinkList = screen.getAllByRole("listitem");
      //* WHEN 1 link string is input, THEN only 1 link list item is rendered
      expect(initialLinkList).toHaveLength(1);
      expect(initialLinkList[0]).toHaveTextContent("foo"); //* AND it is rendered as written

      rerender({ links: ["bar", "Fizz"], currentYear: "2023" });
      const updatedLinkList = screen.getAllByRole("listitem");
      //* WHEN 2 link strings are input, THEN only 2 link list items are rendered
      expect(updatedLinkList).toHaveLength(2);
      expect(updatedLinkList[0]).toHaveTextContent("bar");
      expect(updatedLinkList[1]).toHaveTextContent("Fizz");
      //* WHEN a link is capitalized, THEN its href attribute is input lowercased
      expect(updatedLinkList[1].firstChild).toHaveAttribute("href", "/fizz");

      rerender({ links: [], currentYear: "2023" });
      //* WHEN no links are input, THEN none are rendered
      expect(screen.queryAllByRole("listitem")).toHaveLength(0);
    });
    test("becoming 'active' if on the correct path", () => {
      LocationSpy.mockReturnValue(readable({ pathname: "/foo" }));
      const { rerender } = render(Navbar, { links: ["foo"], currentYear: "2023" });
      const linkListItem = screen.getByRole("listitem");
      expect(linkListItem).toHaveTextContent("foo");
      expect(linkListItem.firstChild).toHaveClass("active");

      rerender({ links: ["bar", "Fizz"], currentYear: "2023" });
      const updatedLinkList = screen.getAllByRole("listitem");
      expect(updatedLinkList).toHaveLength(2);
      expect(updatedLinkList[0]).toHaveTextContent("bar");
      expect(updatedLinkList[0].firstChild).not.toHaveClass("active");
      expect(updatedLinkList[1]).toHaveTextContent("Fizz");
      expect(updatedLinkList[1].firstChild).not.toHaveClass("active");
    });
  });
  test("accepting a prop to display the current year", () => {
    const { rerender } = render(Navbar, { links: ["foo"], currentYear: "2023" });
    const initBrandLink = screen.getByText(/2023/);
    expect(initBrandLink).toBeInTheDocument();
    expect(initBrandLink).toHaveTextContent("Dodgers 2023");
    expect(initBrandLink).toHaveAttribute("href", "/");

    rerender({ links: ["foo"], currentYear: "2021" });
    const updatedBrandLink = screen.getByText(/2021/);
    expect(updatedBrandLink).toBeInTheDocument();
    expect(updatedBrandLink).toHaveTextContent("Dodgers 2021");
    expect(updatedBrandLink).toHaveAttribute("href", "/");

    rerender({ links: ["foo"], currentYear: "" });
    const emptyBrandLink = screen.getAllByRole("link")[0];
    expect(emptyBrandLink).toBeInTheDocument();
    expect(emptyBrandLink).toHaveTextContent("Dodgers");
    expect(emptyBrandLink).toHaveAttribute("href", "/");
  });
  test("expanding based on click events or viewport width", async () => {
    const originalWidth = global.innerWidth; //? Expected to normally be 1024
    global.innerWidth = 991;
    const user = userEvent.setup();
    const { rerender } = render(Navbar, { links: ["foo"], currentYear: "2023" });
    const togglerButton = screen.getByRole("button");
    expect(togglerButton).toBeInTheDocument();
    //* WHEN an initial render occurs at viewport widths < 991, THEN aria-expanded is "false"
    expect(togglerButton).toHaveAttribute("aria-expanded", "false");
    //* WHEN the toggler button is pressed, THEN aria-expanded is flipped to "true"
    await user.click(togglerButton);
    expect(screen.getByRole("button")).toHaveAttribute("aria-expanded", "true");
    expect(UseExpandableSpy).toHaveBeenCalledTimes(1);
    //* WHEN the toggler button is pressed again, THEN aria-expanded is flipped back to "false"
    await user.click(togglerButton);
    expect(screen.getByRole("button")).toHaveAttribute("aria-expanded", "false");

    rerender({ links: ["foo"], currentYear: "2023" });
    //* WHEN a rerender occurs, THEN aria-expanded is "false"
    expect(screen.getByRole("button")).toHaveAttribute("aria-expanded", "false");
    await user.click(screen.getByRole("button"));
    expect(screen.getByRole("button")).toHaveAttribute("aria-expanded", "true");
    //* WHEN the navbar is expanded, THEN clicking a link will set aria-expanded to "false"
    //? Clicking <a> tags in tests usually causes a "navigation" implementation error since Jest/Vitest's underlying JSDom doesn't implement it
    await user.click(screen.getByRole("link", { name: "foo" })); //? BUT since Svelte-Routing's <Link> hijacks navigation, my tests have no issues!
    expect(screen.getByRole("button")).toHaveAttribute("aria-expanded", "false");
    //* WHEN the navbar is not expanded, THEN clicking a link will keep aria-expanded as "false"
    await user.click(screen.getByRole("link", { name: "foo" }));
    expect(screen.getByRole("button")).toHaveAttribute("aria-expanded", "false");

    global.innerWidth = 1024;
    //* WHEN a rerender occurs at viewport widths > 991, THEN aria-expanded is true
    rerender({ links: ["foo"], currentYear: "2023" });
    expect(screen.getByRole("button")).toHaveAttribute("aria-expanded", "true");
    //* WHEN the viewport width > 991 , THEN clicking a link will not update "aria-expanded"
    await user.click(screen.getByRole("link", { name: "foo" }));
    expect(screen.getByRole("button")).toHaveAttribute("aria-expanded", "true");

    global.innerWidth = originalWidth;
  });
});