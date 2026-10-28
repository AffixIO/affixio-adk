# Google ADK example

Install the package with `pip install -e '.[google]'`, set `AFFIXIO_API_KEY` and `GOOGLE_API_KEY`, then run this directory with the Google ADK tooling. The function exposed to ADK is wrapped before registration, so an AffixIO `allow` decision is required before `lookup_order` executes.
