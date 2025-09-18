# Makefile for generating Python dataclasses from JSON schemas

# Install datamodel-code-generator if not already installed
install:
	pip install datamodel-code-generator

.PHONY: install generate-models event-model system-topics-model
		test

test:
	.venv/bin/python -m unittest discover -s tests

event-model:
	datamodel-codegen --input schemas/event.json --output dseventstream/models/event.py --input-file-type jsonschema --output-model-type dataclasses.dataclass --collapse-root-models

system-topics-model:
	datamodel-codegen --input schemas/system-topics.json --output dseventstream/models/system_topics.py --input-file-type jsonschema --output-model-type dataclasses.dataclass --collapse-root-models

generate-models:
	@echo "Regenerating models..."
	@rm -f dseventstream/models/event.py dseventstream/models/system_topics.py
	$(MAKE) event-model
	$(MAKE) system-topics-model
