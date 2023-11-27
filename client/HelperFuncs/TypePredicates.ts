import { isDate as checkIfDate } from "date-fns";

//? Provide simple type guards to common BUT potentially difficult-to-assert types
//? TS Type Predicates help a ton with narrowing, especially in specific contexts to get specifically typed returns
//* Inspired by Radash and Lodash

export function isEmpty(value: unknown) { //DEBATE: BUT should `false` be treated as empty?
  //* Catch falsy values and treat them as "empty"
  if (value === undefined || value === null || value === false) { return true; }
  if (value === true) { return false; } //? Handle `true` here. Otherwise Object.keys(true) check below will return true as if empty

  //* Catch number primitives and test if they are 0
  if (isNumber(value)) { return value === 0; }

  //* THEN check for the odd/complex types like funcs
  if (isFunction(value)) { return false; }
  //* THEN check for the rare Symbol type
  if (isSymbol(value)) { return false; }

  //* THEN test against Date since it's common AND if the date is invalid, getTime() returns NaN
  if (isDate(value)) { return isNaN(value.getTime()); }

  //* Coerce the type into an object to type exclude primitives, including strings
  if (value instanceof Object) {
    //* Catch arrays by their length property, AND objects that added their own length prop, AND also `new String("foo")`
    if ("length" in value && isNumber(value.length)) { return value.length === 0; }

    //* Catch Maps & Sets since they have size properties
    if ("size" in value && isNumber(value.size)) { return value.size === 0; }
  }

  //* For all normal random Javascript objects, including strings, measure their keys
  return Object.keys(value).length === 0;
}

//? Date is kind of special since it comes up so often that it's worth type-guarding
export function isDate(value: unknown): value is Date {
  return checkIfDate(value); //? Use `date-fns` version which is similar to the following return
  // return Object.prototype.toString.call(value) === "[object Date]";
}

//? Why not a type predicate (`value is Function`)? The generic `Function` type is type unsafe in a way similar to `any`
export function isFunction(value: unknown): value is Function { // eslint-disable-line @typescript-eslint/ban-types
  //? `typeof value` WOULD work pretty well! BUT Safari 9 (2015) returns 'object' for typed arrays and constructors
  // return typeof value === "function";
  const tag = Object.prototype.toString.call(value);
  return tag == "[object Function]" || tag == "[object GeneratorFunction]" || tag == "[object AsyncFunction]" || tag == "[object Proxy]";
}
//? Alternatively could leverage `in` to check if the obj is callable (`someFunc.apply()` works similar to call())
// function isFunction(value: unknown): value is Function { // eslint-disable-line @typescript-eslint/ban-types
//   return !!(value?.constructor && value instanceof Object && ("call" in value) && ("apply" in value));
// }

export function isNumber(value: unknown): value is number {
  try { //? If the Number constructor fails to coerce the value, then there's no way the value can be any number primitive
    return Number(value) === value;
  } catch {
    return false;
  }
}

export function isObject(value: unknown): value is object {
  //? `Object` here is the initial value for all types, UNTIL they change it to something more fitting for their type
  //? Even primitives change this property, e.g. "[Function: Number] or "[Function: String]"
  return !!value && value.constructor === Object;
}

export function isString(value: unknown): value is string {
  return typeof value === "string" || value instanceof String;
}

export function isSymbol(value: unknown): value is symbol {
  return !!value && value.constructor === Symbol;
}
