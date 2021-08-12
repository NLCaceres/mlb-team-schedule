import type { Month } from '../../Models/Month'; //? As of TS 3.8, this syntax is used to import ONLY the type (rather than the whole file)

export function CreateStartingWeek(calendarMonth: Month): string[] {
  return Array.from({length: 7}, (_, i) => (i < calendarMonth.startDay) ? '' : `${i - calendarMonth.startDay + 1}`)
}

export function CreateRemainingMonth(calendarMonth: Month): string[][] {
  let restOfMonth: string[][] = [];
  //* If starting on friday, we're only two days in by start of next week's sunday
  const daysPast = 7 - calendarMonth.startDay; //* Hence days past in month so far!
  for (var i=0; i <= 4; i++) { //* Represents weeks after first (using 0 to calculate below)
    const currentWeek: string[] = [];
    for (var j=1; j <= 7; j++) {
      const nextDayNum = 7*i + daysPast + j; //* Days past in first week + day of this week + # days / week
      const dayToAdd = (nextDayNum > calendarMonth.numDays) ? '' : `${nextDayNum}`
      currentWeek.push(dayToAdd);
    }
    restOfMonth.push(currentWeek);
  } 
  return restOfMonth;
}