import json
import logging
import asyncio
import os
import time
from flask import request, jsonify
from services.azopenai import AzureOpenAIClient
from services.aisearch import AzureAISearchClient
from services.cosmosdb import AzureCosmosDBClient
from config.config import Config


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set Azure SDK logging level to WARNING to reduce noise
azure_logger = logging.getLogger("azure.core.pipeline.policies.http_logging_policy")
azure_logger.setLevel(logging.WARNING)

class Orchestrator:
    """Class to handle chat interactions."""

    def __init__(self):
        try:
            # Set parameters configuration
            config = Config().config
            self.azurecosmos = AzureCosmosDBClient()            
            self.gpt4o_name = config["model"]["deployments"]["gpt-4o"]["name"]
            self.gpt4o_input_price = config["model"]["deployments"]["gpt-4o"]["price"]["input_tokens"]
            self.gpt4o_output_price = config["model"]["deployments"]["gpt-4o"]["price"]["output_tokens"]
            self.gpt4o_mini_name = config["model"]["deployments"]["gpt-4o-mini"]["name"]
            self.gpt4o_mini_input_price = config["model"]["deployments"]["gpt-4o-mini"]["price"]["input_tokens"]
            self.gpt4o_mini_output_price = config["model"]["deployments"]["gpt-4o-mini"]["price"]["output_tokens"]

            self.prompts_path = config["model"]["prompt"]["path"]
            self.system_prompt = config["model"]["prompt"]["system_prompt"]

            self.tools_path = config["model"]["parameters"]["tools"]["path"]
            self.tools = config["model"]["parameters"]["tools"]["file"]
            self.tool_choice = config["model"]["parameters"]["tools"]["tool_choice"]

            self.functions_path = config["model"]["parameters"]["functions"]["path"]
            self.functions = config["model"]["parameters"]["functions"]["file"]
            self.function_call = config["model"]["parameters"]["functions"]["function_call"]

            self.data_path = config["model"]["data"]["path"]
            self.data = config["model"]["data"]["file"]
            logger.info("Configuration loaded successfully.")
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            raise
    
    @staticmethod
    def read_file(file_path, as_json=False):
        """Reads content from a file."""
        try:
            with open(file_path, 'r') as file:
                logger.info(f"File '{file_path}' successfully loaded.")
                if as_json:
                    return json.load(file)
                else:
                    return file.read()
        except json.JSONDecodeError:
            logger.error(f"Error decoding JSON file: {file_path}")
            return ""
        except Exception as e:
            logger.error(f"Error reading file: {e}")
            return ""
    
    async def run(self, session_id, query):
        """Processes the chat request and returns a response."""
        try:
            start_time = time.time()
            logger.info("Starting chat response processing...")
            azurezopenai = AzureOpenAIClient()
            azureaisearch = AzureAISearchClient()

            model_gpt4o=self.gpt4o_name
            model_gpt4o_mini=self.gpt4o_mini_name

            if not query or not session_id:
                logger.error("query or session_id not provided")
                return jsonify({"error": "query or session_id not provided"}), 400

            # Load system prompt and data
            system_prompt = self.read_file(os.path.join(self.prompts_path, self.system_prompt))

            functions = self.read_file(os.path.join(self.functions_path, self.functions), as_json=True)
            function_call = self.function_call

            context_results = azureaisearch.run(query)
            if not context_results:
                raise ValueError("Empty response from Azure OpenAI")
            context = [item['content'] for item in context_results]
            logger.info(f"Context: \n{context}")
            
            user_input = {"CONTEXT": f"'''{context}'''", "QUERY": {query}}
            message_user = [{"role": "user", "content": f"'''{user_input}'''"}]
            
            messages_history = await self.azurecosmos.get_chat_history_async(session_id)

            result = azurezopenai.run(
                                model_gpt4o, 
                                system_prompt, 
                                message_user, 
                                messages_history,
                                # tools,
                                # tool_choice,
                                functions,
                                function_call
                                )
            
            if not result:
                raise ValueError("Empty result from Azure OpenAI")
            logger.info(f"Result received: {result}")

            response_data = result["response"]

            logger.info(f"Response data: \n{response_data}")

            if isinstance(response_data, dict) and "answer" in response_data:
                answer = response_data["answer"]
            else:
                answer = response_data

            execution_time = time.time() - start_time
        
            message_save = [{"role": "user", "content": query},
                            {"role": "assistant", "content": f"'''{response_data}'''"}]
            
            total_tokens_cost = ( 
                    result["input_tokens"]*self.gpt4o_input_price + 
                    result["output_tokens"]*self.gpt4o_output_price
            )
            
            evals_save = [{ 
                            "chat": {
                                    "query": query,
                                    "context": context,
                                    "answer": answer
                                },
                            "cost": {
                                "model": result["model"],
                                "input_tokens": result["input_tokens"],
                                "output_tokens": result["output_tokens"],
                                "input_tokens_price": self.gpt4o_input_price,
                                "output_tokens_price": self.gpt4o_output_price,
                                "total_tokens_cost": total_tokens_cost,
                                },
                            "time": execution_time
                        }]

            await asyncio.gather(
                self.azurecosmos.insert_items_async(
                            self.azurecosmos.container_history, 
                            session_id, 
                            message_save, 
                            "chat_history"
                ),
                self.azurecosmos.insert_evals_async(session_id, evals_save)
            )

            logger.info("Chat response processing completed successfully.")
            return jsonify({"response": answer}), 200
        except Exception as e:
            logger.error(f"Error generating model response: {e}")
            return jsonify({"error": str(e)}), 500