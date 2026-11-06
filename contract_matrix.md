

|Method / Path|Case|Expected|Actual|Result|
|-|-|-:|-:|-|
|GET /health|normal|200|200|pass|
|GET /documents|normal|200|200|pass|
|POST /documents|valid|201|201|pass|
|POST /documents|invalid|422|422|pass|
|GET /documents/999999|missing|404|404|pass|
|POST /documents/upload|unsupported type|400|400|pass|
|POST /documents/{id}/analyze|existing|200|200|pass|
|POST /documents/{id}/analyze|missing|404|404|pass|
|POST /agent/ask|document request|200|200|pass|



