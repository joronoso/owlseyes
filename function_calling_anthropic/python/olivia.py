from anthropic import Anthropic
import sqlite3
import io
import json

save_recipe_declaration = {
    "name": "save_recipe",
    "description": "Save a new recipe",
    "input_schema": {
        "type": "object",
        "properties": {
            "name": {
                "type": "string",
                "description": "Name of the recipe.",
            },
            "ingredients": {
                "type": "string",
                "description": "List of ingredients needed to prepare the recipe, with their quantities.",
            },
            "instructions": {
                "type": "string",
                "description": "List of specific steps required to prepare the recipe, including order, cooking times, and any details that need to be specified so that a person with no prior knowledge can successfully make it.",
            },
        },
        "required": ["name", "ingredients", "instructions"],
    }
}

list_recipes_declaration = {
    "name": "list_recipes",
    "description": "List saved recipes.",
    "input_schema": {
        "type": "object",
        "properties": {}
    }
}

table_exists = False

def list_recipes():
    # Gets the list of stored recipes
    conn = sqlite3.connect("recipes.db")
    try:
        recipes = [{"name":row[0], "ingredients":row[1], "instructions":row[2]} for row in conn.execute("select name, ingredients, instructions from recipe")]
    except:
        recipes = []
    conn.close()
    return recipes

def save_recipe(name, ingredients, instructions):
    # Save a new recipe
    conn = sqlite3.connect("recipes.db")
    cur = conn.cursor()
    if not table_exists:
        cur.execute("""CREATE TABLE if not exists recipe (
                    [name] TEXT NOT NULL,
                    [ingredients] TEXT,
                    [instructions] TEXT)""")
    cur.execute("insert into recipe (name, ingredients, instructions) values (?,?,?)",
                (name, ingredients, instructions))
    conn.commit()
    cur.close()
    conn.close()

class ClaudeClient:
    def __init__(self, model, system_prompt):
        self.model = model
        self.system_prompt = system_prompt
        self.anthropic = Anthropic()
        self.messages = []

    def __call_function(self, llf):
        if llf.name == "list_recipes":
            return json.dumps(list_recipes())
        elif llf.name == "save_recipe":
            return json.dumps(save_recipe(llf.input["name"], llf.input["ingredients"], llf.input["instructions"]))


    def chat(self, user_message):
        self.messages.append(
            {
                "role": "user",
                "content": user_message
            }
        )
        response = self.anthropic.messages.create(
            max_tokens=4096,
            system=self.system_prompt,
            messages=self.messages,
            model = self.model,
            tools=[save_recipe_declaration, list_recipes_declaration]
        )
        self.messages.append(
             {
                "role": "assistant",
                "content": response.content
            }
        )
        if response.stop_reason == "tool_use":
            output = ""
            function_result = []
            for c in response.content:
                if c.type == "text":
                    output = c.text
                elif c.type == "tool_use":
                    function_result.append(
                        {
                            "type": "tool_result",
                            "tool_use_id": c.id,
                            "content": self.__call_function(c)
                        })
            self.messages.append(
                {
                    "role": "user",
                    "content": function_result
                })
            response2 = response = self.anthropic.messages.create(
                max_tokens=4096,
                system=self.system_prompt,
                messages=self.messages,
                model = self.model,
                tools=[save_recipe_declaration, list_recipes_declaration]
            )
            self.messages.append(
                {
                    "role": "assistant",
                    "content": response2.content
                }
            )
            return output+"\n"+response2.content[0].text
        
        return response.content[0].text

with io.open("olivia.md", "r") as arch:
    system_prompt = "\n".join(arch.readlines())

client = ClaudeClient("claude-3-5-sonnet-20240620", system_prompt)
while (user_text := input("What do you want to say to Olivia?\n> ").strip()) !="":
    if len(user_text)==0: 
        break
    print(client.chat(user_text))

