export function lodashUnescape(string) {
  const htmlUnescapes = { '&amp;': '&', '&lt;': '<', '&gt;': '>', '&quot;': '"', '&#39;': "'" };

  /** Used to match HTML entities and HTML characters. */
  const reEscapedHtml = /&(?:amp|lt|gt|quot|#(0+)?39);/g
  const reHasEscapedHtml = RegExp(reEscapedHtml.source)

  return (string && reHasEscapedHtml.test(string))
    ? string.replace(reEscapedHtml, (entity) => (htmlUnescapes[entity] || "'"))
    : (string || '')
}