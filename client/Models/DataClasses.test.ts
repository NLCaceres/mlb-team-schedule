import BaseballGame, { Promotion } from "./DataClasses";

describe("forms the main models of the app like", () => {
  describe("a BaseballGame", () => {
    test("with an optional static builder", () => {
      const id = "1";
      const date = "";
      const homeTeam = { id: "1", teamLogo: "", teamName: "foo", cityName: "fizz", abbreviation: "", wins: 1, losses: 0 };
      const awayTeam = { id: "1", teamLogo: "", teamName: "bar", cityName: "buzz", abbreviation: "", wins: 0, losses: 1 };
      const promos: Promotion[] = [];
      const seriesGameNumber = 1;
      const seriesGameCount = 2;

      const normalGame = new BaseballGame(id, date, homeTeam, awayTeam, promos, seriesGameNumber, seriesGameCount);
      const builderGame = BaseballGame.of({ id, date, homeTeam, awayTeam, promos, seriesGameNumber, seriesGameCount });

      //* WHEN using the builder, THEN it should completely match usage of the constructor
      expect(builderGame.id).toBe(normalGame.id);
      expect(builderGame.date).toBe(normalGame.date);
      expect(builderGame.homeTeam).toBe(normalGame.homeTeam);
      expect(builderGame.awayTeam).toBe(normalGame.awayTeam);
      expect(builderGame.promos).toStrictEqual(normalGame.promos);
      expect(builderGame.seriesGameNumber).toBe(normalGame.seriesGameNumber);
      expect(builderGame.seriesGameCount).toBe(normalGame.seriesGameCount);

      //* WHEN using the builder, THEN all values should be set to the values set in the build object
      expect(builderGame.id).toBe("1");
      expect(builderGame.date).toBe("");
      expect(builderGame.homeTeam).toBe(homeTeam);
      expect(builderGame.awayTeam).toBe(awayTeam);
      expect(builderGame.promos).toStrictEqual([]);
      expect(builderGame.seriesGameNumber).toBe(1);
      expect(builderGame.seriesGameCount).toBe(2);
    });
    test("with a series description method", () => {
      const homeTeam = { id: "1", teamLogo: "", teamName: "foo", cityName: "fizz", abbreviation: "", wins: 1, losses: 0 };
      const awayTeam = { id: "1", teamLogo: "", teamName: "bar", cityName: "buzz", abbreviation: "", wins: 0, losses: 1 };
      const game = BaseballGame.of({ id: "1", date: "", homeTeam, awayTeam, promos: [], seriesGameNumber: 1, seriesGameCount: 2 });

      //* WHEN the seriesGameNumber == 1, THEN the series description should start with "The First Game"
      expect(game.seriesDescription()).toContain("The First Game");
      //* WHEN the seriesGameCount == 2, THEN the series description should end with "2-day Series"
      expect(game.seriesDescription()).toContain("in a 2-day Series");

      game.seriesGameNumber = 2;
      //* WHEN the seriesGameNumber == seriesGameCount (BOTH 2 here), THEN the series description should start with "The Last Game"
      expect(game.seriesDescription()).toContain("The Last Game");
      expect(game.seriesDescription()).toContain("in a 2-day Series");

      game.seriesGameCount = 3;
      //* WHEN the seriesGameNumber == 2 BUT is not the last game, THEN the series description should use that number 2
      expect(game.seriesDescription()).toContain("Game #2");
      //* WHEN the seriesGameCount == 3, THEN the series description should end with "3-day Series"
      expect(game.seriesDescription()).toContain("in a 3-day Series");

      game.seriesGameNumber = 3;
      //* WHEN the seriesGameNumber == seriesGameCount (BOTH 3 here), THEN the series description should start with "The Last Game"
      expect(game.seriesDescription()).toContain("The Last Game");
      expect(game.seriesDescription()).toContain("in a 3-day Series");

      game.seriesGameCount = 4;
      //* WHEN the seriesGameNumber == 3 BUT is not the last game, THEN the series description should use that number 3
      expect(game.seriesDescription()).toContain("Game #3");
      //* WHEN the seriesGameCount == 4, THEN the series description should end with "4-day Series"
      expect(game.seriesDescription()).toContain("in a 4-day Series");

      game.seriesGameNumber = 4;
      //* WHEN the seriesGameNumber == seriesGameCount (BOTH 4 here), THEN the series description should start with "The Last Game"
      expect(game.seriesDescription()).toContain("The Last Game");
      expect(game.seriesDescription()).toContain("in a 4-day Series");
    });
  });
});