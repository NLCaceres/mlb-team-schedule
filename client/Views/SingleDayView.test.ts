import SingleDayView from "./SingleDayView.svelte";
import { render, screen } from "@testing-library/svelte";
import { vi, type SpyInstance } from "vitest";
import * as Api from "../API";

describe("renders the details of a single game", () => {
  let ApiSpy: SpyInstance;
  beforeEach(() => {
    ApiSpy = vi.spyOn(Api, "getSingleGame");
  })
  afterEach(() => {
    vi.restoreAllMocks();
  })
  test("depending on if it's provided by the API", () => {
    //* No game from the API, so render a "Day off" message
    ApiSpy.mockReturnValueOnce(undefined);
    const { rerender } = render(SingleDayView, { day: 14, monthName: "foobar" });
    expect(ApiSpy).toBeCalledWith("foobar", "14");
    expect(screen.getByText(/just a dodger's day off/i)).toBeInTheDocument();
    
    //* Render the game if provided by the API
    const homeTeam = { id: "1", teamLogo: "", teamName: "foo", cityName: "fizz", abbreviation: "", wins: 1, losses: 0 };
    const awayTeam = { id: "1", teamLogo: "", teamName: "bar", cityName: "buzz", abbreviation: "", wins: 0, losses: 1 };
    const game = { id: "1", date: "Thur April 05 2020 at 01:10 PM", homeTeam: homeTeam, awayTeam: awayTeam, promos: [], gameNumInSeries: 1, gamesInSeries: 3 };
    ApiSpy.mockReturnValueOnce(game);
    rerender({ day: 9, monthName: "april" });
    expect(screen.getByText("Thur April 5 2020 at 1:10 PM's Matchup:"));
    //* Away Team
    expect(screen.getByText(/buzz bar/)).toBeInTheDocument();
    expect(screen.getByText(/0 - 1/)).toBeInTheDocument();
    //* Home Team
    expect(screen.getByText(/fizz foo/)).toBeInTheDocument();
    expect(screen.getByText(/1 - 0/)).toBeInTheDocument();
    expect(screen.getByText("The First Game in a 3-day Series"));

    //* Add details about the promotions if it's a home game
    ApiSpy.mockReturnValueOnce({ ...game, homeTeam: { ...homeTeam, teamName: "Dodgers" } });
    rerender({ day: 9, monthName: "april" });
    expect(screen.getByText(/no dodgers promos today/i)).toBeInTheDocument();
    
    //* Render any promotions found
    ApiSpy.mockReturnValueOnce({ ...game, promos: [{ id: "bam", name: "bam", thumbnailUrl: "bam.jpg" }, { id: "boom", name: "boom", thumbnailUrl: "boom.jpg" }] });
    rerender({ day: 9, monthName: "april" });
    expect(screen.getByText("Promotions for Today")).toBeInTheDocument();
    const images = screen.getAllByRole("listitem");
    expect(images).toHaveLength(2);
    expect(images[0]).toHaveTextContent("bam");
    expect(images[0].firstElementChild).toHaveAttribute("src", "bam.jpg");
    expect(images[1]).toHaveTextContent("boom");
    expect(images[1].firstElementChild).toHaveAttribute("src", "boom.jpg");
  })
})