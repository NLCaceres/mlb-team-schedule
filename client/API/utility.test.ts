import getRequest, { ApiError } from "./utility";
import { vi } from "vitest";
import type { Mock } from "vitest";

type errorJson = { error: string }
type invalidErrorJson = { errMsg: string }
const createMockResponse = (jsonResponse: string | errorJson | invalidErrorJson, statusCode: number = 200) => 
  vi.fn(() => Promise.resolve({ json: () => Promise.resolve(jsonResponse), status: statusCode })) as Mock;

describe("like a 'fetch' wrapper", () => {
  test("returns the json response", async () => {
    const fetchSpy = vi.spyOn(global, "fetch").mockImplementationOnce(createMockResponse("Fizz"));

    const response = await getRequest("foobar");
    expect(response).toBe("Fizz");
    expect(fetchSpy).toHaveBeenCalledWith("foobar", { headers: { "Accept": "application/json" } });
  })
  describe("an error is thrown if an unexpected status code is found", () => {
    test("like a 500-599 status code", async () => {
      const fetchSpy = vi.spyOn(global, "fetch").mockImplementationOnce(createMockResponse("Fizz", 500));

      //? To test for errors thrown in async funcs, must wrap the func in a closure AND use `rejects` to catch the promise
      await expect(() => getRequest("foobar")).rejects.toThrowError(ApiError); //? SO can test for general type matching
      expect(fetchSpy).toHaveBeenCalledWith("foobar", { headers: { "Accept": "application/json" } });

      fetchSpy.mockImplementationOnce(createMockResponse({ error: "500 Internal Server Error" }, 500));
      await expect(() => getRequest("foobar")).rejects.toThrowError("500 Internal Server Error"); //? OR to test for specific error messaging
      expect(fetchSpy).toHaveBeenCalledWith("foobar", { headers: { "Accept": "application/json" } });

      expect(fetchSpy).toHaveBeenCalledTimes(2);
    })
    test("like a 400-499 status code", async () => {
      const fetchSpy = vi.spyOn(global, "fetch").mockImplementationOnce(createMockResponse("Fizz", 400));

      //? Can also test for a very specific concrete error
      await expect(() => getRequest("foobar")).rejects.toThrowError(new ApiError({ name: "CLIENT_ERROR_STATUS", message: "" }));
      expect(fetchSpy).toHaveBeenCalledWith("foobar", { headers: { "Accept": "application/json" } });
      
      //* WHEN error json found with an error key, THEN it is used as the ApiError message
      fetchSpy.mockImplementationOnce(createMockResponse({ error: "404 Not Found" }, 404));
      await expect(() => getRequest("foobar")).rejects.toThrowError("404 Not Found");

      //* WHEN no error json is found, THEN the error message will be empty (albeit still an ApiError)
      fetchSpy.mockImplementationOnce(createMockResponse("", 400));
      await expect(() => getRequest("foobar")).rejects.toThrowError("");
      
      fetchSpy.mockImplementationOnce(createMockResponse("", 400));
      await expect(() => getRequest("foobar")).rejects.toThrowError(ApiError);

      expect(fetchSpy).toHaveBeenCalledTimes(4);
    })
    test("like a 300-399 status code", async () => {
      const fetchSpy = vi.spyOn(global, "fetch").mockImplementationOnce(createMockResponse("Fizz", 302));
      //* WHEN no error key-val pair in the errorJson is found, no message is inserted into the ApiError
      await expect(() => getRequest("foobar")).rejects.toThrowError(new ApiError({ name: "REDIRECT_STATUS", message: "" }));

      //* WHEN an unexpected error key-val pair in the errorJson is found, no message is inserted into the ApiError
      fetchSpy.mockImplementationOnce(createMockResponse({ errMsg: "301 Moved Permanently" }, 301));
      await expect(() => getRequest("foobar")).rejects.toThrowError(new ApiError({ name: "REDIRECT_STATUS", message: "" }));

      //* WHEN the CORRECT error key-val pair in the errorJson is found, its message is inserted into the ApiError
      fetchSpy.mockImplementationOnce(createMockResponse({ error: "301 Moved Permanently" }, 301));
      await expect(() => getRequest("foobar")).rejects.toThrowError("301 Moved Permanently");

      fetchSpy.mockImplementationOnce(createMockResponse({ error: "302 Found" }, 302));
      await expect(() => getRequest("foobar")).rejects.toThrowError(new ApiError({ name: "REDIRECT_STATUS", message: "302 Found" }));

      expect(fetchSpy).toHaveBeenCalledTimes(4);
    })
  })
  test("returns undefined if an empty response is found", async () => {
    const fetchSpy = vi.spyOn(global, "fetch").mockImplementationOnce(createMockResponse(""));

    const otherBadResponse = await getRequest("foobar");
    expect(otherBadResponse).toBe(undefined);
    expect(fetchSpy).toHaveBeenCalledWith("foobar", { headers: { "Accept": "application/json" } });
    expect(fetchSpy).toHaveBeenCalledTimes(1);
  })
})