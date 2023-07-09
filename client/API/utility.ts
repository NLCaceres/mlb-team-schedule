/* Provide basic functionality for interacting with the API */
const DEFAULT_HEADERS = { headers: {"Accept": "application/json"} };

export default async function getRequest(endpointURL: string) {
  const response  = await fetch(endpointURL, DEFAULT_HEADERS);
  if (response.status >= 400) { return undefined }

  const jsonResponse = await response.json(); //? Await needed! Or else, no parsing happens
  if (jsonResponse.length === 0) { return undefined }

  return jsonResponse;
}