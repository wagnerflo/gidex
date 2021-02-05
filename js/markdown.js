import unified from 'unified';
import markdown from 'remark-parse';
import zwitch from 'zwitch';

import markdown_root from './markdown/root.svelte';
import markdown_heading from './markdown/heading.svelte';
import markdown_text from './markdown/text.svelte';
import markdown_paragraph from './markdown/paragraph.svelte';

function sveltify(destination, options) {
  this.Compiler = (tree) => {
    const handle = (node, component) => handler(node, component, handle);
    const bind = (component) => {
      return function(node) {
        const props = component.prototype.from_mdast(node, handle);
        return function() {
          return new component({ props });
        };
      };
    };
    const handler = zwitch('type', {
      invalid: (node) => console.log('invalid', node),
      unknown: (node) => console.log('unknown', node),
      handlers: {
        root: bind(markdown_root),
        heading: bind(markdown_heading),
        text: bind(markdown_text),
        paragraph: bind(markdown_paragraph),
      }
    });
    return handler(tree);
  };
}

export const transformer = (
  unified()
    .use(markdown)
    .use(sveltify)
);
