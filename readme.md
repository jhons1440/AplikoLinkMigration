This code resolves a Firebase Dynamic Link by safely following its HTTP redirect chain and detecting loops.
It extracts metadata from query parameters embedded across redirect URLs.
It uses standard HTTP GET requests with retries, not Firebase SDKs or APIs.
The final output reconstructs the original link’s intent and sharing information for reuse or migration.
