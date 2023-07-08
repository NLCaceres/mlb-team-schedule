//! Funcs specific to handle the expected formatted strings from the API
//* General format of strings is ShortWeekDay Month DayNum Year at Time PM
//* Ex: Thur June 09 2021 at 07:10 PM
export default function getReadableDate(dateStr: string) {
  if (dateStr.length === 0) { return "" } //* Undefined or invalid string

  const splitStr = dateStr.split("at"); //* Should have ["Thur June 09 2021", "07:10 PM"]

  if (splitStr.length != 2) { return "" } //* Probably not a valid string

  const formattedDate = dateFormatter(splitStr[0]);
  const formattedTime = timeFormatter(splitStr[1]);

  return `${formattedDate} at ${formattedTime}`.trim(); //* Ensure no empty space if formattedTime returns an empty string
}
export function dateFormatter(dateStr: string) { //* Idea: Split, modify, join
  if (dateStr.length === 0) { return "" } //* Undefined or invalid string

  const splitStr = dateStr.trim().split(" ");

  if (splitStr.length != 4) { return "" } //* Should have ["Thur", "June", "09", "2021"]
  splitStr[2] = removeLeadingZero(splitStr[2]); //* Turn the "09" into "9"

  return splitStr.join(" "); //* "Thur June 9 2021" instead of "Thur June 09 2021"
}
//* Expect the general date format from the API i.e. Thur June 09 2021 at 07:10 PM
//* Extract 7:10 PM from the date string
export function getTimeFromDateStr(dateStr: string) {
  if (dateStr.length === 0) { return "" }

  const splitStr = dateStr.split("at"); //* Should have ["Thur June 09 2021", "07:10 PM"]

  if (splitStr.length != 2) { return "" } //* Probably not a valid string
  
  return timeFormatter(splitStr[1])
}
export function timeFormatter(timeStr: string) {
  if (timeStr.length === 0) { return "" }

  const splitStr = timeStr.trim().split(" "); //* Remove any leading empty space, i.e. " 07:10 PM"

  if (splitStr.length != 2) { return "" } //* Should have ["07:10", "PM"]
  const timeWithoutLeadingZero = removeLeadingZero(splitStr[0]);

  return `${timeWithoutLeadingZero} ${splitStr[1]}`;
}

//! Helpers
export function removeLeadingZero(strWithZero: string) {
  let i = 0;
  while(strWithZero[i] == "0") { i++ }
  return strWithZero.slice(i);
}
//* Getters
export function utcDate() {
  return new Date().toISOString();
}
export function currentYear() {
  const currentDatetime = utcDate(); //? Should be YYYY-MM-DDTHH:MM:SS.SSSZ
  return currentDatetime.split("-")[0] //* So first index should contain "YYYY"
}