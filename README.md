# falcon-jsonify

 [Falcon](https://github.com/falconry/falcon) middleware to serialize/deserialize JSON with built-in request validator.

This is a fork based on [Andrei Reigani's falcon-jsonify](https://github.com/AndreiRegiani/falcon-jsonify) that adds **actual** support for Python 3, and a few fixes. As for the moment, you have to clone this repository into your project or submodule it.

```shell
$ git clone https://github.com/Pisay127/falcon-jsonify.git
$ # or you can submodule this project
$ git submodule add https://github.com/Pisay127/falcon-jsonify.git
```

## Getting Started

### Registering `falcon-jsonify`
In order for your project to use `falcon-jsonify`, we must first register this middleware.

```python
import falcon_jsonify

falcon.API(middleware=[falcon_jsonify.Middleware(help_messages=True)])
```


### Responses

```python
resp.json = {"my_field": "Hello World"}
```

### Requests

```python
value = req.get_json('my_field')  # required field
```
* Response `400 Bad Request` is returned if field does not exist in the request body.
* Full deserialized dict can be accesed at `req.json` *(without validations)*, e.g. `req.json['my_field']`.


### Built-in validators

* `dtype`, `min`, `max`

```python
req.get_json('name', data_type=str, min_value=1, max_value=16)  # min/max char length
req.get_json('age', data_type=int, min_value=18, max_value=99)  # min/max numeric value
req.get_json('amount', data_type=float, min_value=0.0)
req.get_json('approved', data_type=bool)
```
* Response `400 Bad Request` is returned if a validation fails containing the error message.

### Additional parameters ###

* `default`, `match`

```python
# make a field optional with default value
req.get_json('country_code', data_type=str, default="USA", max_value=3, min_value=3)

# custom validation with Regular Expressions
req.get_json('email', match="[^@]+@[^@]+\.[^@]+")
```

### Error responses

Example:

```javascript
400 Bad Request
{
  "title": "Validation error",
  "description": "Minimum value for 'age' is '18'"
}
```

For proprietary APIs on production environment set `Middleware(help_messages=False)` to hide error messages *(missing fields, validation checks, malformed JSON)*. For public APIs may be useful to let it visible.
