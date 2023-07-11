const fs = require('fs');
const parser = require("@babel/parser");
const traverse = require("@babel/traverse").default;

const filePath = process.argv[2];
const code = fs.readFileSync(filePath, 'utf-8');

const ast = parser.parse(code, {
    sourceType: "module",
    plugins: ["jsx"],
});

const components = [];

traverse(ast, {
    FunctionDeclaration(path) {
        components.push(path.node.id.name);
    },
});

console.log(JSON.stringify(components));
