/* eslint-env node */

module.exports = {
  env: {
    browser: true,
    es2022: true
  },
  extends: [
    "eslint:recommended",
    "plugin:@typescript-eslint/strict-type-checked",
    "plugin:@typescript-eslint/stylistic-type-checked",
    "plugin:svelte/recommended"
  ],
  ignorePatterns: [
    "commands/*", "dist/*", "migrations/*", "models/*", "node_modules/*", "public/*", "templates/*", "tests/*", "utility/*", "venv/*"
  ],
  parser: "@typescript-eslint/parser",
  parserOptions: {
    sourceType: "module",
    project: true,
    tsconfigRootDir: __dirname,
    extraFileExtensions: [".svelte"]
  },
  plugins: [
    "@typescript-eslint"
  ],
  root: true,
  rules: {
    "no-trailing-spaces": "error",
    "indent": "off",
    "@typescript-eslint/indent": ["error", 2],
    "quotes": "off",
    "@typescript-eslint/quotes": "error",
    "semi": "off",
    "@typescript-eslint/semi": "error",
    "@typescript-eslint/consistent-type-definitions": ["error", "type"],
    "svelte/block-lang": ["error", { "script": ["ts"], "style": "less" }],
    "svelte/button-has-type": "error",
    "svelte/no-useless-mustaches": "error",
    "svelte/require-each-key": "error",
    "svelte/require-event-dispatcher-types": "error",
    "svelte/valid-each-key": "error",
    "svelte/first-attribute-linebreak": ["error", { multiline: "beside", singleline: "beside" }],
    "svelte/html-closing-bracket-spacing": "error",
    "svelte/html-quotes": "error",
    "svelte/html-self-closing": "error",
    "svelte/no-extra-reactive-curlies": "error",
    "svelte/no-spaces-around-equal-signs-in-attribute": "error",
    "svelte/prefer-class-directive": "error",
    "svelte/prefer-style-directive": "error",
    "svelte/shorthand-attribute": "error",
  },
  overrides: [
    {
      files: ["*.js"],
      extends: ["plugin:@typescript-eslint/disable-type-checked"]
    },
    {
      files: ["*.svelte"],
      parser: "svelte-eslint-parser",
      parserOptions: { // Parse the `<script>` in `.svelte` as TS via the following
        parser: "@typescript-eslint/parser"
      },
      "rules": {
        "indent": "off",
        "svelte/indent": "error",
        "no-trailing-spaces": "off", // Don't need ESLint's no-trailing-spaces rule, so turn it off.
        "svelte/no-trailing-spaces": ["error", { "skipBlankLines": false, "ignoreComments": false }]
      }
    },
    {
      "files": ["*test.ts"],
      "rules": {
        "@typescript-eslint/no-non-null-assertion": "off"
      }
    }
  ]
};