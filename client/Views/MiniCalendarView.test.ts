import MiniCalendarView from "./MiniCalendarView.svelte";
import { render, screen } from "@testing-library/svelte";
import { vi, type MockInstance } from "vitest";
import * as Api from "../API";
import * as DateHelpers from "../HelperFuncs/DateExtension";

//? Generally innerWidth starts at 1024 and innerHeight starts at 768, BUT being explicit might help CI tests
const innerWidthStart = global.innerWidth;
const innerHeightStart = global.innerHeight;

describe("renders several calendar months to briefly detail game info for each day", () => {
  let ApiSpy: MockInstance;
  let DateHelperSpy: MockInstance;
  beforeEach(() => {
    global.innerWidth = innerWidthStart;
    global.innerHeight = innerHeightStart;
    ApiSpy = vi.spyOn(Api, "getFullSchedule");
    DateHelperSpy = vi.spyOn(DateHelpers, "todaysSplitLocalDate");
  });
  afterEach(() => {
    vi.restoreAllMocks();
  });
  test("depending on viewport width & height to display the view's subtitle", () => {
    ApiSpy.mockReturnValue([]);
    const { rerender } = render(MiniCalendarView, { months: [] });
    expect(screen.getByText("Click the date to show game specifics"));

    global.innerHeight = 1125; //* This would qualify as "1125 > innerWidth + 100" i.e. 1125 > 1024 + 100 -> 1125 > 1124
    rerender({ months: [] }); //* Treating this pretty big screen as a tablet
    expect(screen.getByText("Tap the date to show game specifics"));

    global.innerHeight = 728; //* For a more normal tablet size
    global.innerWidth = 500;
    rerender({ months: [] });
    expect(screen.getByText("Tap the date to show game specifics"));

    global.innerHeight = 768; //* Mid to Large Desktops render "Click"
    global.innerWidth = 1025;
    rerender({ months: [] });
    expect(screen.getByText("Click the date to show game specifics"));

    global.innerHeight = 1126; //* Despite "1126 > innerWidth + 100", innerWidth > 1024 forces the view to use "Click"
    rerender({ months: [] });
    expect(screen.getByText("Click the date to show game specifics"));
  });
  test("using hyperlinks if in a small viewport", async () => {
    const homeTeam = { id: "1", teamLogo: "", teamName: "foo", cityName: "fizz", abbreviation: "", wins: 1, losses: 0 };
    const awayTeam = { id: "1", teamLogo: "", teamName: "bar", cityName: "buzz", abbreviation: "", wins: 0, losses: 1 };
    const game = { id: "1", date: "Thur April 05 2020 at 01:10 PM", homeTeam: homeTeam, awayTeam: awayTeam, promos: [], seriesGameNumber: 1, seriesGameCount: 3 };
    ApiSpy.mockReturnValue([game]);
    const { rerender } = render(MiniCalendarView, { months: ["April"] });
    const expectedText = "Today's Game is:";
    const button = await screen.findByRole("button", { name: expectedText });
    expect(button).toBeInTheDocument();

    //* Convert the button into a hyperlink (<a> tag) on mobile screens
    DateHelperSpy.mockReturnValueOnce(["year", "3", "20"]);
    global.innerWidth = 575;
    rerender({ months: ["April"] });
    const link = await screen.findByRole("link", { name: expectedText });
    expect(link).toBeInTheDocument();
    expect(link).toHaveAttribute("href", "/march/20");
  });
  test("depending on the schedule returned by the API to render a full calendar", async () => {
    //* If undefined schedule, "sorry" message is rendered
    ApiSpy.mockReturnValue([]);
    const { rerender } = render(MiniCalendarView, { months: [] });
    const sorryMessage = await screen.findByText("Sorry! Seems we hit a snag!");
    expect(sorryMessage).toBeInTheDocument();

    //* Even if the months prop is used, no calendar is displayed if no schedule is returned by the API
    rerender({ months: ["March", "April", "May", "June"] });
    expect(await screen.findByText("Sorry! Seems we hit a snag!")).toBeInTheDocument();
    expect(screen.queryByRole("table")).not.toBeInTheDocument();

    const homeTeam = { id: "1", teamLogo: "", teamName: "foo", cityName: "fizz", abbreviation: "", wins: 1, losses: 0 };
    const awayTeam = { id: "1", teamLogo: "", teamName: "bar", cityName: "buzz", abbreviation: "", wins: 0, losses: 1 };
    const game = { id: "1", date: "Thur April 05 2020 at 01:10 PM", homeTeam: homeTeam, awayTeam: awayTeam, promos: [], seriesGameNumber: 1, seriesGameCount: 3 };
    ApiSpy.mockReturnValue([game]);
    //* If the API returns a normal list, BUT the months prop is empty, then "Sorry" error message rendered instead
    rerender({ months: [] });
    const emptyCalendarErrMessage = await screen.findByText("Sorry! Seems we hit a snag!");
    expect(emptyCalendarErrMessage).toBeInTheDocument();

    //* Still getting normal list from API BUT game found is in April, so it's not displayed
    rerender({ months: ["March"] });
    expect(await screen.findAllByRole("table")).toHaveLength(1); //* ONLY March is rendered
    expect(screen.getByText("March")).toBeInTheDocument();
    expect(screen.queryByText("April")).not.toBeInTheDocument();
    expect(screen.getAllByRole("cell")).toHaveLength(7); //* Empty calendar months w/out a game just render 7 empty days

    //* Possibly too obscure of an edge case but the game date compares month and day BUT NOT year
    //* So despite the game being April 05 2020, and the current year being 2023, the game is injected into April's calendar
    rerender({ months: ["April"] });
    expect(await screen.findAllByRole("table")).toHaveLength(1); //* ONLY March is rendered
    expect(screen.getByText("April")).toBeInTheDocument();
    expect(screen.queryByText("March")).not.toBeInTheDocument();
    expect(screen.getAllByText(/missing/i)).toHaveLength(2); //* Single day in April filled

    //* Extra months are rendered based on "months" prop expecting that games will occur in those months
    //* Here only April is filled, the others get simple 7 day renderings, all based on gamesList received from API
    rerender({ months: ["April", "May", "June"] });
    expect(await screen.findAllByRole("table")).toHaveLength(3);
    expect(screen.getByText("April")).toBeInTheDocument();
    expect(screen.getByText("May")).toBeInTheDocument();
    expect(screen.getByText("June")).toBeInTheDocument();
    expect(screen.getAllByText(/missing/i)).toHaveLength(2);
  });
});
