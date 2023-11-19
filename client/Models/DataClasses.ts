export default class BaseballGame {
  constructor(public id: string, public date: string,
    public homeTeam: BaseballTeam, public awayTeam: BaseballTeam,
    public promos: Promotion[], public seriesGameNumber: number, public seriesGameCount: number) { }
}

export class BaseballTeam {
  constructor(public id: string, public teamLogo: string, public teamName: string,
    public cityName: string, public abbreviation: string, public wins: number, public losses: number,
    public homeGames?: BaseballGame[], public awayGames?: BaseballGame[]) { }
}

export class Promotion {
  constructor(public id: string, public name: string,
    public thumbnailUrl: string, public baseballGame?: BaseballGame) { }
}