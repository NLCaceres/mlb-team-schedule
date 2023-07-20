import BaseballGame from "../Models/DataClasses";
import type { Month } from "../Models/Month";
import getRequest from "./utility";

const BASE_URL = "/api";

//! GET Requests
export async function getSingleGame(monthParam: string, dayParam: string): Promise<BaseballGame | undefined> {
  //* Likely will have to update func signature to return array
  const endpoint = `${BASE_URL}/${monthParam.toLowerCase()}/${dayParam}`; //* Ex: "march/29"
  const response = await getRequest(endpoint);
  if (response === undefined) { return undefined }

  const gameOne = response[0]; //todo More adapting needed for potential double header days
  const thisGame = new BaseballGame(
    gameOne.id, gameOne.date, gameOne.homeTeam, gameOne.awayTeam, gameOne.promos, gameOne.gameNumInSeries, gameOne.gamesInSeries
  );
  return thisGame;
}

export async function getMonthsGames(monthParam: string): Promise<BaseballGame[] | undefined> {
  const response = await getRequest(`${BASE_URL}/${monthParam.toLowerCase()}`);
  if (response === undefined) { return undefined } //todo Might be best to just return an empty array and handle in view

  const monthsGames = response.map((game) => new BaseballGame(
    game.id, game.date, game.homeTeam, game.awayTeam, game.promos, game.gameNumInSeries, game.gamesInSeries
  ));
  return monthsGames;
}

export async function getFullSchedule(): Promise<BaseballGame[] | undefined> {
  const response = await getRequest(`${BASE_URL}/fullSchedule`);
  if (response === undefined) { return undefined } //todo Might be best to just return an empty array and handle in view
  
  const monthsGames = response.map((game) => new BaseballGame(
    game.id, game.date, game.homeTeam, game.awayTeam, game.promos, game.gameNumInSeries, game.gamesInSeries
  ));
  return monthsGames;
}