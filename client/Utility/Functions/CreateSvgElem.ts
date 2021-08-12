import DOMPurify from "dompurify";
import { lodashUnescape } from "./Lodash";

export default function createSvgElem(logoSvgStr: string, dimensions: string) {
  //* DomParser is not perfect but it's a start toward avoiding XSS concerns by not allowing them to run while DOM manipulating
  //* DOMPurify, on the other hand, will handle do the removing
  var sanitizedDoc = new DOMParser().parseFromString(DOMPurify.sanitize(lodashUnescape(logoSvgStr)), "text/html"); 
  const svgTag = sanitizedDoc.body.firstElementChild; 
  //* Since img can be square, a single 'dimensions' var may work for both height/width below
  svgTag?.setAttribute('height', dimensions); svgTag?.setAttribute('width', dimensions);
  return DOMPurify.sanitize(sanitizedDoc.body.firstElementChild); //* Insurance sanitize!
}