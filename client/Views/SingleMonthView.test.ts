import SingleMonthView from "./SingleMonthViewTest.svelte";
import { render, screen } from "@testing-library/svelte";
import { vi, type SpyInstance } from "vitest";
import { readable } from "svelte/store";
import * as Api from "../API";
import * as Navigator from "svelte-navigator";

/* //* Using a Test Component since a Router wrapper is required thanks to useLocation being used in the SingleMonthView component */
describe("renders a single month", () => {
  let LocationSpy: SpyInstance; 
  let ApiSpy: SpyInstance;
  beforeEach(() => {
    ApiSpy = vi.spyOn(Api, "getMonthsGames");
    LocationSpy = vi.spyOn(Navigator, "useLocation");
  })
  afterEach(() => {
    vi.restoreAllMocks();
  })
  test("depending on the useLocation hook + currentYear prop to create the subtitle header", () => {
    ApiSpy.mockReturnValue([]);
    LocationSpy.mockReturnValueOnce(readable({ pathname: "/March" }));
    const { rerender } = render(SingleMonthView, { currentYear: "2023" });
    expect(screen.getByText(/march 2023 Games/i)).toBeInTheDocument();

    LocationSpy.mockReturnValueOnce(readable({ pathname: "/april" }));
    rerender({ currentYear: "foobar" });
    //* Case-insensitive check to see "/april" turns into "April"
    expect(screen.getByText(/April foobar Games/)).toBeInTheDocument();
  })
  test("depending on the viewWidth to display a helpful note on Promotion availability", () => {
    ApiSpy.mockReturnValue([]);
    LocationSpy.mockReturnValueOnce(readable({ pathname: "/March" }));
    //* WHEN the innerWidth > 576
    global.innerWidth = 1024;
    const { rerender } = render(SingleMonthView, { currentYear: "2023" });
    //* THEN no notice to let the user know which games are at home with promotions
    expect(screen.queryByText("* indicates a home game with promotions")).not.toBeInTheDocument();
    //* WHEN the innerWidth > 576
    global.innerWidth = 768;
    rerender({ currentYear: "2023" });
    //* THEN no notice to let the user know which games are at home with promotions
    expect(screen.queryByText("* indicates a home game with promotions")).not.toBeInTheDocument();
    //* WHEN the innerWidth > 576
    global.innerWidth = 576;
    rerender({ currentYear: "2023" });
    //* THEN no notice to let the user know which games are at home with promotions
    expect(screen.queryByText("* indicates a home game with promotions")).not.toBeInTheDocument();

    //* WHEN the innerWidth < 576
    global.innerWidth = 575;
    rerender({ currentYear: "2023" });
    //* THEN show the notice to let the user know which games are at home with promotions
    expect(screen.getByText("* indicates a home game with promotions")).toBeInTheDocument();
  })
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
    const game = { id: "1", date: "Thur April 05 2020 at 01:10 PM", homeTeam: homeTeam, awayTeam: awayTeam, promos: [], gameNumInSeries: 1, gamesInSeries: 3 };
    ApiSpy.mockReturnValueOnce([game]);
    rerender({ currentYear: "2023" });
    expect(screen.getByRole("table")).toBeInTheDocument();
  })
})