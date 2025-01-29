import os.path
import sys
import requests
import json
import subprocess
import uuid
from rich.console import Console
from rich.markdown import Markdown
from typing import Iterator
from datetime import datetime, timedelta


class JarvisCompanion:
    """
    An AI for the terminal based on the LLM that's loaded in LM Studio

    Works with every LLM that is installed and loaded in LM Studio

    Runs on the default IP:PORT by LM Studio (localhost:1234) can be changed from `jarvis_config.json`
    """

    def __init__(self, verbose, save_chat=False, context=None):
        """
        :param verbose: Should output in verbose mode
        :param save_chat: Whether to save the chat
        :param context:  history to provide to LLM as context
        """
        self.verbose = verbose
        self.save_chat = save_chat
        self.context = context
        self.__CONSOLE = Console()

        config = f'{self.__get_cur_file_dir()}\\jarvis_config.json'
        if os.path.isfile(config):
            with open(config) as jarvis_config:
                self.data = json.loads(jarvis_config.read())
                self.api = self.data['api']
                self.model = self.data['model']
                self.last_health_check = self.data['last_health_check']

                if self.last_health_check == "":
                    self.last_health_check = datetime.now().isoformat()

                self.skip_health_check = self.__is_health_check_old(datetime.fromisoformat(self.last_health_check))
                if not self.skip_health_check:
                    self.__update_health_check()

        else:
            raise FileNotFoundError("jarvis_config.json not find, could not load LLM configuration")

    @staticmethod
    def __get_cur_file_dir():
        # sys.argv[0] is the path of the script
        path = sys.argv[0]
        strip_file_name = path.split('\\')[:-1] or path.split('/')[:-1]
        return "\\".join(strip_file_name)

    @staticmethod
    def __render_with_mdv(buffer) -> None:
        # This uses mdv to render the markdown buffer in the terminal
        result = subprocess.run(['mdv', '-'], input=buffer, text=True, capture_output=True)
        print(result.stdout)

    @staticmethod
    def __is_health_check_old(last_health_check) -> bool:
        """
        Check if the last online status check of LM Studio and LLM load is old enough

        The status will update every 5 minutes
        :return: True if the last health check is old, False otherwise
        """
        current_time = datetime.now()
        time = current_time - timedelta(minutes=10)
        return time <= last_health_check

    def __update_health_check(self) -> None:
        current_time = datetime.now().isoformat()
        self.data['last_health_check'] = current_time
        with open('jarvis_config.json', 'w') as file:
            file.write(json.dumps(self.data, indent=4))

    def is_llm_online(self, log=True) -> bool:
        """
        Check status load of LLM and LM Studio Server status
        :param log: Whether to log (print to stdout) the status
        :return: True in case of up and running services, false otherwise
        """
        if not self.skip_health_check:
            try:
                r = requests.get(self.api['models'])
                if r.status_code == 200:
                    if len(r.json()['data']) >= 1:
                        if log:
                            print("[+] Server is up and LLM is loaded")
                        return True
                    elif log:
                        print("[-] LLM is not loaded")
            except requests.exceptions.ConnectionError:
                print("[-] Server is down")
            return False
        else:
            return True

    @property
    def get_all_chats(self) -> list:
        return [chat[:-4] for chat in os.listdir("./conversations")]


    def __get_context(self) -> str | None:
        if self.context:
            with open(f"./conversations/{self.context}.txt") as chat:
                return chat.read()
        return None

    def __save_context(self, chat) -> None:
        """Save content to the context file"""
        mode = 'a' if self.context in self.get_all_chats else 'w'
        with open(f"./conversations/{self.context}.txt", mode) as file:
            file.write(chat)

    def llm_generate(self, prompt) -> Iterator:
        """
        Send a request with :param prompt to LM Studio API and returns the response back
        :param prompt: Your input to Jarvis
        :return: An iterator with the response object
        """

        history = ""

        if self.verbose:
            print("[+] Starting up...\n")

        if not self.context:
            self.context = str(uuid.uuid4())
        # Check if chat has a history
        elif self.context in self.get_all_chats:
            history = self.__get_context()

        payload = {
            "model": self.model['name'],
            "messages": [
                {"role": "system", "content": self.model['behavior']},
                {"role": "user", "content": f"{history}\n{prompt}"}
            ],
            "temperature": self.model['temperature'],
            "max_tokens": self.model['max_tokens'],
            "stream": self.model['stream']
        }

        headers = {"Content-Type": "application/json"}
        response = requests.post(self.api['completion'], headers=headers, data=json.dumps(payload), stream=True)

        if payload['stream']:
            return response.iter_content(chunk_size=1024 * 1024)

        return response.json()

    def stream_llm_response(self, response, render_markdown=True) -> None:
        """
        Streams from LLM's response to stdout
        :param response: The generated LLM response
        :param render_markdown: Whether to stream as plain text or rendered markdown
        :return: None (the response is outputted to the stdout)
        """

        # json response from llm (stream set to False)
        if type(response) == dict:
            if (content := response['choices'][0]['message']['content']) != "":
                if not render_markdown:
                    print(content, end='', flush=True)
                else:
                    self.__render_with_mdv(content)
            return

        buffer = ""  # Initialize a buffer to accumulate Markdown content
        save_buffer = ""  # Buffer for saving to file

        for chunk in response:
            if chunk:
                try:
                    # Decode and load JSON, removing 'data: ' prefix
                    decoded_chunk = chunk.decode('utf-8')[6:]
                    data = json.loads(decoded_chunk.strip())['choices'][0]

                    # Append new content to the buffer
                    if data['delta']:
                        current_response = data['delta']['content']
                        save_buffer += current_response

                        if not render_markdown:
                            print(current_response, end='', flush=True)
                        else:
                            buffer += current_response

                    # Save accumulated content when we have a reasonable chunk
                    if self.save_chat and len(save_buffer) >= 100:
                        self.__save_context(save_buffer)
                        save_buffer = ""  # Clear save buffer after writing

                    if render_markdown:
                        # Render only when buffer contains two consecutive line breaks
                        if "\n\n" in buffer:
                            self.__CONSOLE.print(Markdown(buffer), soft_wrap=True)  # Render Markdown content
                            buffer = ""  # Clear the buffer after printing

                except json.JSONDecodeError:
                    continue

        # Handle any remaining content in buffers
        if save_buffer and self.save_chat:
            self.__save_context(save_buffer + "\n")

        # Render any remaining content in the buffer
        if buffer and render_markdown:
            self.__render_with_mdv(buffer.strip())
