//* Define the basic structure of Errors in the client side of the project */

export default class ErrorBase<T extends string> extends Error {
  name: T; //* Describes the error AND extends `string` to leverage TS's union typing for easy narrowing via 'union discrimination'
  message: string; //* Describe the specifics of how the error occurred
  cause: any; //* Could use this to provide the original error to code that catches this error higher in the chain

  constructor({ name, message, cause }: { name: T, message: string, cause?: any }) {
    super();
    this.name = name;
    this.message = message;
    this.cause = cause;
  }
}