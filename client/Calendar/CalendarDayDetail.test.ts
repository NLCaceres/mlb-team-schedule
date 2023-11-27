import CalendarDayDetail from "./CalendarDayDetail.svelte";
import { render, screen } from "@testing-library/svelte";
import type BaseballGame from "../Models/DataClasses";
import type { BaseballTeam } from "../Models/DataClasses";

const innerWidthStart = global.innerWidth;

describe("render a single day in a typical wall-calendar style", () => {
  let homeTeam: BaseballTeam;
  let awayTeam: BaseballTeam;
  let game: BaseballGame;
  beforeEach(() => {
    homeTeam = { id: "1", teamLogo: "", teamName: "foo", cityName: "", abbreviation: "", wins: 1, losses: 0 };
    awayTeam = { id: "1", teamLogo: "", teamName: "foo", cityName: "", abbreviation: "", wins: 0, losses: 1 };
    game = { id: "1", date: "", homeTeam: homeTeam, awayTeam: awayTeam, promos: [], seriesGameNumber: 1, seriesGameCount: 3 };
    global.innerWidth = innerWidthStart;
  });
  test("displays any promotions of the game if not a mini calendar", () => {
    const { rerender } = render(CalendarDayDetail, { game: game });
    expect(screen.getByText(/dodgers away/i)).toBeInTheDocument();

    //todo Another good point to make dynamic for whichever team the user wants to track
    rerender({ game: { ...game, homeTeam: { ...homeTeam, teamName: "Dodgers" } } });
    expect(screen.getByText(/no dodgers promo/i)).toBeInTheDocument();

    rerender({ game: game, mini: true });
    const emptyPromoSection = screen.getByText("vs").nextElementSibling;
    expect(emptyPromoSection).toBeEmptyDOMElement();

    const gameWithPromos = { ...game, promos: [{ id: "foo", name: "", thumbnailUrl: "" }] };
    rerender({ game: gameWithPromos }); //* Mini == false
    expect(screen.getByRole("list").children).toHaveLength(1);

    rerender({ game: gameWithPromos, mini: true });
    expect(screen.getByText("*")).toBeInTheDocument(); //* Just render an asterisk for promo days in a mini calendar
  });
  describe("altering the style", () => {
    test("based on if the component is mini", () => {
      const gameWithPromos = { ...game, promos: [{ id: "foo", name: "", thumbnailUrl: "" }] };
      const { rerender, container } = render(CalendarDayDetail, { game: gameWithPromos });
      //* Mini == false by default
      const componentRoot = container.firstElementChild!.firstElementChild;
      expect(componentRoot).toHaveClass("even"); //* Only class is "even"
      expect(componentRoot).not.toHaveClass("d-flex");
      const logoContainer = componentRoot!.firstElementChild;
      expect(logoContainer).toHaveClass("me-1");
      expect(logoContainer).not.toHaveClass("flex-column");
      const promoContainer = componentRoot!.lastElementChild;
      expect(promoContainer).toHaveClass("mt-3");

      rerender({ game: gameWithPromos, mini: true });
      const miniComponentRoot = container.firstElementChild!.firstElementChild;
      expect(miniComponentRoot).toHaveClass("d-flex even"); //* Add flex
      const miniLogoContainer = miniComponentRoot!.firstElementChild;
      expect(miniLogoContainer).not.toHaveClass("me-1");
      expect(miniLogoContainer).toHaveClass("flex-column");
      const miniPromoContainer = miniComponentRoot!.lastElementChild;
      expect(miniPromoContainer).not.toHaveClass("mt-3");
    });
    test("based on if the week is odd (1st, 3rd, 5th) or even (2nd or 4th)", () => {
      const gameWithPromos = { ...game, promos: [{ id: "foo", name: "", thumbnailUrl: "" }] };
      const { rerender, container } = render(CalendarDayDetail, { game: gameWithPromos });
      //* Even == true by default
      const evenComponentRoot = container.firstElementChild!.firstElementChild;
      expect(evenComponentRoot).toHaveClass("even");
      expect(screen.getByText(/missing thumbnail/i)).toHaveStyle({ "margin-bottom": "7px", "font-size": "14px" });

      rerender({ game: gameWithPromos, even: false });
      expect(screen.getByText(/missing thumbnail/i)).toHaveStyle(
        { "margin-bottom": "7px", "font-size": "14px", "background-color": "#000", color: "#fff" }
      );
      const oddComponentRoot = container.firstElementChild!.firstElementChild;
      expect(oddComponentRoot).toHaveClass("odd");
    });
    test("based on if the viewWidth is less than or equal to 768", () => {
      const gameWithPromos = { ...game, promos: [{ id: "foo", name: "", thumbnailUrl: "" }] };
      const { rerender, container } = render(CalendarDayDetail, { game: gameWithPromos });
      //* Desktop size by default, i.e. 1024px
      expect(screen.getByText(/missing thumbnail/i)).toHaveStyle("font-size:14px"); //* So use larger font

      global.innerWidth = 768; //* Set to tablet size
      rerender({ game: gameWithPromos, even: false });
      expect(screen.getByText(/missing thumbnail/i)).toHaveStyle("font-size:10px"); //* Use smaller font
      const oddComponentRoot = container.firstElementChild!.firstElementChild;
      expect(oddComponentRoot).toHaveClass("odd");
    });
  });
});
