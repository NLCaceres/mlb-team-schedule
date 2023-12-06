import Calendar from "./Calendar.svelte";
import { render, screen } from "@testing-library/svelte";
import BaseballGame from "../Models/DataClasses";

describe("renders a simple Calendar", () => {
  test("setting the name of the Calendar month via 'monthName' prop", () => {
    const { rerender } = render(Calendar, { monthName: "foobar", gamesList: [] });
    expect(screen.getByRole("table").firstElementChild).toHaveTextContent("foobar");

    rerender({ monthName: "" , gamesList: [] });
    expect(screen.getByRole("table").firstElementChild).not.toHaveTextContent("foobar");
    expect(screen.getByRole("table").firstElementChild).toHaveTextContent("");
  });
  describe("generating a full calendar month", () => {
    test("using the day names as table headers", () => {
      render(Calendar, { monthName: "foobar", gamesList: [] });
      expect(screen.getAllByRole("columnheader")).toHaveLength(7);
      expect(screen.getByText("Sun")).toBeInTheDocument();
      expect(screen.getByText("Mon")).toBeInTheDocument();
      expect(screen.getByText("Tues")).toBeInTheDocument();
      expect(screen.getByText("Wed")).toBeInTheDocument();
      expect(screen.getByText("Thurs")).toBeInTheDocument();
      expect(screen.getByText("Fri")).toBeInTheDocument();
      expect(screen.getByText("Sat")).toBeInTheDocument();
    });
    test("rendering only two rows by default", () => {
      render(Calendar, { monthName: "foobar", gamesList: [] });
      const tableRows = screen.getAllByRole("row");
      expect(tableRows).toHaveLength(2); //* Header row + starting week row
      //* The starting week row has 7 cells, one for each day of the week to match the header row
      expect(screen.getAllByRole("cell")).toHaveLength(7);
    });
    test("if any games are in the list, then a normal month will render", () => {
      const homeTeam = { id: "1", teamLogo: "", teamName: "foo", cityName: "", abbreviation: "", wins: 1, losses: 0 };
      const awayTeam = { id: "1", teamLogo: "", teamName: "foo", cityName: "", abbreviation: "", wins: 0, losses: 1 };
      const game = BaseballGame.of({
        id: "1", date: "Thur April 05 2020 at 01:10 PM", homeTeam: homeTeam, awayTeam: awayTeam, promos: [], seriesGameNumber: 1, seriesGameCount: 3
      });
      const { rerender } = render(Calendar, { monthName: "April", gamesList: [game] });
      const daysRendered = screen.getAllByRole("cell");
      expect(daysRendered.length % 7).toBe(0); //* The total # of days rendered in the calendar always a multiple of 7
      expect(screen.getByText("5")).toBeInTheDocument();
      expect(screen.getAllByText(/missing logo/i)).toHaveLength(2); //* Each game day gets 2

      rerender({ monthName: "July", gamesList: [
        BaseballGame.of({ ...game, date: "Mon July 18 2023 at 06:15 PM" }), //? Turns out classes can be spread like regular JS objects!
        BaseballGame.of({ ...game, date: "Tues July 19 2023 at 10:40 AM" })
      ]});
      const julyDaysRendered = screen.getAllByRole("cell");
      expect(julyDaysRendered.length % 7).toBe(0);
      expect(screen.getByText("5")).toBeInTheDocument(); //* Previous days, even if off-days, get their day num
      expect(screen.getByText("18")).toBeInTheDocument(); //* Actual game days do as well
      expect(screen.getByText("19")).toBeInTheDocument();
      expect(screen.getAllByText(/missing logo/i)).toHaveLength(4); //* Two games this time, so 4 total logos rendered
    });
  });
  describe("altering the style", () => {
    test("providing classes to the root element", () => {
      const { rerender } = render(Calendar, { monthName: "", gamesList: [], tableClass: "foobar" });
      expect(screen.getByRole("table")).toHaveClass("foobar");

      rerender({ monthName: "", gamesList: [] });
      expect(screen.getByRole("table")).not.toHaveClass("foobar");
    });
    test("to render the Calendar in miniature form", () => {
      const { rerender } = render(Calendar, { monthName: "", gamesList: [] });
      //* Mini == false by default
      expect(screen.getByRole("table")).not.toHaveClass("mini-calendar");

      rerender({ monthName: "", gamesList: [], mini: true });
      expect(screen.getByRole("table")).toHaveClass("mini-calendar");
    });
  });
});