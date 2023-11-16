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
  test("depending on if it's provided by the API", async () => {
    //* No game from the API, so render a "Day off" message
    ApiSpy.mockReturnValueOnce(Promise.resolve(undefined));
    const { rerender } = render(SingleDayView, { day: 14, monthName: "foobar" });
    expect(ApiSpy).toBeCalledWith("foobar", "14");
    expect(await screen.findByText(/just a dodgers day off/i)).toBeInTheDocument();
    
    //* Render the game if provided by the API
    const homeTeam = { id: "1", teamLogo: "", teamName: "foo", cityName: "fizz", abbreviation: "", wins: 1, losses: 0 };
    const awayTeam = { id: "1", teamLogo: "", teamName: "bar", cityName: "buzz", abbreviation: "", wins: 0, losses: 1 };
    const game = { id: "1", date: "Thur April 05 2020 at 01:10 PM", homeTeam: homeTeam, awayTeam: awayTeam, promos: [], gameNumInSeries: 1, gamesInSeries: 3 };
    ApiSpy.mockReturnValueOnce(Promise.resolve(game));
    rerender({ day: 9, monthName: "april" });
    expect(await screen.findByText("Thur April 5 2020 at 1:10 PM's Matchup:"));
    //* Away Team
    expect(await screen.findByText(/buzz bar/)).toBeInTheDocument();
    expect(await screen.findByText(/0 - 1/)).toBeInTheDocument();
    //* Home Team
    expect(await screen.findByText(/fizz foo/)).toBeInTheDocument();
    expect(await screen.findByText(/1 - 0/)).toBeInTheDocument();
    expect(await screen.findByText("The First Game in a 3-day Series"));

    //* Add details about the promotions if it's a home game
    ApiSpy.mockReturnValueOnce(Promise.resolve({ ...game, homeTeam: { ...homeTeam, teamName: "Dodgers" } }));
    rerender({ day: 9, monthName: "april" });
    expect(await screen.findByText(/no dodgers promos today/i)).toBeInTheDocument();
    
    //* Render any promotions found
    ApiSpy.mockReturnValueOnce(
      Promise.resolve({ ...game, promos: [{ id: "bam", name: "bam", thumbnailUrl: "bam.jpg" }, { id: "boom", name: "boom", thumbnailUrl: "boom.jpg" }] })
    );
    rerender({ day: 9, monthName: "april" });
    expect(await screen.findByText("Promotions for Today")).toBeInTheDocument();
    const images = screen.getAllByRole("listitem");
    expect(images).toHaveLength(2);
    expect(images[0]).toHaveTextContent("bam");
    expect(images[0].firstElementChild).toHaveAttribute("src", "bam.jpg");
    expect(images[1]).toHaveTextContent("boom");
    expect(images[1].firstElementChild).toHaveAttribute("src", "boom.jpg");

    //* WHEN catching an error from the API
    ApiSpy.mockRejectedValue(new Error('Unexpected Error'));
    rerender({ day: 9, monthName: "april" });
    //* THEN the view will get an undefined value, resetting itself to an "Off-Day"
    expect(await screen.findByText(/just a dodgers day off/i)).toBeInTheDocument();
    //? BUT when that error is caught, a real user will just see the view navigate back to the homepage
    //? Unfortunately, Svelte-navigator is not setup in a way that lets Testing-Library render route changes
  })
})