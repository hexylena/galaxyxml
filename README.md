# Galaxy XML Generation Libraries [![Build Status](https://travis-ci.org/erasche/galaxyxml.svg?branch=master)](https://travis-ci.org/erasche/galaxyxml) [![PyPI](https://img.shields.io/pypi/v/galaxyxml.svg)](https://pypi.python.org/pypi/galaxyxml/)

These libraries will support building of Tool XML and Tool Dependencies XML.
We'd be happy to support any other XML that Galaxy supports, just make an issue
or PR if you're feeling motivated.

## Known Bugs

- no validation of unique names
- repeats aren't named properly
- conditional/whens aren't named properly
- conditionals not handled in CLI

## License

- Apache License, v2

## Changelog

- 0.4.0
	- Add feature to import existing Galaxy xml

- 0.3.3
	- [@khillion](https://github.com/khillion) implemented the following:
		- `<options>` with `<filter>` and `<column>`
		- `<container>` for `<requirements>`
		- Started to add `<tests>` section
		- `<section>` in `<inputs>`
		- `<collection>` with `<discover_datasets>` in `<outputs>`
	- Please note that `tool.parameters.OutputParam()` has been changed to `tool.parameters.OutputData()`
- 0.3.2
	- configfiles ([#8](https://github.com/erasche/galaxyxml/pull/8))
- 0.3.0
	- Travis auto-deploys on new tags
	- Testing
	- p3k
- 0.2.3
	- First widely used/stable version
