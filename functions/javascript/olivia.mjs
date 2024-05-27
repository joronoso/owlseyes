import * as readline from "node:readline/promises";
import { GoogleGenerativeAI } from "@google/generative-ai";
import fs from "fs";
import Database from 'better-sqlite3';

const saveRecipeDeclaration = {
    name: "saveRecipe",
    parameters: {
        type: "OBJECT",
        description: "Save a new recipe",
        properties: {
            name: {
                type: "STRING",
                description: "Name of the recipe.",
            },
            ingredients: {
                type: "STRING",
                description: "List of ingredients needed to prepare the recipe, with their quantities.",
            },
            instructions: {
                type: "STRING",
                description: "List of specific steps required to prepare the recipe, including order, cooking times, and any details that need to be specified so that a person with no prior knowledge can successfully make it.",
            },
        },
        required: ["name", "ingredients", "instructions"],
    }
};

const listRecipesDeclaration = {
    name: "listRecipes"
}

let tableExists = false

function listRecipes() {
    let recipes, db;
    try {
        db = new Database('recipes.db');
        const stmt = db.prepare("select name, ingredients, instructions from recipe");
        recipes = stmt.all();
        tableExists = true;
    } catch {
        recipes = "There are no recipes.";
    } finally {
        db.close();
    }
    return recipes;
}

function saveRecipe(name, ingredients, instructions) {
    let result, db;
    try {
        db = new Database('recipes.db');
        if (!tableExists) {
            const stmtTabla = db.prepare(`CREATE TABLE if not exists recipe (
                [name] TEXT NOT NULL,
                [ingredients] TEXT,
                [instructions] TEXT)`);
            stmtTabla.run();
        }
        const stmtInsert = db.prepare("insert into recipe (name, ingredients, instructions) values (?,?,?)");
        stmtInsert.run(name, ingredients, instructions);
        result = "OK";
    } catch {
        result = "Error saving recipe";
    } finally {
        db.close();
    }
    return result;
}

class GeminiClient {
    constructor(model, systemPrompt) {
        this.model = model;
        const genai = new GoogleGenerativeAI(process.env.GOOGLE_API_KEY);
        let genModel = genai.getGenerativeModel(
            {
                model: model,
                safetySettings: [
                    {
                        "category": "HARM_CATEGORY_HARASSMENT",
                        "threshold": "BLOCK_NONE"
                    },
                    {
                        "category": "HARM_CATEGORY_HATE_SPEECH",
                        "threshold": "BLOCK_NONE"
                    },
                    {
                        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                        "threshold": "BLOCK_NONE"
                    },
                    {
                        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                        "threshold": "BLOCK_NONE"
                    },
                ],
                tools: {
                    functionDeclarations: [saveRecipeDeclaration, listRecipesDeclaration],
                },
            }, { apiVersion: 'v1beta', });
        this.chatSession = genModel.startChat();
        this.chatSession.sendMessage(systemPrompt); // we don't display the response, so don't need to handle the promise
    }

    async _chat(functionName, functionResponse) {
        const ret = await this.chatSession.sendMessage([{ "functionResponse": { "name": functionName, "response": { recipes: functionResponse } } }]);
        return ret.response.text();
    }

    async chat(userMessage) {
        const resp = await this.chatSession.sendMessage(userMessage);
        let modelMessage;
        if (resp.response.functionCall()) {
            const fc = resp.response.functionCall();
            console.log("-- function call: " + fc.name); // To be able to tell if function is actually being called
            if (fc.name === "listRecipes") {
                modelMessage = await this._chat(fc.name, listRecipes());
            } else if (fc.name === "saveRecipe") {
                modelMessage = await this._chat(fc.name, saveRecipe(fc.args.name, fc.args.ingredients, fc.args.instructions));
            } else {
                modelMessage = "Function call!! " + fc.name; // Should never happen
            }
        } else modelMessage = resp.response.text();
        return modelMessage;
    }
}

const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
});

let client = new GeminiClient("gemini-1.0-pro", fs.readFileSync("olivia.md", "utf8"));
let userText;
while (userText = (await rl.question('What do you want to say to Olivia?\n> ')).trim()) {
    console.log(await client.chat(userText));
}
rl.close();