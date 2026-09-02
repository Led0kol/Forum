from fastapi import FastAPI, Request, Depends, Form, HTTPException, status
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from starlette.middleware.sessions import SessionMiddleware
import os

from app.database import engine, get_db, Base
from app import models, crud, auth

# 1. Сначала создаем экземпляр app
app = FastAPI(title="Форум", description="Простой форум на FastAPI")

# 2. Добавляем middleware
app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SECRET_KEY", "dev-secret-key-change-in-production-12345")
)

# 3. Настраиваем шаблоны и статику
templates = Jinja2Templates(directory="app/templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


# 4. Теперь можно использовать декоратор @app.on_event
@app.on_event("startup")
async def startup():
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully")


# 5. Вспомогательные функции
def get_user_context(request: Request, db: Session):
    return {
        "current_user": auth.get_current_user(request, db),
        "request": request
    }


# 6. Роуты (эндпоинты)
@app.get("/", response_class=HTMLResponse)
async def index(request: Request, db: Session = Depends(get_db)):
    topics = crud.get_topics(db)
    context = get_user_context(request, db)
    context.update({"topics": topics})
    return templates.TemplateResponse("index.html", context)


@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@app.post("/register")
async def register(
        request: Request,
        email: str = Form(...),
        username: str = Form(...),
        password: str = Form(...),
        confirm_password: str = Form(...),
        db: Session = Depends(get_db)
):
    errors = {}

    # Валидация
    if not auth.validate_email(email):
        errors["email"] = "Неверный формат email"
    elif crud.get_user_by_email(db, email):
        errors["email"] = "Email уже зарегистрирован"

    if not auth.validate_username(username):
        errors["username"] = "Имя пользователя должно содержать 3-30 символов (только буквы и цифры)"
    elif crud.get_user_by_username(db, username):
        errors["username"] = "Имя пользователя уже занято"

    if len(password) < 6:
        errors["password"] = "Пароль должен содержать минимум 6 символов"
    elif password != confirm_password:
        errors["confirm_password"] = "Пароли не совпадают"

    if errors:
        return templates.TemplateResponse("register.html", {
            "request": request,
            "errors": errors,
            "email": email,
            "username": username
        })

    # Создание пользователя
    hashed = auth.hash_password(password)
    user = crud.create_user(db, email, username, hashed)

    # Авторизация после регистрации
    request.session["user_id"] = user.id

    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login")
async def login(
        request: Request,
        email: str = Form(...),
        password: str = Form(...),
        db: Session = Depends(get_db)
):
    user = auth.authenticate_user(db, email, password)
    if not user:
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "Неверный email или пароль"
        })

    request.session["user_id"] = user.id
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)


@app.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)


@app.get("/topic/create", response_class=HTMLResponse)
async def create_topic_page(request: Request, db: Session = Depends(get_db)):
    user = auth.get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

    return templates.TemplateResponse("create_topic.html", {
        "request": request,
        "current_user": user
    })


@app.post("/topic/create")
async def create_topic(
        request: Request,
        title: str = Form(...),
        content: str = Form(...),
        db: Session = Depends(get_db)
):
    user = auth.get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

    if not title or not content:
        return templates.TemplateResponse("create_topic.html", {
            "request": request,
            "current_user": user,
            "error": "Заполните все поля",
            "title": title,
            "content": content
        })

    topic = crud.create_topic(db, title, content, user.id)
    return RedirectResponse(url=f"/topic/{topic.id}", status_code=status.HTTP_303_SEE_OTHER)


@app.get("/topic/{topic_id}", response_class=HTMLResponse)
async def view_topic(
        request: Request,
        topic_id: int,
        db: Session = Depends(get_db)
):
    topic = crud.get_topic(db, topic_id)
    if not topic:
        raise HTTPException(status_code=404, detail="Тема не найдена")

    # Увеличиваем счетчик просмотров
    crud.increment_topic_views(db, topic_id)

    posts = crud.get_posts_by_topic(db, topic_id)

    # Группируем ответы на посты
    posts_with_replies = []
    for post in posts:
        replies = crud.get_replies_by_post(db, post.id)
        posts_with_replies.append({
            "post": post,
            "replies": replies
        })

    context = get_user_context(request, db)
    context.update({
        "topic": topic,
        "posts_with_replies": posts_with_replies
    })

    return templates.TemplateResponse("topic.html", context)


@app.get("/topic/{topic_id}/edit", response_class=HTMLResponse)
async def edit_topic_page(
        request: Request,
        topic_id: int,
        db: Session = Depends(get_db)
):
    user = auth.get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

    topic = crud.get_topic(db, topic_id)
    if not topic:
        raise HTTPException(status_code=404, detail="Тема не найдена")

    if topic.author_id != user.id:
        raise HTTPException(status_code=403, detail="Нет прав для редактирования")

    return templates.TemplateResponse("edit_topic.html", {
        "request": request,
        "current_user": user,
        "topic": topic
    })


@app.post("/topic/{topic_id}/edit")
async def edit_topic(
        request: Request,
        topic_id: int,
        title: str = Form(...),
        content: str = Form(...),
        db: Session = Depends(get_db)
):
    user = auth.get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

    topic = crud.get_topic(db, topic_id)
    if not topic:
        raise HTTPException(status_code=404, detail="Тема не найдена")

    if topic.author_id != user.id:
        raise HTTPException(status_code=403, detail="Нет прав для редактирования")

    crud.update_topic(db, topic_id, title, content)
    return RedirectResponse(url=f"/topic/{topic_id}", status_code=status.HTTP_303_SEE_OTHER)


@app.post("/topic/{topic_id}/delete")
async def delete_topic(
        request: Request,
        topic_id: int,
        db: Session = Depends(get_db)
):
    user = auth.get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

    topic = crud.get_topic(db, topic_id)
    if not topic:
        raise HTTPException(status_code=404, detail="Тема не найдена")

    if topic.author_id != user.id:
        raise HTTPException(status_code=403, detail="Нет прав для удаления")

    crud.delete_topic(db, topic_id)
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)


@app.post("/topic/{topic_id}/post")
async def add_post(
        request: Request,
        topic_id: int,
        content: str = Form(...),
        parent_post_id: int = Form(None),
        db: Session = Depends(get_db)
):
    user = auth.get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

    if not content:
        return RedirectResponse(
            url=f"/topic/{topic_id}",
            status_code=status.HTTP_303_SEE_OTHER
        )

    crud.create_post(db, content, user.id, topic_id, parent_post_id)
    return RedirectResponse(
        url=f"/topic/{topic_id}",
        status_code=status.HTTP_303_SEE_OTHER
    )


@app.post("/post/{post_id}/delete")
async def delete_post(
        request: Request,
        post_id: int,
        db: Session = Depends(get_db)
):
    user = auth.get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Пост не найден")

    if post.author_id != user.id:
        raise HTTPException(status_code=403, detail="Нет прав для удаления")

    topic_id = post.topic_id
    crud.delete_post(db, post_id)
    return RedirectResponse(
        url=f"/topic/{topic_id}",
        status_code=status.HTTP_303_SEE_OTHER
    )