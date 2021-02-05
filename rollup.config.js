import babel from '@rollup/plugin-babel';
import commonjs from '@rollup/plugin-commonjs';
import consts from 'rollup-plugin-consts';
import css from 'rollup-plugin-css-only';
import resolve from '@rollup/plugin-node-resolve';
import { readFileSync } from 'fs';
import svelte from 'rollup-plugin-svelte';
import sveltePreprocess from 'svelte-preprocess';
import { terser } from 'rollup-plugin-terser';

const CONSTS = JSON.parse(readFileSync('gidex/consts.json'));

export default {
  input: 'js/ui.js',
  output: [
    {
      format: 'iife',
      name: 'app',
      file: `gidex/assets/${CONSTS.SCRIPT_NAME}`,
    },
    // when not in watch mode also build minified
    !process.env.ROLLUP_WATCH && {
      sourcemap: true,
      format: 'iife',
      name: 'app',
      file: `gidex/assets/${CONSTS.SCRIPT_NAME_MIN}`,
      plugins: [
        terser(),
      ]
    },
  ],
  plugins: [
    // load constants from file
    consts({
      ...CONSTS,
    }),

    // run babel and svelte
    babel({
      babelHelpers: 'bundled',
    }),
    svelte({
      preprocess: sveltePreprocess({
        scss: {
          includePaths: ['theme'],
        }
      })
    }),

    // split of css into file
    css({
      output: CONSTS.CSS_NAME,
    }),

    // not sure what this does
    resolve({
      browser: true,
      dedupe: ['svelte']
    }),
    commonjs(),
  ],
};
