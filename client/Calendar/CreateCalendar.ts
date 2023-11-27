import { todaysSplitDate, getMonthFromDateStr } from "../HelperFuncs/DateExtension";
import type BaseballGame from "../Models/DataClasses";
import { MONTH_MAP } from "../Models/Month";
import { getDaysInMonth } from "date-fns";

export function CreateMonth(games: BaseballGame[]): string[][] {
  if (games.length === 0) { return [["", "", "", "", "", "", ""]]; }
  const exampleGame = games[0];

  const monthStr = getMonthFromDateStr(exampleGame.date);
  const [year, month] = todaysSplitDate();
  const thisMonth = (monthStr === "") ? month : monthStr; //* If monthStr is an emptyStr, use the current month
  const monthNum = MONTH_MAP[thisMonth] - 1; //* MONTH_MAP is 1-indexed so must subtract 1 to 0-index it
  const yearNum = parseInt(year);

  const startDate = new Date(yearNum, monthNum);
  const startDay = startDate.getDay(); //? 0 == Sunday, 6 == Saturday

  const startingWeek = CreateStartingWeek(startDay);

  const numOfDaysInThisMonth = getDaysInMonth(startDate);
  const remainingMonth = CreateRemainingMonth(startDay, numOfDaysInThisMonth);

  return [startingWeek, ...remainingMonth];
}

export function CreateStartingWeek(startDay: number): string[] {
  return Array.from({length: 7}, (_, i) => (i < startDay) ? "" : `${i - startDay + 1}`);
}

export function CreateRemainingMonth(startDay: number, numOfDays: number): string[][] {
  //* Handle negative startDay by flipping them, and handle any unexpected startDay num by using modulo
  const truncatedStartDay = (startDay < 0) ? ((startDay * -1) % 7) : (startDay % 7);
  const restOfMonth: string[][] = [];
  //* If starting on friday, we're only two days in by start of next week's sunday
  const daysPast = 7 - truncatedStartDay; //* Hence accounting for days passed in month so far!
  for (let i = 0; i <= 4; i++) { //* Represents weeks after first (using 0 to calculate below)
    const currentWeek: string[] = [];
    let emptyFinalWeek = true; //* Common for final weeks to be completely empty so rather than waste time rendering them, just skip
    for (let j = 1; j <= 7; j++) {
      const nextDayNum = (7 * i) + daysPast + j; //* Days passed in first week + day of this week + # days / week
      const dayToAdd = (nextDayNum > numOfDays) ? "" : `${nextDayNum}`;
      if (i === 4 && dayToAdd !== "") { emptyFinalWeek = false; } //* Found a filled in final week
      currentWeek.push(dayToAdd);
    }
    if (i === 4 && emptyFinalWeek) { break; } //* If final week and it was filled in with empty strings, don't add it
    restOfMonth.push(currentWeek);
  }
  return restOfMonth;
}

export function BaseballSeasonLength(games: BaseballGame[]) {
  const firstGame = games[0];
  const lastGame = games[games.length - 1];

  const firstMonth = getMonthFromDateStr(firstGame.date);
  const lastMonth = getMonthFromDateStr(lastGame.date);

  const firstMonthNum = MONTH_MAP[firstMonth];
  const lastMonthNum = MONTH_MAP[lastMonth];

  if (lastMonthNum < firstMonthNum) { return 0; } //* Invalid ordering
  const calendarDiff = lastMonthNum - firstMonthNum;
  return calendarDiff + 1; //* Must add 1 to be sure last month is counted
}