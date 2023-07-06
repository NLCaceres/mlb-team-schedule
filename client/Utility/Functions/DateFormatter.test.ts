import getReadableDate, { dateFormatter, getTimeFromDateStr, timeFormatter, removeLeadingZero, utcDate, currentYear } from "./DateFormatter"

describe("Utility functions relating to JS Date types", () => {
  //! Date
  test("gets a simple to read date string using the expected date from the API", () => {
    const emptyStringExample = getReadableDate("");
    expect(emptyStringExample).toBe("");

    //* The following are missing an "at", or have too many
    expect(getReadableDate("This will not be split properly")).toBe("");
    expect(getReadableDate("I am at the house, and the dog is at the park")).toBe("")

    //* This fails due to the date half containing the incorrect length
    const dateInvalidStr = "I am at the house";
    expect(getReadableDate(dateInvalidStr)).toBe("at the house");

    //* This fails due to the time half containing the incorrect length
    const timeInvalidStr = "I am nearly almost at the warm house";
    expect(getReadableDate(timeInvalidStr)).toBe("I am nearly almost at");

    //* Technically a valid string due to proper lengths in both halves BUT not the expected date str i.e. Thur June 09 2021 at 07:10 PM
    const validStr = "I am nearly almost at the house";
    expect(getReadableDate(validStr)).toBe("I am nearly almost at the house");

    const expectedDateStr = "Thur June 09 2021 at 07:10 PM"
    expect(getReadableDate(expectedDateStr)).toBe("Thur June 9 2021 at 7:10 PM");
  })
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
  })

  //! Time
  test("gets the expected time out of the expected date returned by the API", () => {
    const emptyStringExample = getTimeFromDateStr("");
    expect(emptyStringExample).toBe("");

    //* All invalid strings due to length, so they'll return an empty string back
    expect(getTimeFromDateStr("Hello")).toBe("");
    expect(getTimeFromDateStr("Hello world")).toBe("");
    expect(getTimeFromDateStr("Hello world today!")).toBe("");

    //* Technically valid due to the split "at", getting the portion after "at"
    const validStr = "The dog is at the house"
    expect(getTimeFromDateStr(validStr)).toBe("the house");

    //* Expected date string 
    const normalDateFormat = "Thur June 09 2021 at 07:10 PM";
    expect(getTimeFromDateStr(normalDateFormat)).toBe("7:10 PM");
  })
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
  })

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
  })
  //* Quick Getters
  test("gets a simple UTC String", () => {
    const utcString = utcDate();
    expect(utcString[10]).toBe("T"); //? 10th char is always T for the start of the Hour:Minute:Second time
    expect(utcString[utcString.length - 1]).toBe("Z"); //? All UTC Strings end with Z for Zulu Time Zone
    const [date, time] = utcString.split('T');
    const [year, month, day] = date.split('-'); //? [YYYY, MM, DD]
    expect(year.length).toBe(4); expect(month.length).toBe(2); expect(day.length).toBe(2);
    const [hour, minute, second] = time.slice(0, time.length - 1).split(':'); //? [HH, MM, SS.SSS]
    expect(hour.length).toBe(2); expect(minute.length).toBe(2);
    expect(second.length).toBe(6);
  })
  test("grabs the year from a UTC string", () => {
    const thisYear = currentYear();
    expect(thisYear.length).toBe(4); //* Should always be 4 digits
    expect(thisYear.slice(0, 2)).toBe("20"); //* It'll be a while before this test fails
  })
})