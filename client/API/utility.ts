import ErrorBase from "../Models/ErrorBase";

//* Provide basic functionality for interacting with the API */

const DEFAULT_HEADERS = { headers: {"Accept": "application/json"} };

export default async function getRequest(endpointURL: string) {
  const response  = await fetch(endpointURL, DEFAULT_HEADERS);
  //? `response.text()` can be a helpful alternative if json() parsing the Response's ReadableStream body were to fail
  const jsonResponse = await response.json(); //? Await needed! Or else, no parsing happens

  if (response.status >= 500) { throw new ApiError({ name: "SERVER_ERROR_STATUS", message: jsonResponse?.error ?? "" }) }
  else if (response.status >= 400) { throw new ApiError({ name: "CLIENT_ERROR_STATUS", message: jsonResponse?.error ?? "" }) }
  else if (response.status >= 300) { throw new ApiError({ name: "REDIRECT_STATUS", message: jsonResponse?.error ?? "" }) }

  if (jsonResponse.length === 0) { return undefined } //todo Could fail if Json Response is just a plain object, and not an array

  return jsonResponse;
}

//* Typical Errors that may need to be thrown, related to the status codes the API may send instead of a 200 OK Response
type ErrorNames = "CLIENT_ERROR_STATUS" | "SERVER_ERROR_STATUS" | "REDIRECT_STATUS"
export class ApiError extends ErrorBase<ErrorNames> { }