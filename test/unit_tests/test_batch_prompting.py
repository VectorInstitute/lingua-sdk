import pytest
import lingua


class TestBatchPrompting:

    _host = "llm.cluster.local"
    _port = 4001
    model_name = "OPT-175B"  # "OPT-6.7B"
    _client = lingua.Client(gateway_host=_host, gateway_port=_port)
    _model = _client.load_model(model_name)
    _requested_activation = ["decoder.layers.30.fc1"]

    def test_generation_single_prompt_str(self):
        prompt = "What is this"
        response = self._model.generate(prompt)
        assert isinstance(
            response.generation["text"], list
        ), f'Expected type list, found {type(response.generation["text"])}'
        assert (
            len(response.generation["text"]) == 1
        ), f'Expected 1 generation, found {len(response.generation["text"])}'

    def test_generation_single_prompt_list(self):
        prompt = ["What is this"]
        response = self._model.generate(prompt)
        assert isinstance(
            response.generation["text"], list
        ), f'Expected type list, found {type(response.generation["text"])}'
        assert (
            len(response.generation["text"]) == 1
        ), f'Expected 1 generation, found {len(response.generation["text"])}'

    def test_generation_multiple_prompts(self):
        prompts = ["What is this", "Who is that", "When should we"]
        response = self._model.generate(prompts)
        assert isinstance(
            response.generation["text"], list
        ), f'Expected type list, found {type(response.generation["text"])}'
        assert len(response.generation["text"]) == len(
            prompts
        ), f"Length mismatch between # input prompts and # output generations"

    def test_activation_single_prompt_str(self):
        prompt = "What is this"
        response = self._model.get_activations(prompt, self._requested_activation)
        assert isinstance(
            response.activations, list
        ), f"Expected type list, found {type(response.activations)}"
        assert (
            len(response.activations) == 1
        ), f"Expected 1 set of activations, found {len(response.activations)}"

    def test_activation_single_prompt_list(self):
        prompt = ["What is this"]
        response = self._model.get_activations(prompt, self._requested_activation)
        assert isinstance(
            response.activations, list
        ), f"Expected type list, found {type(response.activations)}"
        assert (
            len(response.activations) == 1
        ), f"Expected 1 set of activations, found {len(response.activations)}"

    def test_activation_multiple_prompts(self):
        prompts = ["What is this", "Who is that", "When should we"]
        response = self._model.get_activations(prompts, self._requested_activation)
        assert isinstance(
            response.activations, list
        ), f"Expected type list, found {type(response.activations)}"
        assert len(response.activations) == len(
            prompts
        ), f"Length mismatch between # input prompts and # output set of activations"
