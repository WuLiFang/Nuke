// @ts-check

/**
 * @typedef {Object} FuncArgDoc
 * @property {string} name
 * @property {string=} default
 */
/**
 * @typedef {Object} FuncDoc
 * @property {string} name
 * @property {string} description
 * @property {FuncArgDoc[]} args
 * @property {string} returnType
 */

/**
 * @returns {FuncDoc[]}
 */
function parseFunctions() {
  const el = document.querySelector(
    'a[name="section-Functions"] + table.summary'
  );
  if (!el) {
    throw new Error("parseFunctions: table not found");
  }
  /** @type {FuncDoc[]} */
  const ret = [];
  for (const row of el.querySelectorAll(
    ":scope > tbody > tr:not(.table-header)"
  )) {
    const name = row.querySelector(".summary-sig-name").textContent;
    const description = row
      .querySelector(".summary-sig + br")
      ?.nextSibling.textContent.trim();
    /** @type {FuncArgDoc[]} */
    const args = [];
    for (const argEl of row.querySelectorAll(".summary-sig-arg")) {
      /** @type {FuncArgDoc} */
      const arg = {
        name: argEl.textContent,
      };
      const argDefaultEl = argEl.nextElementSibling;
      if (argDefaultEl?.classList.contains("summary-sig-default")) {
        arg.default = argDefaultEl.textContent;
      }
      args.push(arg);
    }
    const returnType =
      row.querySelector(".summary-type").textContent?.trim() || undefined;
    ret.push({
      name,
      description,
      args,
      returnType,
    });
  }
  return ret;
}

/**
 * @param {FuncDoc} doc
 * @returns {string}
 */
function renderFuncDocPythonTyping(doc) {
  const argsText = doc.args
    .map((i) => (i.default == null ? i.name : `${i.name}=${i.default}`))
    .join(", ");
  const returnTypeText = doc.returnType == null ? "" : ` -> ${doc.returnType}`;
  const docstring =
    doc.description == null
      ? ""
      : `
    """
    ${doc.description.replace(/\n/g, "\n    ")}
    """`;
  return `def ${doc.name}(${argsText})${returnTypeText}:${docstring}
    ...
`;
}

parseFunctions().map(renderFuncDocPythonTyping).join("\n");
