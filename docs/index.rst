kaleidoscope-sdk
==========

Welcome to the **kaleidoscope-sdk**!

``kaleidoscope-sdk`` is a Python module used to interact with large language models
hosted via the Kaleidoscope service (available at https://github.com/VectorInstitute/kaleidoscope).
It provides a simple interface launch LLMs on an HPC cluster, ask them to
perform basic features like text generation, but also retrieve intermediate
information from inside the model such as log probabilities and activations.
These features are exposed via a few high-level APIs, namely:

*  **model_instances** - Shows a list of all active LLMs instantiated by the model service
*  **load_model** - Loads an LLM via the model service
*  **generate** - Returns an LLM text generation based on prompt input
*  **module_names** - Returns all modules names in the LLM neural network
*  **get_activations** - Retrieves all activations for a set of modules

.. toctree::
   :maxdepth: 2
   :caption: Contents

   getting_started
   api
   configuration

Contributing
------------
Contributing to kaleidoscope is welcomed. See `Contributing <https://github.com/VectorInstitute/kaleidoscope-sdk/blob/main/doc/CONTRIBUTING.md>`_ for
guidelines.

License
-------

``kaleidoscope-sdk`` is disributed under the MIT license. See `LICENSE <https://github.com/VectorInstitute/kaleidoscope-sdk/blob/main/doc/LICENSE>`_

Citation
--------
Reference to cite when you use Kaleidoscope in a project or a research paper:

::

   Sivaloganathan, J., Coatsworth, M., Willes, J., Choi, M., & Shen, G. (2022). Kaleidoscope. http://VectorInstitute.github.io/kaleidoscope. computer software, Vector Institute for Artificial Intelligence. Retrieved from https://github.com/VectorInstitute/kaleidoscope-sdk.git.
