import { isEmpty } from "../HelperFuncs/TypePredicates";
import ErrorBase from "../Models/ErrorBase";

//* Provide basic functionality for interacting with the API */

const DEFAULT_HEADERS = { headers: { "Accept": "application/json" } };

//? Since the API doesn't wrap data sent in an object with a data key (e.g. { data: [1,2,3] })
type JsonResponse<T> = T | JsonError; //? THEN the response can only be the data itself (e.g. [1,2,3]) or a JSON error object (e.g. { error: "foobar" })
export default async function getRequest<T>(endpointURL: string) {
  const response  = await fetch(endpointURL, DEFAULT_HEADERS);
  //? `response.text()` can be a helpful alternative if json() parsing the Response's ReadableStream body were to fail
  const jsonResponse = await response.json() as JsonResponse<T> | undefined; //? Await needed! Or else, no parsing happens

  if (response.status >= 500) { throw new ApiError({ name: "SERVER_ERROR_STATUS", message: (jsonResponse as JsonError).error ?? "" }); }
  else if (response.status >= 400) { throw new ApiError({ name: "CLIENT_ERROR_STATUS", message: (jsonResponse as JsonError).error ?? "" }); }
  else if (response.status >= 300) { throw new ApiError({ name: "REDIRECT_STATUS", message: (jsonResponse as JsonError).error ?? "" }); }

  if (isJsonError(jsonResponse)) { throw new ApiError({ name: "UNEXPECTED_ERROR_RESPONSE", message: jsonResponse.error ?? "" }); }

  if (isEmpty(jsonResponse)) { return undefined; } //? Also handles falsy values like 0, undefined/null, and false

  return jsonResponse;
}


//* Typical Errors that may need to be thrown, mostly related to the status codes the API may send instead of a 200 OK Response
type ErrorNames = "CLIENT_ERROR_STATUS" | "SERVER_ERROR_STATUS" | "REDIRECT_STATUS" | "UNEXPECTED_ERROR_RESPONSE";
export class ApiError extends ErrorBase<ErrorNames> { }

//* In case the API unexpectedly returns an error code message WITHOUT an associated status code
type JsonError = { error?: string };
export function isJsonError(obj: unknown): obj is JsonError {
  return (obj as JsonError).error !== undefined;
}