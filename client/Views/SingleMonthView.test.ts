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
  test("depending on if any games are returned by the API", () => {
    LocationSpy.mockReturnValueOnce(readable({ pathname: "/March" }));
    ApiSpy.mockReturnValueOnce([]); //* Renders even if empty
    const { rerender } = render(SingleMonthView, { currentYear: "2023" });
    expect(screen.getByRole("table")).toBeInTheDocument();

    ApiSpy.mockReturnValueOnce(undefined);
    rerender({ currentYear: "2023" }); //* Only render a "Sorry!" message if undefined found
    expect(screen.queryByRole("table")).not.toBeInTheDocument();
    expect(screen.getByText(/sorry/i)).toBeInTheDocument();

    const homeTeam = { id: "1", teamLogo: "", teamName: "foo", cityName: "", abbreviation: "", wins: 1, losses: 0 };
    const awayTeam = { id: "1", teamLogo: "", teamName: "foo", cityName: "", abbreviation: "", wins: 0, losses: 1 };
    const game = { id: "1", date: "Thur April 05 2020 at 01:10 PM", homeTeam: homeTeam, awayTeam: awayTeam, promos: [], seriesGameNumber: 1, seriesGameCount: 3 };
    ApiSpy.mockReturnValueOnce([game]);
    rerender({ currentYear: "2023" });
    expect(screen.getByRole("table")).toBeInTheDocument();
  });
});
