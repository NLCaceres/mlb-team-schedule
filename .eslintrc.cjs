/* eslint-env node */

module.exports = {
  env: {
    browser: true,
    es2022: true
  },
  extends: [
    "eslint:recommended",
    "plugin:@typescript-eslint/strict-type-checked",
    "plugin:@typescript-eslint/stylistic-type-checked"
  ],
  ignorePatterns: [
    "commands/*", "dist/*", "migrations/*", "models/*", "node_modules/*", "public/*", "templates/*", "tests/*", "utility/*", "venv/*"
  ],
  parser: "@typescript-eslint/parser",
  parserOptions: {
    sourceType: "module",
    project: true,
    tsconfigRootDir: __dirname
  },
  plugins: [
    "@typescript-eslint"
  ],
  root: true,
  overrides: [
    {
      files: ["*.js"],
      extends: ["plugin:@typescript-eslint/disable-type-checked"]
    }
  ]
};