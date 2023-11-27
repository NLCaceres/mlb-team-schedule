import getRequest, { ApiError, isJsonError } from "./utility";
import { vi, type Mock } from "vitest";

const createMockResponse = <T>(jsonResponse: T, statusCode = 200) =>
  vi.fn(() => Promise.resolve({ json: () => Promise.resolve(jsonResponse), status: statusCode })) as Mock;

describe("provides utility functions for interacting with an API", () => {
  describe("like a 'fetch' wrapper", () => {
    test("returns the json response", async () => {
      const fetchSpy = vi.spyOn(global, "fetch").mockImplementationOnce(createMockResponse("Fizz"));

      const response = await getRequest("foobar");
      expect(response).toBe("Fizz");
      expect(fetchSpy).toHaveBeenCalledWith("foobar", { headers: { "Accept": "application/json" } });
    });
    describe("an error is thrown if an unexpected status code is found", () => {
      test("like a 500-599 status code", async () => {
        const fetchSpy = vi.spyOn(global, "fetch").mockImplementationOnce(createMockResponse("Fizz", 500));

        //? To test for errors thrown in async funcs, must wrap the func in a closure AND use `rejects` to catch the promise
        await expect(() => getRequest("foobar")).rejects.toThrow(ApiError); //? SO can test for general type matching
        expect(fetchSpy).toHaveBeenCalledWith("foobar", { headers: { "Accept": "application/json" } });

        fetchSpy.mockImplementationOnce(createMockResponse({ error: "500 Internal Server Error" }, 500));
        await expect(() => getRequest("foobar")).rejects.toThrow("500 Internal Server Error"); //? OR to test for specific error messaging
        expect(fetchSpy).toHaveBeenCalledWith("foobar", { headers: { "Accept": "application/json" } });

        expect(fetchSpy).toHaveBeenCalledTimes(2);
      });
      test("like a 400-499 status code", async () => {
        const fetchSpy = vi.spyOn(global, "fetch").mockImplementationOnce(createMockResponse("Fizz", 400));

        //? Can also test for a very specific concrete error
        await expect(() => getRequest("foobar")).rejects.toThrow(new ApiError({ name: "CLIENT_ERROR_STATUS", message: "" }));
        expect(fetchSpy).toHaveBeenCalledWith("foobar", { headers: { "Accept": "application/json" } });

        //* WHEN error json found with an error key, THEN it is used as the ApiError message
        fetchSpy.mockImplementationOnce(createMockResponse({ error: "404 Not Found" }, 404));
        await expect(() => getRequest("foobar")).rejects.toThrow("404 Not Found");

        //* WHEN no error json is found, THEN the error message will be empty (albeit still an ApiError)
        fetchSpy.mockImplementationOnce(createMockResponse("", 400));
        await expect(() => getRequest("foobar")).rejects.toThrow("");

        fetchSpy.mockImplementationOnce(createMockResponse("", 400));
        await expect(() => getRequest("foobar")).rejects.toThrow(ApiError);

        expect(fetchSpy).toHaveBeenCalledTimes(4);
      });
      test("like a 300-399 status code", async () => {
        const fetchSpy = vi.spyOn(global, "fetch").mockImplementationOnce(createMockResponse("Fizz", 302));
        //* WHEN no error key-val pair in the errorJson is found, no message is inserted into the ApiError
        await expect(() => getRequest("foobar")).rejects.toThrow(new ApiError({ name: "REDIRECT_STATUS", message: "" }));

        //* WHEN an unexpected error key-val pair in the errorJson is found, no message is inserted into the ApiError
        fetchSpy.mockImplementationOnce(createMockResponse({ errMsg: "301 Moved Permanently" }, 301));
        await expect(() => getRequest("foobar")).rejects.toThrow(new ApiError({ name: "REDIRECT_STATUS", message: "" }));

        //* WHEN the CORRECT error key-val pair in the errorJson is found, its message is inserted into the ApiError
        fetchSpy.mockImplementationOnce(createMockResponse({ error: "301 Moved Permanently" }, 301));
        await expect(() => getRequest("foobar")).rejects.toThrow("301 Moved Permanently");

        fetchSpy.mockImplementationOnce(createMockResponse({ error: "302 Found" }, 302));
        await expect(() => getRequest("foobar")).rejects.toThrow(new ApiError({ name: "REDIRECT_STATUS", message: "302 Found" }));

        expect(fetchSpy).toHaveBeenCalledTimes(4);
      });
    });
    test("throwing an error if an unexpected error message is found", async () => {
      const fetchSpy = vi.spyOn(global, "fetch").mockImplementationOnce(createMockResponse({ error: "Foo" }));
      await expect(() => getRequest("foobar")).rejects.toThrow(new ApiError({ name: "UNEXPECTED_ERROR_RESPONSE", message: "Foo" }));
      expect(fetchSpy).toHaveBeenCalledTimes(1);
    });
    test("returns undefined if an empty, falsy, or unexpected error response is found", async () => {
      const fetchSpy = vi.spyOn(global, "fetch").mockImplementationOnce(createMockResponse(""));

      const emptyStrResponse = await getRequest("foobar") ;
      expect(emptyStrResponse).toBe(undefined);
      expect(fetchSpy).toHaveBeenCalledWith("foobar", { headers: { "Accept": "application/json" } });

      fetchSpy.mockImplementationOnce(createMockResponse([]));
      const emptyArrResponse = await getRequest("foobar") ;
      expect(emptyArrResponse).toBe(undefined);

      fetchSpy.mockImplementationOnce(createMockResponse({}));
      const emptyObjResponse = await getRequest("foobar") ;
      expect(emptyObjResponse).toBe(undefined);

      fetchSpy.mockImplementationOnce(createMockResponse(false));
      const falsyResponse = await getRequest("foobar") ;
      expect(falsyResponse).toBe(undefined);

      expect(fetchSpy).toHaveBeenCalledTimes(4);
    });
  });
  test("like an unexpected error type predicate", () => {
    //* WHEN an empty obj is checked, THEN it returns false
    expect(isJsonError({})).toBe(false);
    //* WHEN an empty array is checked, THEN it returns false
    expect(isJsonError([])).toBe(false);

    //* WHEN any object is found with an error key and any string value, THEN it returns true
    expect(isJsonError({ error: "Some error" })).toBe(true);
    expect(isJsonError({ error: "A", otherKey: 0 })).toBe(true);
    expect(isJsonError({ error: "" })).toBe(true);
  });
});
