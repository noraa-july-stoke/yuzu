# Tangerine-Auth

Tangerine-Auth is a Python library that provides utilities for user authentication and secure handling of keys and encrypted data. It uses bcrypt for password hashing and JWT for token-based authentication.

## Installation

Use pip to install the package:

```sh
pip install tangerine-auth
```



## Usage

### Yuzu

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
from tangerine.key_lime import KeyLime
from tangerine.yuzu import Yuzu
import json
import jwt
import psycopg2


app = Tangerine()
keychain = KeyLime({
        "SECRET_KEY": "ILOVECATS",
})

def get_user_by_email(email):
    conn = psycopg2.connect("postgresql://postgres:C4melz!!@localhost:5432/local_development")
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
    conn = psycopg2.connect("postgresql://postgres:C4melz!!@localhost:5432/local_development")
    cur = conn.cursor()
    cur.execute("INSERT INTO tangerine.users (email, password) VALUES (%s, %s) RETURNING id", (user_data['email'], user_data['password']))
    user_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return {'_id': user_id, 'email': user_data['email'], 'password': user_data['password']}


auth = Yuzu(keychain, get_user_by_email, create_user)
# serve static files to any request not starting with /api
app.static('^/(?!api).*$', './public')

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

    if token:
        ctx.body = json.dumps({"message": "Logged in successfully", "token": token})
        ctx.set_res_header("Set-Cookie", f"auth_token={token}; HttpOnly; Path=/")
        ctx.send(200, content_type='application/json')
    else:
        ctx.body = json.dumps({"message": "Invalid credentials"})
        ctx.send(401, content_type='application/json')

def logout(ctx: Ctx) -> None:
    auth.logout()
    ctx.body = json.dumps({"message": "Logged out successfully"})
    ctx.send(200, content_type='application/json')

@Router.auth_required
def get_protected_content(ctx: Ctx) -> None:
    ctx.body = json.dumps({"message": "This is protected content. Only authenticated users can see this. I hope you feel special 🍊🍊🍊."})
    ctx.send(200, content_type='application/json')

# ==================== API ROUTES ====================
api_router = Router(prefix='/api')
api_router.post('/logout', logout)
api_router.post('/login', login)
api_router.post('/signup', signup)
api_router.get('/protected', get_protected_content)

app.use(auth.jwt_middleware)
app.use_router(api_router)
app.start()


```
