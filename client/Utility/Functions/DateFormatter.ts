//* General format of strings is ShortWeekDay Month DayNum Year at Time PM
//* Ex: Thur June 09 2021 at 07:10 PM

export default function dateFormatter(dateStr: string) { //* Idea: Split, modify, join
  if (!dateStr || dateStr.length === 0) return ''; //* Undefined or invalid string
  const splitStr = dateStr.split(' ');
  splitStr[2] = removeLeadingZero(splitStr[2]); //* Format June 09 -> June 9
  splitStr[5] = removeLeadingZero(splitStr[5]); //* Format 07:10 PM -> 7:10 PM
  return splitStr.join(' ');
}

export function timeFormatter(timeStr: string) {
  if (!timeStr || timeStr.length === 0) return '';
  const splitStr = timeStr.split(' ')
  const timeWithoutLeadingZero = removeLeadingZero(splitStr[5]);
  return `${timeWithoutLeadingZero} ${splitStr[6]}`
}

export function removeLeadingZero(strWithZero: string) {
  return (strWithZero.charAt(0) === '0') ? strWithZero.slice(1) : strWithZero;
}