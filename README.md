# Tangerine-Auth

Tangerine-Auth is a Python library that provides utilities for user authentication and secure handling of keys and encrypted data. It uses bcrypt for password hashing and JWT for token-based authentication.

## Installation

NOTE: Tangerine-Auth is currently in beta. It is not recommended for production use quite yet. Please feel free to download and play around with it in the meantime!  We are working on adding more tests and documentation. If you find any bugs or have any suggestions, please open an issue on GitHub.

Use pip to install the package:

```sh
pip install tangerine-auth
```

## Usage

### Yuzu

The general steps to integrating Yuzu into your application are as follows:

1. Define two functions for creating a user in your database, and another for finding a user in your database. These functions should take a dictionary of user data as an argument and return a dictionary of user data. The user data dictionary should contain at least an email and password field. The user data dictionary can contain any other fields you want to store in your database. Here is an example:

```python
def get_user_by_email(email):
    conn = psycopg2.connect("postgresql://postgres:<your postgres password>@localhost:5432/local_development")
    cur = conn.cursor()
    cur.execute("SELECT * FROM tangerine.users WHERE email = %s", (email,))
    user = cur.fetchone()
    cur.close()
    conn.close()

    if user:
        return {'_id': user[0], 'email': user[1], 'password': user[2]}
    else:
        return None

def create_user(user_data):
    conn = psycopg2.connect("postgresql://<your postgres password>@localhost:5432/local_development")
    cur = conn.cursor()
    cur.execute("INSERT INTO tangerine.users (email, password) VALUES (%s, %s) RETURNING id", (user_data['email'], user_data['password']))
    user_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return {'_id': user_id, 'email': user_data['email'], 'password': user_data['password']}
```

2. Create a KeyLime object and pass it to the Yuzu constructor. The KeyLime object is used for securely handling keys and encrypted data. You can use the KeyLime object to encrypt and decrypt data, and to store and retrieve keys.

3. Create a Yuzu object and pass it the KeyLime object, the function for finding a user in your database, and the function for creating a user in your database.

4. (optional) Yuzu uses bcrypt to hash passwords. You can optionally pass a custom hash function to the Yuzu constructor. The custom hash function should take a password string as an argument and return a hashed password string.

5. After step 3 is complete, you can now use the Yuzu object to sign up a new user, log in a user, log out a user, and verify authentication tokens.

6. Yuzu was built to work with flask as well as tangerine, there are currently two JWT middlewares bundled with Yuzu, one for flask and one for tangerine. Once you have initialized the Yuzu class properly, you can use the Tangerine middleware by calling:

```python
app.use(auth.jwt_middleware).
```

The Flask version JWT middleware is still experimental and, could be issue-prone.
It will not be recommended for production use until it has been tested more thoroughly.
The JWT middleware works a bit different in Flask, To use it with Flask, you use it as a decorator:

```python
from flask import Flask
from yuzu import Yuzu

app = Flask(__name__)
def get_user_by_email(email):
    # Logic to create user in DB
    pass

def create_user(user_data):
    # Logic to create user in DB
    pass

auth = Yuzu(keychain, get_user_by_email, create_user)  # Fill with your functions

@app.route('/secure_route')
@auth.flask_jwt_middleware(auth)
def secure_route():
    # Your secure code here. This will only run if the JWT is valid.
    return "This is a secure route"

if __name__ == "__main__":
    app.run(debug=True)

```


NOTE: The auth middleware appends the user data to the Ctx object. You can access the user data in your route handler by calling

```python
ctx.auth.user or ctx.get("user")
```

Yuzu is a class that provides user authentication functionalities. It uses bcrypt for password hashing and JWT for creating and verifying authentication tokens.

Below are the key methods of the Yuzu class:

```python
- `__init__(self, keychain, get_user_by_email, create_user, hash_func: Optional[Callable] = None)`: Initializes the Yuzu object.
- `get_config(self, key_name: str) -> str`: Fetches the configuration value for a given key.
- `authenticate(self, email: str, password: str) -> bool`: Checks if the given email and password are valid.
- `generate_auth_token(self, user_id: str, email: str) -> str`: Generates an authentication token for the given user.
- `verify_auth_token(self, token: str) -> dict`: Verifies if the given authentication token is valid.
- `sign_up(self, user_data: dict) -> dict`: Signs up a new user with the given user data.
- `login(self, email: str, password: str) -> Tuple[str, str]`: Logs in a user with the given email and password.
- `logout(self)`: Logs out the current user.
- `jwt_middleware()`: Tangerine middleware for JWT authentication.
- `flask_jwt_middleware(yuzu_instance)`: Flask middleware for JWT authentication.
```


### KeyLime

KeyLime is a class that provides functionalities for securely handling keys and encrypted data.

Below are the key methods of the KeyLime class:

```python
- `__init__(self, keychain: Dict[str, bytes] = {})`: Initializes the KeyLime object.
- `add_key(self, key_name: str, key: bytes)`: Adds a key to the keychain.
- `remove_key(self, key_name: str)`: Removes a key from the keychain.
- `get_key(self, key_name: str) -> bytes`: Fetches a key from the keychain.
- `encrypt(self, key_name: str, message: str) -> str`: Encrypts a given message using a key from the keychain.
- `decrypt(self, key_name: str, cipher_text: str) -> str`: Decrypts a given cipher text using a key from the keychain.
```

The general conept for this is that you want to write two functions, one for finding
a user in your chosen database system, and one for creating a user in your chosen
database system. These functions should take a dictionary of user data as an argument
and return a dictionary of user data. The user data dictionary should contain at least
an email and password field. The user data dictionary can contain any other fields
you want to store in your database.

Here is an example of how to use the Yuzu and KeyLime classes:

```python
from tangerine import Tangerine, Ctx, Router
from pymongo import MongoClient
from tangerine.key_lime import KeyLime
from tangerine.yuzu import Yuzu
import json
import jwt
import hashlib

app = Tangerine(debug_level=1)
client = MongoClient('mongodb://localhost:27017/')
keychain = KeyLime({
        "SECRET_KEY": "ILOVECATS",
})


def get_user_by_email(email):
    db = client['mydatabase']
    users = db['users']
    query = {'email': email}
    user = users.find_one(query)
    if user:
        user['_id'] = str(user['_id'])  # Convert ObjectId to string
    return user

def create_user(user_data):
    db = client['mydatabase']
    users = db['users']
    result = users.insert_one(user_data)
    if result.inserted_id:
        user_data['_id'] = str(result.inserted_id)  # Convert ObjectId to string
    return user_data

auth = Yuzu(keychain, get_user_by_email, create_user)

# serve static files to any request not starting with /api
app.static('^/(?!api).*$', './public')

# This is how you define a custom middleware.
def hello_middle(ctx: Ctx, next) -> None:
    ctx.hello_message = json.dumps({"message": "Hello from middleware!"})
    next()
# ==================== AUTH HANDLERS ====================
def api_hello_world(ctx: Ctx) -> None:
    ctx.body = ctx.hello_message
    ctx.send(200, content_type='application/json')

def signup(ctx: Ctx) -> None:
    user_data = ctx.request.body
    created_user = auth.sign_up(user_data)
    if created_user:
        ctx.body = json.dumps(created_user)
        ctx.send(201, content_type='application/json')
    else:
        ctx.send(500, content_type='application/json')

def login(ctx: Ctx) -> None:
    user_data = ctx.request.body
    email = user_data['email']
    password = user_data['password']
    user_id, token = auth.login(email, password)
    print(ctx.user, "HELLO FROM LOGIN")

    if token:
        ctx.body = json.dumps({"message": "Logged in successfully", "token": token})
        ctx.set_res_header("Set-Cookie", f"auth_token={token}; HttpOnly; Path=/")
        ctx.send(200, content_type='application/json')
        # Set the token as a cookie or in the response headers
    else:
        ctx.body = json.dumps({"message": "Invalid credentials"})
        ctx.send(401, content_type='application/json')

def logout(ctx: Ctx) -> None:
    auth.logout(ctx)
    ctx.body = json.dumps({"message": "Logged out successfully"})
    ctx.send(200, content_type='application/json')

@Router.auth_required
def get_protected_content(ctx: Ctx) -> None:
    ctx.body = json.dumps({"message": "This is protected content. Only authenticated users can see this. I hope you feel special 🍊🍊🍊."})
    ctx.send(200, content_type='application/json')

# ==================== API ROUTES ====================
# if you need to bind more variables to your handler, you can pass in a closure
api_router = Router(prefix='/api')

api_router.post('/logout', logout)
api_router.post('/login', login)
api_router.post('/signup', signup)
api_router.get('/hello', api_hello_world)


# api_router.get('/users', get_and_delete_users)
api_router.get('/protected', get_protected_content)

app.use(hello_middle)
app.use(auth.jwt_middleware)
app.use_router(api_router)
app.start()

```



## Advanced Configuration for Yuzu

Yuzu is designed to be flexible, allowing you to adapt it to the specific needs of your project. One way in which you can customize its behavior is by changing the default password hashing and verification functions.

### Custom Hashing and Verification Functions

By default, Yuzu uses the `bcrypt` library for password hashing and verification. If you want to use a different approach, you can pass your own hashing and verification functions to the Yuzu class constructor. Here's an example of how to do it:

#### Using SHA256 for Hashing

```python
import hashlib

def my_hash_func(password: str, salt: str = None) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def my_check_password_func(password: str, hashed_password: str, salt: str = None) -> bool:
    return hashlib.sha256(password.encode()).hexdigest() == hashed_password

auth = Yuzu(keychain, get_user_by_email, create_user, hash_func=my_hash_func, checkpw_func=my_check_password_func)

```
Using Argon2 for Hashing
Argon2 is a modern, secure password hashing algorithm that is recommended by the Password Hashing Competition. Here's an example of how to use it with Yuzu:

```python
from argon2 import PasswordHasher, exceptions

ph = PasswordHasher(time_cost=16, memory_cost=65536)

def my_hash_func(password: str, salt: str = None) -> str:
    return ph.hash(password)

def my_check_password_func(password: str, hashed_password: str, salt: str = None) -> bool:
    try:
        return ph.verify(hashed_password, password)
    except exceptions.VerifyMismatchError:
        return False

auth = Yuzu(keychain, get_user_by_email, create_user, hash_func=my_hash_func, checkpw_func=my_check_password_func)

```

These examples allow you to switch from the default bcrypt algorithm to SHA256 or Argon2. You could also modify these functions to change the difficulty of the hash function (e.g., by increasing the number of iterations or the memory usage) as per your specific requirements.

Remember that changing these functions can have implications for the security of your application. You should understand the workings of the chosen hash function and its strengths and weaknesses before making a decision.
