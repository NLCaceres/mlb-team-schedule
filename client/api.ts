import BaseballGame from "./Models/DataClasses";
import type { Month } from "./Models/Month";

const acceptHeader = { headers: {'Accept': 'application/json'} };

//* All Get functions
export async function getSingleGame(monthParam: string, dayParam: string): Promise<BaseballGame | undefined> {
  //* Likely will have to update func signature to return array
  const apiURL = `/api/${monthParam.toLowerCase()}/${dayParam}`
  const response = await fetch(apiURL, acceptHeader);
  const jsonResponse: BaseballGame[] = await response.json(); //? Await needed! Or else no parsing possible!
  // console.log(jsonResponse); //todo May need to consider doubleHeaders
  if (jsonResponse.length === 0) return undefined;
  const firstGame = jsonResponse[0] //* Consider future double headers
  const thisGame = new BaseballGame(firstGame.id, firstGame.date, firstGame.homeTeam, firstGame.awayTeam, 
    firstGame.promos, firstGame.gameNumInSeries, firstGame.gamesInSeries);
  return thisGame;
}

export async function getMonthsGames(monthParam: Month): Promise<BaseballGame[] | undefined> {
  const apiURL = `/api/${monthParam.monthName.toLowerCase()}`;
  const response = await fetch(apiURL, acceptHeader);
  const jsonResponse: BaseballGame[] = await response.json();
  if (jsonResponse.length === 0) return undefined;
  const monthsGames = jsonResponse.map((game) => new BaseballGame(game.id, game.date, game.homeTeam, game.awayTeam, 
    game.promos, game.gameNumInSeries, game.gamesInSeries));
  return monthsGames;
}

export async function getFullSchedule() {
  const apiURL = '/api/fullSchedule';
  const response = await fetch(apiURL, acceptHeader);
  const jsonResponse: BaseballGame[] = await response.json();
  if (jsonResponse.length === 0) return undefined;
  const monthsGames = jsonResponse.map((game) => new BaseballGame(game.id, game.date, game.homeTeam, game.awayTeam, 
    game.promos, game.gameNumInSeries, game.gamesInSeries));
  return monthsGames;
}