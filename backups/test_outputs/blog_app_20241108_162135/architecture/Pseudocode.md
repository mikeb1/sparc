AuthService:
- generate_token(user_data) -> str
- validate_token(token) -> dict
- authenticate_user(username, password) -> bool

BlogPostManager:
- create_post(user_id, title, content) -> Post
- get_post(post_id) -> Post
- update_post(post_id, updates) -> Post
- delete_post(post_id) -> bool

ErrorHandler:
- handle_auth_error() -> Response(401)
- handle_not_found() -> Response(404)
- handle_validation_error() -> Response(400)
