import getReadableDate, { dateFormatter, getTimeFromDateStr, timeFormatter, removeLeadingZero,
  utcDate, currentYear, getMonthFromDateStr, getDayFromDateStr, todaysSplitUtcDate, localDate, getDateElemsFromDateStr } from "./DateExtension";
import { vi } from "vitest";

describe("Utility functions relating to JS Date types", () => {
  beforeAll(() => {
    vi.useFakeTimers(); //? Use fake timers to allow the tests to set any Date they need
  });
  afterAll(() => {
    vi.useRealTimers();
  });
  //! Date
  test("gets a simple to read date string using the expected date from the API", () => {
    const emptyStringExample = getReadableDate("");
    expect(emptyStringExample).toBe("");

    //* The following are missing an "at", or have too many
    expect(getReadableDate("This will not be split properly")).toBe("");
    expect(getReadableDate("I am at the house, and the dog is at the park")).toBe("");

    //* This fails due to the date half containing the incorrect length
    const dateInvalidStr = "I am at the house";
    expect(getReadableDate(dateInvalidStr)).toBe("at the house");

    //* This fails due to the time half containing the incorrect length
    const timeInvalidStr = "I am nearly almost at the warm house";
    expect(getReadableDate(timeInvalidStr)).toBe("I am nearly almost at");

    //* Technically a valid string due to proper lengths in both halves BUT not the expected date str i.e. Thur June 09 2021 at 07:10 PM
    const validStr = "I am nearly almost at the house";
    expect(getReadableDate(validStr)).toBe("I am nearly almost at the house");

    const expectedDateStr = "Thur June 09 2021 at 07:10 PM";
    expect(getReadableDate(expectedDateStr)).toBe("Thur June 9 2021 at 7:10 PM");

    //! Very important edge case - Saturday is an issue if splitting string with "at" instead of " at "
    expect(getReadableDate("Sat June 11 2021 at 07:10 PM")).toBe("Sat June 11 2021 at 7:10 PM");
  });
  test("formats the expected date from the API", () => {
    const emptyStringExample = dateFormatter("");
    expect(emptyStringExample).toBe("");

    const shortString = "foo bar";
    expect(dateFormatter(shortString)).toBe("");
    const longStr = "foo bar fizz buzz barf";
    expect(dateFormatter(longStr)).toBe("");

    const properLengthString = "foo bar fizz buzz";
    //* Correct length so it's returned back "formatted" BUT not actually the expected date string i.e. Thur June 09 2021
    expect(dateFormatter(properLengthString)).toBe(properLengthString);

    const normalDateFormat = "Thur June 09 2021";
    expect(dateFormatter(normalDateFormat)).toBe("Thur June 9 2021");
  });
  test("extract the year, month and day from the typical dateStr", () => {
    expect(getDateElemsFromDateStr("")).toBe(""); //* Empty strings return empty strings

    //* Invalid strings due to length
    expect(getDateElemsFromDateStr("Hello")).toBe("");
    expect(getDateElemsFromDateStr("Thur June 09")).toBe("");

    //* Technically valid but not expected, returning unpredictable results
    expect(getDateElemsFromDateStr("03 June 2021 Fri")).toStrictEqual(["Fri", "June", "2021"]);
    expect(getDateElemsFromDateStr("June 03 2021 Thur 05:12 PM")).toStrictEqual(["Thur", "03", "2021"]);

    const expectedDateStr = "Thur June 09 2021 at 07:10 PM";
    expect(getDateElemsFromDateStr(expectedDateStr)).toStrictEqual(["2021", "June", "09"]);
  });
  test("extract the month from the typical dateStr", () => {
    expect(getMonthFromDateStr("")).toBe(""); //* Empty strings return empty strings

    expect(getMonthFromDateStr("Hello")).toBe(""); //* Invalid string due to length

    //* Technically valid but not expected
    expect(getMonthFromDateStr("Hello world")).toBe("world");
    expect(getMonthFromDateStr("Hello there world")).toBe("there");

    //* Half strings that would yield expected results
    expect(getMonthFromDateStr("Thur June")).toBe("June");
    expect(getMonthFromDateStr("Saturday september 05")).toBe("september");

    const expectedDateStr = "Thur June 09 2021 at 07:10 PM";
    expect(getMonthFromDateStr(expectedDateStr)).toBe("June");
  });
  test("extract the day of the month from the typical dateStr", () => {
    expect(getDayFromDateStr("")).toBe(""); //* Empty strings return empty strings

    //* Invalid string due to length
    expect(getDayFromDateStr("Hello")).toBe("");
    expect(getDayFromDateStr("Hello world")).toBe("");

    //* Technically valid but not expected
    expect(getDayFromDateStr("Hello there world")).toBe("world");

    //* Half strings that would yield expected results
    expect(getDayFromDateStr("Saturday september 31")).toBe("31");
    //! The leading 0 is not dropped yet! parseInt() is one option to drop that 0
    expect(getDayFromDateStr("Thur June 09")).toBe("09");
    expect(getDayFromDateStr("Monday November 05 2021")).toBe("05");

    const expectedDateStr = "Thur June 09 2021 at 07:10 PM";
    expect(getDayFromDateStr(expectedDateStr)).toBe("09");
  });

  //! Time
  test("gets the expected time out of the expected date returned by the API", () => {
    const emptyStringExample = getTimeFromDateStr("");
    expect(emptyStringExample).toBe("");

    //* All invalid strings due to length, so they'll return an empty string back
    expect(getTimeFromDateStr("Hello")).toBe("");
    expect(getTimeFromDateStr("Hello world")).toBe("");
    expect(getTimeFromDateStr("Hello world today!")).toBe("");

    //* Technically valid due to the split "at", getting the portion after "at"
    const validStr = "The dog is at the house";
    expect(getTimeFromDateStr(validStr)).toBe("the house");

    //* Expected date string
    const normalDateFormat = "Thur June 09 2021 at 07:10 PM";
    expect(getTimeFromDateStr(normalDateFormat)).toBe("7:10 PM");

    //! Time version also has the Saturday edge case, split() MUST use " at ", NOT "at"
    expect(getReadableDate("Sat June 11 2021 at 07:10 PM")).toBe("Sat June 11 2021 at 7:10 PM");
  });
  test("formats the expected time from the API", () => {
    const emptyStringExample = timeFormatter("");
    expect(emptyStringExample).toBe("");

    const invalidLengthStr = "foo bar fizz buzz barf";
    expect(timeFormatter(invalidLengthStr)).toBe("");

    //* Correct length so it's returned back "formatted" BUT not actually the expected date string i.e. 07:10 PM
    const properLengthStr = "foo bar";
    expect(timeFormatter(properLengthStr)).toBe("foo bar");

    const normalDateFormat = " 07:10 PM ";
    expect(timeFormatter(normalDateFormat)).toBe("7:10 PM");
  });

  //! Quick Helpers
  test("removes leading zeros in a string", () => {
    expect(removeLeadingZero("")).toBe("");

    const expectedResult = "Hello World";

    const basicExample = "0000Hello World";
    expect(removeLeadingZero(basicExample)).toBe(expectedResult);

    const normalStr = "Hello World";
    expect(removeLeadingZero(normalStr)).toBe(expectedResult);

    const trailingZeroExample = "Hello World000000000";
    const actualResult = removeLeadingZero(trailingZeroExample);
    expect(actualResult).not.toBe(expectedResult); //* The zeros will not be removed
    expect(actualResult).toBe(trailingZeroExample); //* It will remain exactly the same

    const middleZeroExample = "Hello0World";
    expect(removeLeadingZero(middleZeroExample)).toBe(middleZeroExample); //* No change

    const randomZeroExample = "0Hello00000World000";
    const randomZeroActualResult = removeLeadingZero(randomZeroExample);
    expect(randomZeroActualResult).not.toBe(randomZeroExample); //* Change has occurred
    expect(randomZeroActualResult).toBe("Hello00000World000");
  });
  //* Quick Getters
  describe("using universal time", () => {
    test("getting a simple ISO formatted string", () => {
      vi.setSystemTime(new Date(2021, 2, 27).getTime());
      vi.setSystemTime(Date.UTC(2021, 2, 27, 3, 15, 22, 123)); //? Set fake System Time with Epoch Milliseconds aka Unix Time
      const utcString = utcDate();
      expect(utcString[10]).toBe("T"); //? 10th char is always T for the start of the Hour:Minute:Second time
      expect(utcString[utcString.length - 1]).toBe("Z"); //? All UTC Strings end with Z for Zulu Time Zone

      const [date, time] = utcString.split("T");

      const [year, month, day] = date.split("-"); //? [YYYY, MM, DD]
      expect(year).toBe("2021");
      expect(month).toBe("03");
      expect(day).toBe("27");

      const [hour, minute, second] = time.slice(0, time.length - 1).split(":"); //? [HH, MM, SS.SSS]
      expect(hour).toBe("03");
      expect(minute).toBe("15");
      expect(second).toBe("22.123");
    });
    test("grabbing the current year, month and day as an array", () => {
      vi.setSystemTime(Date.UTC(2021, 2, 27, 3, 15, 22));
      const dateElements = todaysSplitUtcDate();
      expect(dateElements).toHaveLength(3); //* Should always be [YYYY, MM, DD]

      const [year, month, day] = dateElements; //* Easily destructured for use
      expect(year).toBe("2021");
      expect(month).toBe("3");
      expect(day).toBe("27");
    });
  });
  describe("using a user's local date", () => {
    test("getting a simple string in a particular format", () => {
      vi.setSystemTime(new Date(2020, 8, 7, 20, 41, 5, 321).getTime()); //? STILL set fake System Time with Unix Time
      const localString = localDate(); //? Mon Sep 07 2020 20:41:05 GMT-0700 (Pacific Daylight Time)
      expect(localString.endsWith("(Pacific Daylight Time)")).toBe(true); //TODO: May be a failing point in a CI context

      const [dayName, monthAbbrev, dayNum, yearNum, time] = localString.split(" ");
      expect(dayName).toBe("Mon");
      expect(monthAbbrev).toBe("Sep");
      expect(dayNum).toBe("07");
      expect(yearNum).toBe("2020");
      expect(time).toBe("20:41:05");
    });
    test("grabbing the year, month and day as an array", () => {
      vi.setSystemTime(new Date(2018, 9, 31).getTime());
      const dateElements = todaysSplitUtcDate();
      expect(dateElements).toHaveLength(3); //* Should always be [YYYY, MM, DD]

      const [year, month, day] = dateElements; //* Easily destructured for use
      expect(year).toBe("2018");
      expect(month).toBe("10");
      expect(day).toBe("31");
    });
    test("grabbing the year", () => {
      vi.setSystemTime(new Date(2019, 5, 2).getTime());
      const thisYear = currentYear();
      expect(thisYear).toBe("2019");
    });
  });
});