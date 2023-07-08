import DOMPurify from "dompurify";

export default function createSvgElem(logoSvgStr: string, dimensions: string) {
  const normalHtml = unescapeHTML(logoSvgStr);
  const sanitizedHtml = DOMPurify.sanitize(normalHtml); //* DOMPurify removes XSS concerns
  //* DomParser creates a htmlDoc, avoiding XSS issues by not running them in the process
  var sanitizedDoc = new DOMParser().parseFromString(sanitizedHtml, "text/html"); 

  const svgTag = sanitizedDoc.body.firstElementChild; //* Grab the SVG Tag from the logoStr
  svgTag?.setAttribute("height", dimensions); //* A single "dimensions" prop works since 
  svgTag?.setAttribute("width", dimensions); //* The logo is most likely square

  //* Should grab the SVG Tag and convert its whole HTML into a string via ".outerHtml", or coalesce to an empty string
  return DOMPurify.sanitize(sanitizedDoc.body.firstElementChild?.outerHTML ?? ""); //* Insurance sanitize!
}

export function unescapeHTML(htmlStr: string) {
  const htmlEscapeMap = { //? Escaped to Unescaped
    '&amp;': '&', //? Ampersand
    '&lt;': '<', //? Opening angle bracket
    '&gt;': '>', //? Closing angle bracket
    '&quot;': '"', //? Quotation mark
    '&#39;': "'" //? Apostrophe
  };

  //* Test if htmlStr matches any of these escaped HTML patterns
  const escapedHtmlRegex = /&(?:amp|lt|gt|quot|#(0+)?39);/g

  return (htmlStr && escapedHtmlRegex.test(htmlStr))
    ? htmlStr.replace(escapedHtmlRegex, (matchingSubstr) => htmlEscapeMap[matchingSubstr])
    : htmlStr
}