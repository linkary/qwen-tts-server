/**
 * Syntax highlighting utility for JSON code blocks
 * Ported from static demo
 */

export function syntaxHighlightJSON(json: string | object): string {
  let jsonString: string;
  
  if (typeof json !== 'string') {
    jsonString = JSON.stringify(json, null, 2);
  } else {
    jsonString = json;
  }

  return jsonString.replace(
    /("(\\u[a-zA-Z0-9]{4}|\\[^u]|[^\\"])*"(\s*:)?|\b(true|false|null)\b|-?\d+(?:\.\d*)?(?:[eE][+\-]?\d+)?)/g,
    (match) => {
      let cls = 'number';
      
      if (/^"/.test(match)) {
        if (/:$/.test(match)) {
          cls = 'key';
          return `<span class="${cls}">${match.slice(0, -1)}</span>:`;
        } else {
          cls = 'string';
        }
      } else if (/true|false/.test(match)) {
        cls = 'boolean';
      } else if (/null/.test(match)) {
        cls = 'null';
      }
      
      return `<span class="${cls}">${match}</span>`;
    }
  );
}
