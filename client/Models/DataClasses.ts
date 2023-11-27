//? Leverage TS types/interfaces as Class Property checkers (AND as a bonus for tests to create API mock JSON)
export type BaseballGameProps = {
  id: string, date: string,
  homeTeam: BaseballTeam, awayTeam: BaseballTeam,
  promos: Promotion[], seriesGameNumber: number, seriesGameCount: number
};
//? Implementing a TS type treats it like an interface
export default class BaseballGame implements BaseballGameProps {
  constructor(public id: string, public date: string,
    public homeTeam: BaseballTeam, public awayTeam: BaseballTeam,
    public promos: Promotion[], public seriesGameNumber: number, public seriesGameCount: number) { }

  //* Static Convenience Builder Func that replicates named args of Kotlin
  static of({ id, date, homeTeam, awayTeam, promos, seriesGameNumber, seriesGameCount }: BaseballGameProps) {
    return new BaseballGame(id, date, homeTeam, awayTeam, promos, seriesGameNumber, seriesGameCount);
  }

  //? JS can have weird behavior related to the `this` keyword where it'll unexpectedly change in the wrong context
  //? An arrow func version of below would ensure expected usage BUT every instance would get its own using WAY MORE memory
  //? TS provides `this` params to avoid the wasted memory, throwing if the context tries to change `this`
  seriesDescription(this: BaseballGame) { //? `this` param will work like Python, getting erased at compile
    const gameNumStr = (this.seriesGameNumber === 1) ? "The First Game" :
      (this.seriesGameNumber === this.seriesGameCount) ? "The Last Game" : `Game #${this.seriesGameNumber}`;
    return gameNumStr + ` in a ${this.seriesGameCount}-day Series`;
  }
}

export type BaseballTeamProps = {
  id: string, teamLogo: string, teamName: string, cityName: string, abbreviation: string,
  wins: number, losses: number, homeGames?: BaseballGameProps[], awayGames?: BaseballGameProps[]
};
export class BaseballTeam {
  constructor(public id: string, public teamLogo: string, public teamName: string,
    public cityName: string, public abbreviation: string, public wins: number, public losses: number,
    public homeGames?: BaseballGameProps[], public awayGames?: BaseballGameProps[]) { }
}

export type PromotionProps = {
  id: string, name: string, thumbnailUrl: string, baseballGame?: BaseballGameProps
};
export class Promotion implements PromotionProps {
  constructor(public id: string, public name: string,
    public thumbnailUrl: string, public baseballGame?: BaseballGameProps) { }
}