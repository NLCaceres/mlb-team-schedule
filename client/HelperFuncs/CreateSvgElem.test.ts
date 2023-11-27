import createSvgElem, { unescapeHTML } from "./CreateSvgElem";

describe("provides helpers related to rendering HTML Strings", () => {
  test("enabling an SVG element to be created and rendered", () => {
    const svgString = "&lt;svg width=&quot;100&quot; height=&quot;100&quot;&gt;&lt;circle cx=&quot;50&quot; cy=&quot;50&quot;" +
      "r=&quot;40&quot; stroke=&quot;green&quot; stroke-width=&quot;4&quot; fill=&quot;yellow&quot; /&gt;&lt;/svg&gt;";

    const renderableSvg = createSvgElem(svgString, "50");
    //* Important change is that the dimensions have been updated to 50 each
    expect(renderableSvg).toBe("<svg width=\"50\" height=\"50\"><circle cx=\"50\" cy=\"50\" r=\"40\" " +
      "stroke=\"green\" stroke-width=\"4\" fill=\"yellow\"></circle></svg>");
    //? Small notes on changes the DomParser made: All string props use quotes ("50"), and <circle />  becomes <circle></circle>

    const divString = "&lt;div&gt; Hello world &lt;/div&gt;";
    const renderableDiv = createSvgElem(divString, "20");
    expect(renderableDiv).toBe("<div width=\"20\" height=\"20\"> Hello world </div>");

    const nonHtmlString = "Foobar";
    const renderableText = createSvgElem(nonHtmlString, "10");
    expect(renderableText).toBe(""); //* If not an html string, a blank string is returned

    const blankString = "";
    const renderableBlank = createSvgElem(blankString, "40");
    expect(renderableBlank).toBe(""); //* Similarly, blank strings get blank strings back
  });
  test("unescaping previously escaped HTML strings from the server", () => {
    //* Unescape "<", ">", and "&"
    const escapedHtml = "&lt;div&gt;Hello &amp; Goodbye&lt;/div&gt;";
    const normalHtml = unescapeHTML(escapedHtml);
    expect(normalHtml).toBe("<div>Hello & Goodbye</div>");

    //* Unescape "<", ">", the quotation mark, and the apostrophe
    const otherEscapedHtml = "&lt;div width=&quot;30&quot;&gt;Wayne&#39;s World&lt;/div&gt;";
    const otherNormalHtml = unescapeHTML(otherEscapedHtml);
    expect(otherNormalHtml).toBe("<div width=\"30\">Wayne's World</div>");

    expect(unescapeHTML("Foobar")).toBe("Foobar"); //* Return back regular strings

    expect(unescapeHTML("")).toBe(""); //* Blank strings return blank strings
  });
});