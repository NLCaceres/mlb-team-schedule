import SingleMonthView from "./SingleMonthViewTest.svelte";
import { render, screen } from "@testing-library/svelte";
import { vi, type SpyInstance } from "vitest";
import { readable } from "svelte/store";
import * as Api from "../API";
import * as SvelteRouting from "svelte-routing";

//? Using a Test Component since a Router wrapper is required thanks to useLocation being used in the SingleMonthView component
describe("renders a single month", () => {
  let LocationSpy: SpyInstance;
  let ApiSpy: SpyInstance;
  beforeEach(() => {
    ApiSpy = vi.spyOn(Api, "getMonthsGames");
    LocationSpy = vi.spyOn(SvelteRouting, "useLocation");
  });
  afterEach(() => {
    vi.restoreAllMocks();
  });
  test("depending on the useLocation hook + currentYear prop to create the subtitle header", () => {
    ApiSpy.mockReturnValue([]);
    LocationSpy.mockReturnValueOnce(readable({ pathname: "/March" }));
    const { rerender } = render(SingleMonthView, { currentYear: "2023" });
    expect(screen.getByText(/march 2023 Games/i)).toBeInTheDocument();

    LocationSpy.mockReturnValueOnce(readable({ pathname: "/april" }));
    rerender({ currentYear: "foobar" });
    //* Case-insensitive check to see "/april" turns into "April"
    expect(screen.getByText(/April foobar Games/)).toBeInTheDocument();
  });
  test("depending on if any games are returned by the API", async () => {
    LocationSpy.mockReturnValueOnce(readable({ pathname: "/March" }));
    ApiSpy.mockReturnValueOnce([]); //* WHEN no games returned
    const { rerender } = render(SingleMonthView, { currentYear: "2023" });
    expect(await screen.findByText(/sorry/i)).toBeInTheDocument(); //* THEN "Sorry!" message rendered!

    ApiSpy.mockReturnValueOnce(undefined); //* WHEN undefined is returned
    rerender({ currentYear: "2023" });
    expect(await screen.findByText(/sorry/i)).toBeInTheDocument(); //* THEN render a "Sorry!" message
    expect(screen.queryByRole("table")).not.toBeInTheDocument();

    const homeTeam = { id: "1", teamLogo: "", teamName: "foo", cityName: "", abbreviation: "", wins: 1, losses: 0 };
    const awayTeam = { id: "1", teamLogo: "", teamName: "foo", cityName: "", abbreviation: "", wins: 0, losses: 1 };
    const game = { id: "1", date: "Thur April 05 2020 at 01:10 PM", homeTeam: homeTeam, awayTeam: awayTeam, promos: [], seriesGameNumber: 1, seriesGameCount: 3 };
    ApiSpy.mockReturnValueOnce([game]); //* WHEN even just 1 game is returned
    rerender({ currentYear: "2023" }); //* THEN render a Calendar
    expect(await screen.findByRole("table")).toBeInTheDocument();
  });
});
