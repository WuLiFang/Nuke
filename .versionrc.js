const URL = "https://github.com/WuLiFang/Nuke";

const pathLib = require("path");

/**
 * 生成工作区路径。
 * @param {string[]} parts - 路径部分
 * @returns {string} 解析后的绝对路径
 */
function workspacePath(...parts) {
  return pathLib.resolve(__dirname, ...parts);
}

/**
 * @type {import("standard-version").Options}
 * @link https://github.com/conventional-changelog/conventional-changelog-config-spec/blob/master/versions/2.1.0/README.md#compareurlformat-string
 */
module.exports = {
  types: [
    { type: "feat", section: "Features" },
    { type: "fix", section: "Bug Fixes" },
    { type: "chore", hidden: true },
    { type: "docs", hidden: true },
    { type: "style", hidden: true },
    { type: "refactor", hidden: true },
    { type: "perf", section: "Performance" },
    { type: "test", hidden: true },
  ],
  commitUrlFormat: `${URL}/commit/{{hash}}`,
  compareUrlFormat: `${URL}/compare/{{previousTag}}...{{currentTag}}`,
  issueUrlFormat: `${URL}/issues/{{id}}`,
  userUrlFormat: `https://github.com//{{user}}`,
  bumpFiles: [
    {
      filename: "lib/__version__.py",
      updater: "scripts/python-version-updater.js",
    },
    {
      filename: "wulifang/__version__.py",
      updater: "scripts/python-version-updater.js",
    },
    {
      filename: "version",
      type: "plain-text",
    },
  ],
  scripts: {
    postchangelog: `bash ${workspacePath("scripts/postchangelog.sh")}`,
  },
};
