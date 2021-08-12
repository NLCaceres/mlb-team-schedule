export enum Day {
  Sunday,
  Monday,
  Tuesday,
  Wednesday,
  Thursday,
  Friday,
  Saturday
}

export interface Month {
  monthName: string,
  startDay: Day,
  numDays: number,
}