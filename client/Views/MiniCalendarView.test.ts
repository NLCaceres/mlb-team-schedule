import MiniCalendarView from "./MiniCalendarView.svelte";
import { render, screen } from "@testing-library/svelte";
import { vi, type SpyInstance } from "vitest";
import * as Api from "../API";
import * as DateHelpers from '../HelperFuncs/DateExtension';

const innerWidthStart = global.innerWidth; //* Defaults to 1024
const innerHeightStart = global.innerHeight; //* Defaults to 768

describe("renders several calendar months to briefly detail game info for each day", () => {
  let ApiSpy: SpyInstance;
  let DateHelperSpy: SpyInstance;
  beforeEach(() => {
    global.innerWidth = innerWidthStart;
    global.innerHeight = innerHeightStart;
    ApiSpy = vi.spyOn(Api, "getFullSchedule");
    DateHelperSpy = vi.spyOn(DateHelpers, "todaysSplitDate");
  })
  afterEach(() => {
    vi.restoreAllMocks();
  })
  test("depending on viewport width & height as well as the current year to set the view's subtitle", () => {
    ApiSpy.mockReturnValue(undefined);
    const expectedPrefix = "Below you'll find a full list of the Dodgers Promo schedule";
    const expectedSuffix = "the date will show you the details!";
    const { rerender } = render(MiniCalendarView, { months: [], currentYear: "2023" });
    expect(screen.getByText(`${expectedPrefix} 2023. Clicking ${expectedSuffix}`));

    global.innerHeight = 1125; //* This would qualify as "1125 > innerWidth + 100" i.e. 1125 > 1024 + 100 -> 1125 > 1124
    rerender({ months: [], currentYear: "2023" }); //* Treating this pretty big screen as a tablet
    expect(screen.getByText(`${expectedPrefix} 2023. Tapping ${expectedSuffix}`));

    global.innerHeight = 728; //* For a more normal tablet size
    global.innerWidth = 500;
    rerender({ months: [], currentYear: "2023" });
    expect(screen.getByText(`${expectedPrefix} 2023. Tapping ${expectedSuffix}`));

    global.innerHeight = 768; //* Mid to Large Desktops render "Clicking"
    global.innerWidth = 1025;
    rerender({ months: [], currentYear: "2023" });
    expect(screen.getByText(`${expectedPrefix} 2023. Clicking ${expectedSuffix}`));

    global.innerHeight = 1126; //* Despite "1126 > innerWidth + 100", innerWidth > 1024 forces the view to use "Clicking"
    rerender({ months: [], currentYear: "2023" });
    expect(screen.getByText(`${expectedPrefix} 2023. Clicking ${expectedSuffix}`));
  })
  test("using hyperlinks if in a small viewport", async () => {
    const homeTeam = { id: "1", teamLogo: "", teamName: "foo", cityName: "fizz", abbreviation: "", wins: 1, losses: 0 };
    const awayTeam = { id: "1", teamLogo: "", teamName: "bar", cityName: "buzz", abbreviation: "", wins: 0, losses: 1 };
    const game = { id: "1", date: "Thur April 05 2020 at 01:10 PM", homeTeam: homeTeam, awayTeam: awayTeam, promos: [], gameNumInSeries: 1, gamesInSeries: 3 };
    ApiSpy.mockReturnValue([game]);
    const { rerender } = render(MiniCalendarView, { months: [], currentYear: "2023" });
    const expectedText = "Today's Game is:";
    const button = await screen.findByRole("button");
    expect(button).toHaveTextContent(expectedText);

    //* Convert the button into a hyperlink (<a> tag) on mobile screens
    DateHelperSpy.mockReturnValueOnce(["year", "3", "20"]);
    global.innerWidth = 575;
    rerender({ months: [], currentYear: "2023" });
    const link = await screen.findByRole("link");
    expect(link).toHaveTextContent(expectedText);
    expect(link).toHaveAttribute("href", "March/20");
  })
  test("depending on the schedule returned by the API to render a full calendar", async () => {
    //* If undefined schedule, "sorry" message is rendered
    ApiSpy.mockReturnValue(undefined);
    const { rerender } = render(MiniCalendarView, { months: [], currentYear: "2023" });
    const sorryMessage = await screen.findByText("Sorry! Seems we hit a snag!");
    expect(sorryMessage).toBeInTheDocument();

    //* Even if the months prop is used, no calendar is displayed if no schedule is returned by the API
    rerender({ months: ["March", "April", "May", "June"], currentYear: "2022" });
    expect(await screen.findByText("Sorry! Seems we hit a snag!")).toBeInTheDocument();
    expect(screen.queryByRole("table")).not.toBeInTheDocument();

    const homeTeam = { id: "1", teamLogo: "", teamName: "foo", cityName: "fizz", abbreviation: "", wins: 1, losses: 0 };
    const awayTeam = { id: "1", teamLogo: "", teamName: "bar", cityName: "buzz", abbreviation: "", wins: 0, losses: 1 };
    const game = { id: "1", date: "Thur April 05 2020 at 01:10 PM", homeTeam: homeTeam, awayTeam: awayTeam, promos: [], gameNumInSeries: 1, gamesInSeries: 3 };
    ApiSpy.mockReturnValue([game]);
    //* If the API returns a normal list, BUT the months prop is empty, then no calendar months are rendered
    rerender({ months: [], currentYear: "2023" });
    const button = await screen.findByText("Today's Game is:");
    const calendarContainer = button.parentElement!.nextElementSibling;
    expect(calendarContainer).toBeEmptyDOMElement();

    //* Still getting normal list from API BUT game found is in April, so it's not displayed
    rerender({ months: ["March"], currentYear: "2023" });
    expect(await screen.findAllByRole("table")).toHaveLength(1); //* ONLY March is rendered
    expect(screen.getByText("March")).toBeInTheDocument();
    expect(screen.queryByText("April")).not.toBeInTheDocument();
    expect(screen.getAllByRole("cell")).toHaveLength(7); //* Empty calendar months w/out a game just render 7 empty days

    //* Possibly too obscure of an edge case but the game date compares month and day BUT NOT year
    //* So despite the game being April 05 2020, and the current year being 2023, the game is injected into April's calendar
    rerender({ months: ["April"], currentYear: "2023" });
    expect(await screen.findAllByRole("table")).toHaveLength(1); //* ONLY March is rendered
    expect(screen.getByText("April")).toBeInTheDocument();
    expect(screen.queryByText("March")).not.toBeInTheDocument();
    expect(screen.getAllByText(/missing/i)).toHaveLength(2); //* Single day in April filled

    //* Extra months are rendered based on "months" prop expecting that games will occur in those months
    //* Here only April is filled, the others get simple 7 day renderings, all based on gamesList received from API
    rerender({ months: ["April", "May", "June"], currentYear: "2022" });
    expect(await screen.findAllByRole("table")).toHaveLength(3);
    expect(screen.getByText("April")).toBeInTheDocument();
    expect(screen.getByText("May")).toBeInTheDocument();
    expect(screen.getByText("June")).toBeInTheDocument();
    expect(screen.getAllByText(/missing/i)).toHaveLength(2);
  })
})