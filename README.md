# Galaxy XML Generation Libraries [![Build Status](https://travis-ci.org/erasche/galaxyxml.svg?branch=master)](https://travis-ci.org/erasche/galaxyxml)

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

- 0.3.1
	- configfiles ([#8](https://github.com/erasche/galaxyxml/pull/8))
- 0.3.0
	- Travis auto-deploys on new tags
	- Testing
	- p3k
- 0.2.3
	- First widely used/stable version
