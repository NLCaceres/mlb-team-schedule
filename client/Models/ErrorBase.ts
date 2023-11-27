//* Define the basic structure of Errors in the client side of the project */

export default class ErrorBase<T extends string> extends Error {
  name: T; //* Describes the error AND extends `string` to leverage TS's union typing for easy narrowing via 'union discrimination'
  message: string; //* Describe the specifics of how the error occurred
  cause: unknown; //* Can be used to provide the original error to code that catches this error higher in the chain
  //? `unknown` must be narrowed to properly be handled BUT it is safer than `any` because it'll force the narrowing

  constructor({ name, message, cause }: { name: T, message: string, cause?: unknown }) {
    super();
    this.name = name;
    this.message = message;
    this.cause = cause;
  }
}