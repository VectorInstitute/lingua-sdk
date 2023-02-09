from collections import namedtuple
from functools import cached_property, partial
from getpass import getpass
import json
import requests
from pathlib import Path
import sys
import time
from typing import Dict, List, Optional
from urllib.parse import urljoin

from .hooks import TestForwardHook
from .utils import get, post

JWT_TOKEN_FILE = Path(Path.home() / '.lingua.jwt')


class Client:

    def __init__(self, gateway_host: str, gateway_port: int, auth_key: Optional[str] = None, verbose: bool = False):
        """ Initializes the Lingua client which faciliates communication with the gateway service

        :param gateway_host: The host of the gateway service
        :param gateway_port: The port of the gateway service
        :param auth_key:  The authentication key for the gateway service
        :param verbose: Print debugging information
        """

        if auth_key:
            self._session = GatewaySession(gateway_host, gateway_port, auth_key)
        else:
            self._session = GatewaySession(gateway_host, gateway_port)

            if JWT_TOKEN_FILE.exists():
                with open(JWT_TOKEN_FILE, "r") as f:
                    auth_key = f.read()
            else:
                try:
                    print("You must authenticate with your LDAP credentials to use the Lingua service")
                    auth_key = self.authenticate()
                except Exception as err:
                    print(err)
                    sys.exit(1)

            self._session.auth_key = auth_key

        self.verbose = verbose
        if self.verbose:
            print(f"Available models: {self.models} \nActive models instances: {self.model_instances}")


    def authenticate(self):
        """Authenticates this user with the gateway service via LDAP"""
        num_tries = 0
        while num_tries < 3:
            username = input("Username: ")
            password = getpass()
            result = self._session.authenticate(username, password)
            if result.status_code == 200:
                print("Login successful.")
                auth_key = json.loads(result.text)['token']
                with open(JWT_TOKEN_FILE, "w") as f:
                    f.write(auth_key)
                return auth_key
            else:
                print("Authentication failed.")
                num_tries += 1

        raise Exception("Too many failed login attempts.")

    @cached_property
    def models(self):
        return self._session.get_models()

    @property
    def model_instances(self):
        return self._session.get_model_instances()

    def load_model(self, model_name: str, wait_for_active: bool = False):
        """Loads a model from the gateway service
        
        :param model_name: (str) The name of the model to load
        :param wait_for_active: (bool) Whether to wait for the model to become active before returning
        """

        model_instance_response = self._session.create_model_instance(model_name)

        model = Model(
            model_instance_response['id'],
            model_instance_response['name'],
            self._session
        )

        if wait_for_active:
            active = False
            while not active:
                model_state = model.state
                if model_state == 'ACTIVE':
                    active = True
                elif model_state == 'FAILED':
                    raise Exception("Model failed to load")
                time.sleep(2)
        
        return model

class GatewaySession:
    """A session for a model instance"""

    def __init__(self, gateway_host: str, gateway_port: int, auth_key: Optional[str] = None):
        self.gateway_host = gateway_host
        self.gateway_port = gateway_port
        self.auth_key = auth_key

        self.base_addr = f"http://{self.gateway_host}:{self.gateway_port}/"
        self.create_addr = partial(urljoin, self.base_addr)

    def authenticate(self, username: str, password: str):
        url = self.create_addr("authenticate")
        response = requests.post(url, auth=(username, password))
        return response

    def get_models(self):
        url = self.create_addr("models")
        response = get(url)
        return response

    def get_model_instances(self):
        url = self.create_addr("models/instances")
        response = get(url)
        return response

    def create_model_instance(self, model_name: str):
        url = self.create_addr("models/instances")
        body = { "name": model_name }
        response = post(url, body, auth_key=self.auth_key)

        return response

    def get_model_instance(self, model_instance_id: str):
        url = self.create_addr(f"models/instances/{model_instance_id}")

        response = get(url, auth_key=self.auth_key)
        return response

    def get_model_instance_module_names(self, model_instance_id: str):
        url = self.create_addr(f"models/instances/{model_instance_id}/modules")

        response = get(url, auth_key=self.auth_key)
        return response

    def generate(self, model_instance_id: str, prompt: str, generation_args: Dict):
        """Generates text from the model instance"""

        url = self.create_addr(f"models/instances/{model_instance_id}/generate")
        body = {"prompt": prompt, 'generation_args': generation_args}

        response = post(url, body, auth_key=self.auth_key)

        return response

    def get_activations(self, model_instance_id: str, prompt: str, module_names: List[str]):
        """Gets activations from the model instance"""

        url = self.create_addr(f"models/instances/{model_instance_id}/activations")
        body = {"prompt": prompt, "module_names": module_names}

        response = post(url, body, auth_key=self.auth_key)

        return response


class Model():

    def __init__(self, model_instance_id: str, model_name: str, session: GatewaySession):
        """ Initializes a model instance

        :param client: (Client) Lingua client that this model belongs to
        :param model_name: (str): The name of the model
        """

        self.name = model_name
        self.id = model_instance_id
        self._session = session

    @property
    def state(self):
        return self._session.get_model_instance(self.id)['state']

    @cached_property
    def module_names(self):
        return self._session.get_model_module_names(self.id)['module_names']

    def is_active(self):
        """ Checks if the model instance is active"""
        return self.state == 'ACTIVE'

    def generate(self, prompt: str, generation_args: Dict = {}):
        """ Generates text from the model instance

        :param text: (str) The text to generate from
        :param kwargs: (dict) Additional arguments to pass to the model
        """
        generation_response = self._session.generate(self.id, prompt, generation_args)
        Generation = namedtuple('Generation', generation_response.keys())

        return Generation(**generation_response)


    def get_activations(self, prompt: str, module_names: List[str]):
        """ Gets activations from the model instance

        :param prompt: (str) The text to generate from
        :param module_names: (List[str]) The layer to get activations from
        """
        activations_response = self._session.get_activations(self.id, prompt, module_names)
        Activations = namedtuple('Activations', activations_response.keys())

        return Activations(**activations_response)

