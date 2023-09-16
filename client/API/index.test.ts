import { getFullSchedule, getMonthsGames, getSingleGame } from ".";
import { vi } from "vitest";
import type BaseballGame from "../Models/DataClasses";
import * as Utility from "./utility";

const checkResponse = (game: BaseballGame, strVal: string, numVal: number) => {
  expect(game.id).toBe(strVal);
  expect(game.date).toBe(strVal);
  expect(game.homeTeam).toBe(strVal);
  expect(game.gameNumInSeries).toBe(numVal);
  expect(game.gamesInSeries).toBe(numVal);
}

describe("provides basic API functions", () => {
  afterEach(() => { vi.restoreAllMocks() })
  test("to grab the games of the day", async () => {
    const fetchSpy = vi.spyOn(Utility, "default").mockReturnValueOnce(Promise.resolve([{
      id: "foo", date: "foo", homeTeam: "foo", awayTeam: "foo", promos: [], gameNumInSeries: 1, gamesInSeries: 1
    }]));
    const response = await getSingleGame("march", "29");
    checkResponse(response!, "foo", 1);
    expect(fetchSpy).toHaveBeenCalledWith("/api/march/29");

    fetchSpy.mockReturnValueOnce(Promise.resolve(undefined));
    const badResponse = await getSingleGame("march", "29");
    expect(badResponse).toBe(undefined);
    expect(fetchSpy).toHaveBeenCalledTimes(2);
  })
  test("to grab the games for the month", async () => {
    const fetchSpy = vi.spyOn(Utility, "default").mockReturnValueOnce(Promise.resolve([
      { id: "foo", date: "foo", homeTeam: "foo", awayTeam: "foo", promos: [], gameNumInSeries: 1, gamesInSeries: 1 },
      { id: "bar", date: "bar", homeTeam: "bar", awayTeam: "bar", promos: [], gameNumInSeries: 2, gamesInSeries: 2 }
    ]));
    const response = await getMonthsGames("march");
    expect(response!).toHaveLength(2);
    checkResponse(response![0], "foo", 1);
    checkResponse(response![1], "bar", 2);
    expect(fetchSpy).toHaveBeenCalledWith("/api/march");

    fetchSpy.mockReturnValueOnce(Promise.resolve(undefined));
    const badResponse = await getMonthsGames("march");
    expect(badResponse).toBe(undefined);
    expect(fetchSpy).toHaveBeenCalledTimes(2);
  })
  test("to grab the full schedule of games", async () => {
    const fetchSpy = vi.spyOn(Utility, "default").mockReturnValueOnce(Promise.resolve([
      { id: "foo", date: "foo", homeTeam: "foo", awayTeam: "foo", promos: [], gameNumInSeries: 1, gamesInSeries: 1 },
      { id: "bar", date: "bar", homeTeam: "bar", awayTeam: "bar", promos: [], gameNumInSeries: 2, gamesInSeries: 2 }
    ]));
    const response = await getFullSchedule();
    expect(response).toHaveLength(2);
    checkResponse(response![0], "foo", 1);
    checkResponse(response![1], "bar", 2);
    expect(fetchSpy).toHaveBeenCalledWith("/api/fullSchedule");

    fetchSpy.mockReturnValueOnce(Promise.resolve(undefined));
    const badResponse = await getFullSchedule();
    expect(badResponse).toStrictEqual([]); //* Empty array of games returned, so view can handle unexpectedly empty response
    expect(fetchSpy).toHaveBeenCalledTimes(2);

    fetchSpy.mockReturnValueOnce(Promise.resolve([]));
    const emptyResponse = await getFullSchedule();
    expect(emptyResponse).toStrictEqual([]);
    expect(fetchSpy).toHaveBeenCalledTimes(3);
  })
})