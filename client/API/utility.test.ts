import getRequest from "./utility";
import { vi } from "vitest";
import type { Mock } from "vitest";

const fetchMockHelp = (jsonResponse: string, statusCode: number = 200) => 
  vi.fn(() => Promise.resolve({ json: () => Promise.resolve(jsonResponse), status: statusCode })) as Mock;

describe("like a 'fetch' wrapper", () => {
  test("returns the json response", async () => {
    const fetchSpy = vi.spyOn(global, "fetch").mockImplementationOnce(fetchMockHelp("Fizz"));

    const response = await getRequest("foobar");
    expect(response).toBe("Fizz");
    expect(fetchSpy).toHaveBeenCalledWith("foobar", { headers: {"Accept": "application/json"} });
  })
  test("returns undefined if a 400+ status code or an empty response", async () => {
    const fetchSpy = vi.spyOn(global, "fetch").mockImplementationOnce(fetchMockHelp("Fizz", 400));

    const badResponse = await getRequest("foobar");
    expect(badResponse).toBe(undefined);
    expect(fetchSpy).toHaveBeenCalledWith("foobar", { headers: {"Accept": "application/json"} });

    fetchSpy.mockImplementationOnce(fetchMockHelp(""));
    const otherBadResponse = await getRequest("foobar");
    expect(otherBadResponse).toBe(undefined);
    expect(fetchSpy).toHaveBeenCalledWith("foobar", { headers: {"Accept": "application/json"} });
    expect(fetchSpy).toHaveBeenCalledTimes(2);
  })
})