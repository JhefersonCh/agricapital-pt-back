from fastapi import FastAPI
# from post.controllers.postController import postRouter
# from users.controllers.userController import userRouter
# from auth.controllers.authController import authRouter

app = FastAPI(
    title="Mi API",
    description="Api de prueba con FastApi y JWT",
    version="1.0.0",
)

@app.get("/")
def index():
    return "Hello World"

# app.include_router(authRouter)
# app.include_router(postRouter)
# app.include_router(userRouter)