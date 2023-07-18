import { vi } from "vitest";
import { BaseballSeasonLength, CreateMonth, CreateRemainingMonth, CreateStartingWeek } from "./CreateCalendar";
import * as DateFns from "date-fns";

describe("provides utility functions for creating a data representation of a Calendar", () => {
  test("uses the Baseball game list to check the number of months in the season", () => {
    const homeTeam = { id: "1", teamLogo: "", teamName: "foo", cityName: "", abbreviation: "", wins: 1, losses: 0 };
    const awayTeam = { id: "1", teamLogo: "", teamName: "foo", cityName: "", abbreviation: "", wins: 0, losses: 1 };
    const game = { id: "1", date: "Thur March 20 2021 at 01:10 PM", homeTeam: homeTeam, awayTeam: awayTeam, promos: [], gameNumInSeries: 1, gamesInSeries: 3 };
    const gameList = [game, { ...game, date: "Sat June 30 2021 at 07:10 PM" }];
    //* June is the 6th month, March is the 3rd, so (6-3) + 1 = 4
    //* If 1 isn't added at the end, then it would be excluding June, i.e. March, April, May AND finally June
    expect(BaseballSeasonLength(gameList)).toBe(4);

    const invalidGameList = [{ ...game, date: "Sat June 30 2021 at 07:10 PM" }, game];
    expect(BaseballSeasonLength(invalidGameList)).toBe(0) //* If the first and last games are out of order, 0 is sent back
  })
  describe("creates a single month of the Calendar", () => {
    test("handling the starting week by prepending blank days until the starting day", () => {
      const startWeek = CreateStartingWeek(3); //* 0 == Sunday, 6 == Saturday, so 3 == Wed
      expect(startWeek).toHaveLength(7); //* Length is always 7 for each day of the week
      expect(startWeek).toStrictEqual(["", "", "", "1", "2", "3", "4"]);

      const diffStartweek = CreateStartingWeek(6);
      expect(diffStartweek).toHaveLength(7);
      expect(diffStartweek).toStrictEqual(["", "", "", "", "", "", "1"]);

      const invalidStartWeek = CreateStartingWeek(10);
      expect(invalidStartWeek).toHaveLength(7); //* Invalid weeks still produce a 7 item array
      expect(invalidStartWeek).toStrictEqual(["", "", "", "", "", "", ""]); //* But the whole week is empty
    })
    test("handles creating the remaining 4 to 5 weeks of the month", () => {
      const remainingWeeks = CreateRemainingMonth(2, 31); //* Month starts on Tuesday, & has 31 days
      expect(remainingWeeks).toHaveLength(4);
      //* Starting week is ["", "", "1", "2", "3", "4", "5"], so the 1st element of the remainder is "6"
      expect(remainingWeeks[0][0]).toBe("6");
      //* Weeks end num == Week start num + 6, i.e. start day == 6, end day therefore is 12
      expect(remainingWeeks[0][6]).toBe("12");
      //* So if start day for week one == 6, then, of course, start day for week two == 13, 
      //* i.e. next week start num == 1st week start num + 7
      expect(remainingWeeks[1][6]).toBe("19");
      expect(remainingWeeks[2][6]).toBe("26");
      //* Since 4 weeks produce 28 spaces to fill, but we only 26 spaces to fill "6" to "31"
      //* Therefore, the final array has 2 spaces at the end left empty
      expect(remainingWeeks[3]).toStrictEqual(["27", "28", "29", "30", "31", "", ""]);

      const diffRemainingWeeks = CreateRemainingMonth(0, 30); //* Sunday start, & 30 days
      //* Start week == ["1", "2", "3", "4", "5", "6", "7"]
      //* Remainder starts == "8", then "15", then "22", "29", 
      expect(diffRemainingWeeks).toHaveLength(4);
      expect(diffRemainingWeeks[3]).toStrictEqual(["29", "30", "", "", "", "", ""]);

      //* Friday and Saturday starts sometimes generate an extra week 
      //? Under the hood, the extra week is ALWAYS made, it's just not usually added to the final array since it's completely blank
      const fiveWeekRemainder = CreateRemainingMonth(6, 30);
      expect(fiveWeekRemainder).toHaveLength(5);
      expect(fiveWeekRemainder[4]).toStrictEqual(["30", "", "", "", "", "", ""]);

      const invalidRemainingWeeks = CreateRemainingMonth(11, 31);
      //* Even though 11 is not technically a valid start day, modulo causes the correct day to still be used
      //* i.e. 11 % 7 == 4 so Thursday is used!
      expect(invalidRemainingWeeks).toHaveLength(4);
      expect(invalidRemainingWeeks[0][0]).toBe("4"); //* Since 1st week starts on Thurs, 2nd week's Sunday is the 4th
      expect(invalidRemainingWeeks[3][6]).toBe("31"); //* And the 31st of the month perfectly falls on Saturday

      //* Similarly, negative values are flipped, so Thursday is used here too, producing the same month
      const negativeStartRemainingWeeks = CreateRemainingMonth(-4, 31);
      expect(negativeStartRemainingWeeks).toHaveLength(4);
      expect(negativeStartRemainingWeeks[0][0]).toBe("4");
      expect(negativeStartRemainingWeeks[3][6]).toBe("31");
    })
    test("creates a full calendar depending on a list of baseball games", () => {
      const emptyCalendarWeeks = CreateMonth([]); //* No list provided
      expect(emptyCalendarWeeks).toHaveLength(1); //* So empty 7 day single week returned
      expect(emptyCalendarWeeks[0]).toStrictEqual(["", "", "", "", "", "", ""]);
      
      //* Using spies here eliminates the guess work since CreateMonth() dynamically grabs the year
      //* which would make tests get unexpected results depending on the month/year they're run
      vi.spyOn(Date.prototype, "getDay").mockReturnValue(4);
      vi.spyOn(DateFns, "getDaysInMonth").mockReturnValue(31);
      const homeTeam = { id: "1", teamLogo: "", teamName: "foo", cityName: "", abbreviation: "", wins: 1, losses: 0 };
      const awayTeam = { id: "1", teamLogo: "", teamName: "foo", cityName: "", abbreviation: "", wins: 0, losses: 1 };
      const game = { id: "1", date: "Thur June 09 2023 at 07:10PM", homeTeam: homeTeam, awayTeam: awayTeam, promos: [], gameNumInSeries: 1, gamesInSeries: 3 };
      
      const normalCalendarWeeks = CreateMonth([game]);
      expect(normalCalendarWeeks).toHaveLength(5);
      expect(normalCalendarWeeks[0][4]).toBe("1"); //* Starting week used and Thursday is day 1
      expect(normalCalendarWeeks[4][6]).toBe("31"); //* So day 31 lands perfectly at the end of the 2d array

      //! Edge case: if, for some reason, an invalid dateStr was passed in, then no month can be grabbed to calculate the month's shape
      //* Solution is: Provide backup, specifically the current month is used, which makes it tricky to test
      
      vi.restoreAllMocks(); //* restoreAllMocks & mockRestore() ONLY works on mocks from spyOn()
    })
  })
})