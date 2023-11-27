import { isDate, isEmpty, isFunction, isNumber, isObject, isString, isSymbol } from "./TypePredicates";

describe("provides type predicate utility functions", () => {
  test("to check if a value is an empty object", () => {
    //! WHEN the following values are input, THEN false is returned indicating an an object is NOT "empty"
    expect(isEmpty(true)).toBe(false);
    //* WHEN the value is a number, it is caught by the isNumber() conditional
    expect(isEmpty(1)).toBe(false);
    expect(isEmpty(1.0)).toBe(false);
    expect(isEmpty(BigInt(1))).toBe(true);
    //* WHEN the value is a function, it is caught by the isFunction() conditional
    expect(isEmpty(() => { console.log("Foobar"); })).toBe(false);
    //* WHEN the value is a Symbol object, it is caught by the isSymbol() conditional
    expect(isEmpty(Symbol())).toBe(false);
    //* WHEN the value is a Date object, it is caught by the isDate() conditional
    expect(isEmpty(new Date())).toBe(false);
    //* WHEN the value is an array or object w/ length property, it is caught by the `value instanceof Object` conditional
    expect(isEmpty([1])).toBe(false);
    expect(isEmpty({ length: 1 })).toBe(false);
    //* WHEN the value is a Map or Set, it proceeds through a "size" property check
    expect(isEmpty(new Map([["a", "1"]]))).toBe(false);
    expect(isEmpty(new Set([1,1]))).toBe(false);
    //* All other values are enumerated to check for length
    expect(isEmpty("a")).toBe(false);
    expect(isEmpty("abc def")).toBe(false);
    expect(isEmpty("0")).toBe(false);

    //! WHEN the following values are input (mostly falsy values), THEN true is returned indicating an "empty" value
    expect(isEmpty(undefined)).toBe(true);
    expect(isEmpty(null)).toBe(true);
    expect(isEmpty(false)).toBe(true); //* Not sure if false should be considered empty
    expect(isEmpty(0)).toBe(true);
    expect(isEmpty(0.0)).toBe(true);
    expect(isEmpty(BigInt(0.0))).toBe(true);
    expect(isEmpty(new Date("abc"))).toBe(true); //? Invalid dates will fail since getTime() will return NaN
    expect(isEmpty([])).toBe(true);
    expect(isEmpty({ })).toBe(true);
    expect(isEmpty({ length: 0 })).toBe(true);
    expect(isEmpty(new Map())).toBe(true);
    expect(isEmpty(new Set())).toBe(true);
    expect(isEmpty("")).toBe(true);
    expect(isEmpty(new String())).toBe(true);
    expect(isEmpty(new String(""))).toBe(true);
  });
  test("to check if a value is a date object", () => { //? An alias for `date-fns` version of isDate
    //* WHEN the normal constructor is used, THEN a date is returned and isDate() returns true
    expect(isDate(new Date())).toBe(true);
    expect(isDate(new Date(1.20))).toBe(true);
    expect(isDate(new Date(123))).toBe(true);
    expect(isDate(new Date(0,0))).toBe(true); //? 0-99 are treated as the 1900s
    expect(isDate(new Date(123,2))).toBe(true);
    expect(isDate(new Date(1910,1))).toBe(true);
    expect(isDate(new Date("abc"))).toBe(true);

    //* WHEN a date is created BUT returns a different type, THEN isDate() returns false
    expect(isDate(Date.now())).toBe(false);
    expect(isDate(Date())).toBe(false);
  });
  test("to check if a value is a function object", () => {
    expect(isFunction(() => { console.log("Foobar"); })).toBe(true);
    expect(isFunction((a: string) => { console.log(a); })).toBe(true);
    expect(isFunction(function foo() { console.log("Barfoo"); })).toBe(true);

    //* WHEN any other type is input, THEN isFunction() returns false
    expect(isFunction(undefined)).toBe(false);
    expect(isFunction(null)).toBe(false);
    expect(isFunction(true)).toBe(false);
    expect(isFunction(false)).toBe(false);
    expect(isFunction(1)).toBe(false);
    expect(isFunction(1.0)).toBe(false);
    expect(isFunction(BigInt(123))).toBe(false);
    expect(isFunction(Symbol())).toBe(false);
    expect(isFunction(new Date())).toBe(false);
    expect(isFunction({ })).toBe(false);
    expect(isFunction({ a: 1 })).toBe(false);
    expect(isFunction([1,2,3])).toBe(false);
    expect(isFunction(new Set([1, 2]))).toBe(false);
    expect(isFunction(new Map([[1, 2]]))).toBe(false);
    expect(isFunction("a")).toBe(false);
    expect(isFunction(new String(""))).toBe(false);
  });
  test("to check if a value is a number", () => {
    //* WHEN any number primitive is input, THEN isNumber() returns true
    expect(isNumber(0)).toBe(true);
    expect(isNumber(1)).toBe(true);
    expect(isNumber(123)).toBe(true);
    expect(isNumber(1.0)).toBe(true);

    //* WHEN any other type is input, THEN isNumber() returns false
    expect(isNumber(undefined)).toBe(false);
    expect(isNumber(null)).toBe(false);
    expect(isNumber(true)).toBe(false);
    expect(isNumber(false)).toBe(false);
    expect(isNumber(BigInt(123))).toBe(false); //? BigInt DOESN'T count
    expect(isNumber(() => { console.log("isNumber() check"); })).toBe(false);
    expect(isNumber(function foo() { console.log("isNumber() check"); })).toBe(false);
    expect(isNumber(Symbol())).toBe(false);
    expect(isNumber(new Date())).toBe(false);
    expect(isNumber({ })).toBe(false);
    expect(isNumber({ a: 1 })).toBe(false);
    expect(isNumber([1,2,3])).toBe(false);
    expect(isNumber(new Set([1, 2]))).toBe(false);
    expect(isNumber(new Map([[1, 2]]))).toBe(false);
    expect(isNumber("a")).toBe(false);
    expect(isNumber(new String(""))).toBe(false);
  });
  test("to check if a value is an object", () => {
    //* WHEN a normal object is input, THEN isObject() returns true
    expect(isObject({ })).toBe(true);
    expect(isObject({ a: "" })).toBe(true);
    expect(isObject({ b: 1 })).toBe(true);
    expect(isObject({ c: { d: 1.0 } })).toBe(true);

    //* WHEN any other object is input, THEN isObject() returns false
    expect(isObject(undefined)).toBe(false);
    expect(isObject(null)).toBe(false);
    expect(isObject(true)).toBe(false);
    expect(isObject(false)).toBe(false);
    expect(isObject(0)).toBe(false);
    expect(isObject(1)).toBe(false);
    expect(isObject(1.0)).toBe(false);
    expect(isObject(BigInt(1))).toBe(false);
    expect(isObject(BigInt(1.0))).toBe(false);
    expect(isObject(() => { console.log("isObject() check"); })).toBe(false);
    expect(isObject(function foo() { console.log("isObject() check"); })).toBe(false);
    expect(isObject(Symbol())).toBe(false);
    expect(isObject(new Date())).toBe(false);
    expect(isObject(Date())).toBe(false);
    expect(isObject("a")).toBe(false);
    expect(isObject(new String(""))).toBe(false);
  });
  test("to check if a value is a string", () => {
    //* WHEN any string is input, THEN isString() returns true
    expect(isString("")).toBe(true);
    expect(isString("a")).toBe(true);
    expect(isString("a b")).toBe(true);
    expect(isString("0")).toBe(true);
    expect(isString("1")).toBe(true);
    expect(isString(new String("0"))).toBe(true);
    expect(isString(new String("1"))).toBe(true);
    expect(isString(Date())).toBe(true);

    //* WHEN any other type is input, THEN isString() returns false
    expect(isString(undefined)).toBe(false);
    expect(isString(null)).toBe(false);
    expect(isString(true)).toBe(false);
    expect(isString(false)).toBe(false);
    expect(isString(0)).toBe(false);
    expect(isString(1)).toBe(false);
    expect(isString(BigInt(1.0))).toBe(false);
    expect(isString(() => { console.log("isString() check"); })).toBe(false);
    expect(isString(function foo() { console.log("isString() check"); })).toBe(false);
    expect(isString(Symbol())).toBe(false);
    expect(isString(new Date())).toBe(false);
    expect(isString({ })).toBe(false);
    expect(isString({ "a": "b" })).toBe(false);
    expect(isString(["a", "b", "c"])).toBe(false);
    expect(isString(new Set(["a", "b"]))).toBe(false);
    expect(isString(new Set("abc"))).toBe(false);
    expect(isString(new Map([["a", "b"]]))).toBe(false);
  });
  test("to check if a value is a symbol", () => {
    //* WHEN the normal constructor is used, THEN a symbol is returned and isSymbol() returns true
    expect(isSymbol(Symbol())).toBe(true);
    expect(isSymbol(Symbol(""))).toBe(true);
    expect(isSymbol(Symbol.for("foo"))).toBe(true);
    //? WHEN a symbol static property is input, THEN isSymbol returns true!
    expect(isSymbol(Symbol.hasInstance)).toBe(true);

    //* WHEN a symbol method is input, THEN isSymbol() returns false
    expect(isSymbol(Symbol.for)).toBe(false);
    //* All other type instances also return false
    expect(isSymbol(undefined)).toBe(false);
    expect(isSymbol(null)).toBe(false);
    expect(isSymbol(true)).toBe(false);
    expect(isSymbol(false)).toBe(false);
    expect(isSymbol(0)).toBe(false);
    expect(isSymbol(1)).toBe(false);
    expect(isSymbol(1.0)).toBe(false);
    expect(isSymbol(BigInt(1.0))).toBe(false);
    expect(isSymbol(() => { console.log("isSymbol() check"); })).toBe(false);
    expect(isSymbol(function foo() { console.log("isSymbol() check"); })).toBe(false);
    expect(isSymbol(new Date())).toBe(false);
    expect(isSymbol(Date())).toBe(false);
    expect(isSymbol({ })).toBe(false);
    expect(isSymbol({ a: 1 })).toBe(false);
    expect(isSymbol([1,2,3])).toBe(false);
    expect(isSymbol(new Map([["a", 1]]))).toBe(false);
    expect(isSymbol(new Set(["a", "b"]))).toBe(false);
    expect(isSymbol("a")).toBe(false);
    expect(isSymbol(new String(""))).toBe(false);
  });
});