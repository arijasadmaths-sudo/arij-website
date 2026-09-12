/* Build-time maths rendering; the published pages need no maths JavaScript. */
const katex = require('katex');
const fs = require('node:fs');
const values = JSON.parse(fs.readFileSync(0, 'utf8'));
const escape = s => s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
const result = {};
for (const value of values) {
  let end = 0, output = '';
  for (const m of value.matchAll(/\\\(([\s\S]*?)\\\)|\\\[([\s\S]*?)\\\]/g)) {
    output += escape(value.slice(end,m.index));
    output += katex.renderToString(m[1] ?? m[2], {output:'mathml',displayMode:m[2]!==undefined,throwOnError:true,strict:'error'});
    end=m.index+m[0].length;
  }
  result[value] = output+escape(value.slice(end));
}
process.stdout.write(JSON.stringify(result));
