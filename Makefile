SHELL = /bin/bash

BOLD=\033[1m
NORMAL=\033[0m

BANNER := $(shell echo -e "Welcome to $(BOLD)SkyPortal-Fink-Client")

$(info $())
$(info $(BANNER))
$(info $())

skyportal/Makefile:
	git submodule update --init

poll_alerts:
	@PYTHONPATH=. python3 __main__.py $(if $(config),--config $(config),)
