//! Funcs specific to handle the expected formatted strings from the API
//* General format of strings is ShortWeekDay Month DayNum Year at Time PM
//* Ex: Thur June 09 2021 at 07:10 PM
export default function getReadableDate(dateStr: string) {
  if (dateStr.length === 0) { return ""; } //* Undefined or invalid string

  const splitStr = dateStr.split(" at "); //* Should have ["Thur June 09 2021", "07:10 PM"]

  if (splitStr.length != 2) { return ""; } //* Probably not a valid string

  const formattedDate = dateFormatter(splitStr[0]);
  const formattedTime = timeFormatter(splitStr[1]);

  return `${formattedDate} at ${formattedTime}`.trim(); //* Ensure no empty space if formattedTime returns an empty string
}
export function dateFormatter(dateStr: string) { //* Idea: Split, modify, join
  if (dateStr.length === 0) { return ""; } //* Undefined or invalid string

  const splitStr = dateStr.trim().split(" ");

  if (splitStr.length != 4) { return ""; } //* Should have ["Thur", "June", "09", "2021"]
  splitStr[2] = removeLeadingZero(splitStr[2]); //* Turn the "09" into "9"

  return splitStr.join(" "); //* "Thur June 9 2021" instead of "Thur June 09 2021"
}
export function getDateElemsFromDateStr(dateStr: string) {
  if (dateStr.length === 0) { return ""; } //* Undefined or invalid string
  const splitStr = dateStr.split(" ");

  //* Should be 4 words i.e. "Thur June 9 2021"
  if (splitStr.length <= 3) { return ""; }

  return [splitStr[3], splitStr[1], splitStr[2]]; //* Expect: [Year, Month, Day] strings
}
export function getMonthFromDateStr(dateStr: string) {
  if (dateStr.length === 0) { return ""; } //* Undefined or invalid string
  const splitStr = dateStr.split(" ");

  //* Since expected format of dateStr is "Thur June 9 2021", there must be at least 2 words, i.e. "Thur June"
  if (splitStr.length <= 1) { return ""; }

  return splitStr[1]; //* At index 1 should be June, i.e. the month
}
export function getDayFromDateStr(dateStr: string) {
  if (dateStr.length === 0) { return ""; } //* Undefined or invalid string
  const splitStr = dateStr.split(" ");

  if (splitStr.length <= 2) { return ""; }

  return splitStr[2]; //* At index 2 should be "09", which parseInt can convert into "9"
}

//* Expect the general date format from the API i.e. Thur June 09 2021 at 07:10 PM
//* Extract 7:10 PM from the date string
export function getTimeFromDateStr(dateStr: string) {
  if (dateStr.length === 0) { return ""; }

  const splitStr = dateStr.split(" at "); //* Should have ["Thur June 09 2021", "07:10 PM"]

  if (splitStr.length != 2) { return ""; } //* Probably not a valid string

  return timeFormatter(splitStr[1]);
}
export function timeFormatter(timeStr: string) {
  if (timeStr.length === 0) { return ""; }

  const splitStr = timeStr.trim().split(" "); //* Remove any leading empty space, i.e. " 07:10 PM"

  if (splitStr.length != 2) { return ""; } //* Should have ["07:10", "PM"]
  const timeWithoutLeadingZero = removeLeadingZero(splitStr[0]);

  return `${timeWithoutLeadingZero} ${splitStr[1]}`;
}

//! Helpers
export function removeLeadingZero(strWithZero: string) {
  let i = 0;
  while(strWithZero[i] == "0") { i++; }
  return strWithZero.slice(i);
}
//* Getters
export function utcDate() {
  return new Date().toISOString();
}
export function localDate() {
  return new Date().toString();
}
export function todaysSplitUtcDate() {
  const currentDatetime = new Date();
  const year = currentDatetime.getUTCFullYear();
  const month = currentDatetime.getUTCMonth(); //? Months are 0-indexed, so MUST add 1 to get actual month number
  const day = currentDatetime.getUTCDate();
  return [`${year}`, `${month + 1}`, `${day}`]; //* Useful for destructuring
}
export function todaysSplitLocalDate() {
  const currentDatetime = new Date();
  const year = currentDatetime.getFullYear();
  const month = currentDatetime.getMonth();
  const day = currentDatetime.getDate();
  return [`${year}`, `${month + 1}`, `${day}`]; //* Useful for destructuring
}
export function currentYear() {
  const [thisYear] = todaysSplitLocalDate();
  return `${thisYear}`;
}