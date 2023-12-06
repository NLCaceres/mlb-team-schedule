import CalendarDay from "./CalendarDay.svelte";
import { render, screen } from "@testing-library/svelte";
import BaseballGame from "../Models/DataClasses";
import type { BaseballTeam } from "../Models/DataClasses";

const innerWidthStart = global.innerWidth; //* For test resetting purposes

describe("render a single day in a typical wall-calendar style", () => {
  let homeTeam: BaseballTeam;
  let awayTeam: BaseballTeam;
  let game: BaseballGame;
  beforeEach(() => {
    homeTeam = { id: "1", teamLogo: "", teamName: "foo", cityName: "", abbreviation: "", wins: 1, losses: 0 };
    awayTeam = { id: "1", teamLogo: "", teamName: "foo", cityName: "", abbreviation: "", wins: 0, losses: 1 };
    game = BaseballGame.of({ id: "1", date: "", homeTeam: homeTeam, awayTeam: awayTeam, promos: [], seriesGameNumber: 1, seriesGameCount: 3 });
    global.innerWidth = innerWidthStart;
  });
  test("unless missing a dayNum", () => {
    const { rerender } = render(CalendarDay, { currentMonth: "", dayNum: "", games: [game] });

    const calendarDayBody = screen.getByRole("cell");
    expect(calendarDayBody.firstChild).toBeEmptyDOMElement();

    rerender({ currentMonth: "", dayNum: "foo", games: [game] });
    const gameDayBody = screen.getByRole("cell");
    expect(gameDayBody.firstChild).not.toBeEmptyDOMElement();
  });
  test("including the start time of any given game", () => {
    const { rerender } = render(CalendarDay, { currentMonth: "", dayNum: "foo",
      games: [BaseballGame.of({ ...game, date: "Thur June 09 2021 at 07:10 PM" })] });
    expect(screen.getByText("7:10 PM"));

    //* Poorly formatted dates or strings without a time get left empty
    rerender({ currentMonth: "", dayNum: "foo", games: [BaseballGame.of({ ...game, date: "Thur June 09" })] });
    const calendarDayNumWithHalfDate = screen.getByText("foo");
    const startTimeElemWithHalfDate = calendarDayNumWithHalfDate.nextElementSibling;
    expect(startTimeElemWithHalfDate).toHaveTextContent(""); //* No text inserted, just an empty string

    rerender({ currentMonth: "", dayNum: "foo", games: [BaseballGame.of({ ...game, date: "Barfoo" })] });
    const calendarDayNumWithBadDate = screen.getByText("foo");
    const startTimeElemWithBadDate = calendarDayNumWithBadDate.nextElementSibling;
    expect(startTimeElemWithBadDate).toHaveTextContent("");

    rerender({ currentMonth: "", dayNum: "foo", games: [] });
    expect(screen.queryByText("7:10 PM")).not.toBeInTheDocument();
    //* As a sanity check, grab the calendar day number and check if it has the start time sibling
    expect(screen.getByText("foo").nextElementSibling).toBeNull(); //* Time should non-existent
    //? use "nextElementSibling" because "nextSibling" may treat the text inside a <p> tag as a sibling
  });
  test("altering the game/promo section depending on the screen width and if a game is happening", () => {
    //todo Since small screens, use a simplified/smaller version of the CalendarDayDetail
    //todo Seems best to find a way to merge the simpler stylings into CalendarDayDetail, simplifying this entire conditional block
    //* On small screens, each calendar day gets a smaller version of the CalendarDayDetail component
    global.innerWidth = 575;
    const { rerender } = render(CalendarDay, { currentMonth: "foo", dayNum: "bar", games: [game] });
    expect(screen.getByText("vs")).toBeInTheDocument();
    expect(screen.getByText("vs").nextElementSibling?.firstElementChild).toHaveTextContent("");
    //* The link gets an asterisk if it has promotions
    rerender({ currentMonth: "foo", dayNum: "bar", games: [BaseballGame.of({ ...game, promos: [{ id: "foo", name: "", thumbnailUrl: "" }] })] });
    expect(screen.getByText("vs")).toBeInTheDocument();
    expect(screen.getByText("vs").nextElementSibling?.firstElementChild).toHaveTextContent("*");

    //! If no game, then one of the following messages is displayed in the Calendar Day depending on time of the season
    rerender({ currentMonth: "march", dayNum: "15", games: [] });
    expect(screen.getByText(/spring training/i)).toBeInTheDocument();

    rerender({ currentMonth: "october", dayNum: "30", games: [] });
    expect(screen.getByText(/post season/i)).toBeInTheDocument();

    rerender({ currentMonth: "october", dayNum: "31", games: [] });
    expect(screen.getByText(/season over/i)).toBeInTheDocument();

    rerender({ currentMonth: "bar", dayNum: "12", games: [] });
    expect(screen.getByText(/off day/i)).toBeInTheDocument();
  });
  describe("altering the style", () => {
    test("based on if the component is mini", () => {
      const { rerender } = render(CalendarDay, { currentMonth: "", dayNum: "foo", games: [game] });
      expect(screen.getByText("foo")).not.toHaveClass("mini"); //* NOT mini by default, i.e. mini == false

      rerender({ currentMonth: "", dayNum: "foo", games: [game], mini: true });
      expect(screen.getByText("foo")).toHaveClass("mini");

      global.innerWidth = 575; //* Need to change viewport size to prevent rendering full CalendarDayDetail
      rerender({ currentMonth: "", dayNum: "foo", games: [game], mini: true });
      expect(screen.getByText("foo")).toHaveClass("mini"); //* No change
      expect(screen.getByText("vs")).toHaveClass("flex-column"); //* Smaller non-component based CalendarDayDetail

      rerender({ currentMonth: "", dayNum: "foo", games: [game], mini: false });
      expect(screen.getByText("foo")).not.toHaveClass("mini"); //* Mini now false, so remove class
      expect(screen.getByText("vs")).not.toHaveClass("flex-column"); //* Small screen, so despite mini being false, keep this class

      rerender({ currentMonth: "march", dayNum: "15", games: [], mini: true });
      expect(screen.getByText(/spring training/i)).toHaveClass("mini");
      rerender({ currentMonth: "march", dayNum: "15", games: [], mini: false });
      expect(screen.getByText(/spring training/i)).not.toHaveClass("mini");

      rerender({ currentMonth: "october", dayNum: "30", games: [], mini: true });
      expect(screen.getByText(/post season/i)).toHaveClass("mini");
      rerender({ currentMonth: "october", dayNum: "30", games: [], mini: false });
      expect(screen.getByText(/post season/i)).not.toHaveClass("mini");

      rerender({ currentMonth: "october", dayNum: "31", games: [], mini: true });
      expect(screen.getByText(/season over/i)).toHaveClass("mini");
      rerender({ currentMonth: "october", dayNum: "31", games: [], mini: false });
      expect(screen.getByText(/season over/i)).not.toHaveClass("mini");

      rerender({ currentMonth: "bar", dayNum: "12", games: [], mini: true });
      expect(screen.getByText(/off day/i)).toHaveClass("mini");
      rerender({ currentMonth: "bar", dayNum: "12", games: [], mini: false });
      expect(screen.getByText(/off day/i)).not.toHaveClass("mini");
    });
    test("to style the calendar for large screens", () => {
      const gameWithDate = BaseballGame.of({ ...game, date: "Thur June 09 2021 at 07:10 PM" });
      const { rerender } = render(CalendarDay, { currentMonth: "", dayNum: "foo", games: [gameWithDate] });
      //* Viewport should be 1024 AND mini is false by default so use the following classes
      expect(screen.getByRole("cell").firstElementChild).toHaveClass("flex-column");
      expect(screen.getByText("foo").parentElement).toHaveClass("d-flex justify-content-between");
      expect(screen.getByText("7:10 PM")).toHaveClass("fs-5 text-end lh-1 mt-1");

      rerender({ currentMonth: "", dayNum: "foo", games: [gameWithDate], mini: true });
      expect(screen.getByRole("cell").firstElementChild).not.toHaveClass("flex-column");
      expect(screen.getByText("foo").parentElement).not.toHaveClass("d-flex justify-content-between");
      expect(screen.getByText("7:10 PM")).not.toHaveClass("fs-5 text-end lh-1 mt-1");

      global.innerWidth = 575; //* Now small with mini = false again
      rerender({ currentMonth: "", dayNum: "foo", games: [gameWithDate] });
      expect(screen.getByRole("cell").firstElementChild).not.toHaveClass("flex-column");
      expect(screen.getByText("foo").parentElement).not.toHaveClass("d-flex justify-content-between");
      expect(screen.getByText("7:10 PM")).not.toHaveClass("fs-5 text-end lh-1 mt-1");

      //* Mini == true AND screen is still small
      rerender({ currentMonth: "", dayNum: "foo", games: [gameWithDate], mini: true });
      expect(screen.getByRole("cell").firstElementChild).not.toHaveClass("flex-column");
      expect(screen.getByText("foo").parentElement).not.toHaveClass("d-flex justify-content-between");
      expect(screen.getByText("7:10 PM")).not.toHaveClass("fs-5 text-end lh-1 mt-1");

      //! Small quirk: The child container used for the CalendarDayDetails adds its largeCalendar CSS on days without a game
      rerender({ currentMonth: "", dayNum: "foo", games: [], mini: true }); //* Regardless of screen size and mini == false
      expect(screen.getByRole("cell").firstElementChild).toHaveClass("flex-column");
    });
    test("based on if the week is odd (1st, 3rd, 5th) or even (2nd or 4th)", () => {
      const { rerender } = render(CalendarDay, { currentMonth: "", dayNum: "foo", games: [game] });
      //* Even by default
      const calendarDayBody = screen.getByRole("cell");
      expect(calendarDayBody).toHaveClass("even");
      const calendarDayNum = screen.getByText("foo");
      expect(calendarDayNum).toHaveClass("text-dodger-blue"); //todo Good place to target variable team colors

      rerender({ currentMonth: "", dayNum: "foo", games: [game], even: false });
      expect(screen.getByRole("cell")).toHaveClass("odd");
      expect(screen.getByText("foo")).toHaveClass("text-white");
    });
    describe("of the root element", () => {
      test("via a CssClass prop", () => {
        const { rerender } = render(CalendarDay, { currentMonth: "", dayNum: "foo", games: [game], cssClasses: "foobar" });
        expect(screen.getByRole("cell")).toHaveClass("foobar");

        rerender({ currentMonth: "", dayNum: "foo", games: [game] });
        expect(screen.getByRole("cell")).not.toHaveClass("foobar");
        expect(screen.getByRole("cell")).toHaveClass("standard-detail"); //* Just has its normal base CSS class
      });
      test("via an empty dayNum string", () => {
        const { rerender } = render(CalendarDay, { currentMonth: "", dayNum: "", games: [game] });
        expect(screen.getByRole("cell")).toHaveClass("different-month");

        rerender({ currentMonth: "", dayNum: "foo", games: [game] });
        expect(screen.getByRole("cell")).not.toHaveClass("different-month");
      });
    });
  });
});