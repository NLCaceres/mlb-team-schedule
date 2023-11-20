import SingleDayView from "./SingleDayView.svelte";
import { render, screen } from "@testing-library/svelte";
import { vi, type SpyInstance } from "vitest";
import BaseballGame, { type BaseballTeam } from "../Models/DataClasses";
import * as Api from "../API";

describe("renders the details of a single game", () => {
  let ApiSpy: SpyInstance;
  let homeTeam: BaseballTeam; let awayTeam: BaseballTeam;
  let game: BaseballGame;
  beforeEach(() => {
    ApiSpy = vi.spyOn(Api, "getSingleGame");
    homeTeam = { id: "1", teamLogo: "", teamName: "foo", cityName: "fizz", abbreviation: "", wins: 1, losses: 0 };
    awayTeam = { id: "1", teamLogo: "", teamName: "bar", cityName: "buzz", abbreviation: "", wins: 0, losses: 1 };
    game = BaseballGame.of({
      id: "1", date: "Thur April 05 2020 at 01:10 PM",
      homeTeam: homeTeam, awayTeam: awayTeam, promos: [],
      seriesGameNumber: 1, seriesGameCount: 3
    });
  })
  afterEach(() => {
    vi.restoreAllMocks();
  })
  describe("if the Game was fetched", () => {
    test("successfully", async () => {
      //* No game from the API, so render a "Day off" message
      ApiSpy.mockReturnValueOnce(Promise.resolve(undefined));
      const { rerender } = render(SingleDayView, { day: 14, monthName: "foobar" });
      expect(ApiSpy).toBeCalledWith("foobar", "14");
      expect(await screen.findByText(/just a dodgers day off/i)).toBeInTheDocument();
      
      //* WHEN a game is successfully fetched from the API
      ApiSpy.mockReturnValueOnce(Promise.resolve(game));
      rerender({ day: 9, monthName: "april" });
      //* THEN the day is rendered with a home and away team at minimum
      expect(await screen.findByText("Thur April 5 2020 at 1:10 PM's Matchup:"));
      //* Away Team
      expect(await screen.findByText(/buzz bar/)).toBeInTheDocument();
      expect(await screen.findByText(/0 - 1/)).toBeInTheDocument();
      //* Home Team
      expect(await screen.findByText(/fizz foo/)).toBeInTheDocument();
      expect(await screen.findByText(/1 - 0/)).toBeInTheDocument();
      expect(await screen.findByText("The First Game in a 3-day Series"));

      //* WHEN catching an error from the API
      ApiSpy.mockRejectedValue(new Error('Unexpected Error'));
      rerender({ day: 9, monthName: "april" });
      //* THEN the view will get an undefined value, resetting itself to an "Off-Day"
      expect(await screen.findByText(/just a dodgers day off/i)).toBeInTheDocument();
      //? BUT when that error is caught, a real user will just see the view navigate back to the homepage
      //? Unfortunately, Svelte-navigator is not setup in a way that lets Testing-Library render route changes
    })
    describe("and may render its promotions", () => {
      test("if available", async () => {
        //* Render any promotions found REGARDLESS of home team
        const promoBaseballGame = BaseballGame.of({
          ...game, promos: [{ id: "bam", name: "bam", thumbnailUrl: "bam.jpg" }, { id: "boom", name: "boom", thumbnailUrl: "boom.jpg" }]
        });
        ApiSpy.mockReturnValueOnce(Promise.resolve(promoBaseballGame));
        render(SingleDayView, { day: 14, monthName: "foobar" });
        expect(await screen.findByText("Promotions for Today")).toBeInTheDocument();
        const images = screen.getAllByRole("listitem");
        expect(images).toHaveLength(2);
        expect(images[0]).toHaveTextContent("bam");
        expect(images[0].firstElementChild).toHaveAttribute("src", "bam.jpg");
        expect(images[1]).toHaveTextContent("boom");
        expect(images[1].firstElementChild).toHaveAttribute("src", "boom.jpg");
      })
      test("unless there are none, so, instead, it renders a message based on home vs away", async () => {
        //* WHEN the home team of the game is the user defined one (commonly "Dodgers")
        const homeBaseballGame = BaseballGame.of({ ...game, homeTeam: { ...homeTeam, teamName: "Dodgers" } });
        ApiSpy.mockReturnValueOnce(Promise.resolve(homeBaseballGame));
        const { rerender } = render(SingleDayView, { day: 14, monthName: "foobar" });
        //* THEN the team name is used in the message
        expect(await screen.findByText(/no dodgers promos today/i)).toBeInTheDocument();

        //* WHEN the home team of the game is NOT the user defined one (commonly "Dodgers")
        const awayBaseballGame = BaseballGame.of({ ...game, homeTeam: { ...homeTeam, teamName: "Angels" } });
        ApiSpy.mockReturnValueOnce(Promise.resolve(awayBaseballGame));
        rerender({ day: 9, monthName: "april" });
        //* THEN the message notifies the user their home team is away
        expect(await screen.findByText(/the Dodgers are away/i)).toBeInTheDocument();
      })
      test("as well as a note if special tickets required", async () => {
        //* CURRENTLY WHEN the promotion name ends in Ticket Package
        const ticketPackagePromoBaseballGame = BaseballGame.of({
          ...game, promos: [{ id: "bam", name: "bam Ticket Package", thumbnailUrl: "bam.jpg" }]
        });
        ApiSpy.mockReturnValueOnce(Promise.resolve(ticketPackagePromoBaseballGame));
        const { rerender } = render(SingleDayView, { day: 14, monthName: "foobar" });
        expect(await screen.findByText("Promotions for Today")).toBeInTheDocument();
        expect(screen.getAllByRole("listitem")).toHaveLength(1);
        //* THEN the user is notified special ticket may be necessary
        expect(screen.getByText(/promotions today may require special tickets/i)).toBeInTheDocument();

        //* WHEN the promotion name includes anything else
        const normalTicketPromoBaseballGame = BaseballGame.of({
          ...game, promos: [{ id: "bam", name: "bam Ticket", thumbnailUrl: "bam.jpg" }]
        });
        ApiSpy.mockReturnValueOnce(Promise.resolve(normalTicketPromoBaseballGame));
        rerender({ day: 14, monthName: "foobar" });
        expect(await screen.findByText("Promotions for Today")).toBeInTheDocument();
        //* THEN the message will not render
        expect(screen.queryByText(/promotions today may require special tickets/i)).not.toBeInTheDocument();

        //* WHEN the promotion name includes "Ticket Package" BUT in a different case
        const wrongCaseTicketPackagePromoBaseballGame = BaseballGame.of({
          ...game, promos: [{ id: "bam", name: "bam ticket package", thumbnailUrl: "bam.jpg" }]
        });
        ApiSpy.mockReturnValueOnce(Promise.resolve(wrongCaseTicketPackagePromoBaseballGame));
        rerender({ day: 14, monthName: "foobar" });
        expect(await screen.findByText("Promotions for Today")).toBeInTheDocument();
        //* THEN the message will not render
        expect(screen.queryByText(/promotions today may require special tickets/i)).not.toBeInTheDocument();
      })
    })
  })
})