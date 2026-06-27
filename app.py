from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from api.check_login import router as check_login_router
from api.fetch_trending import router as fetch_trending_router
from api.generate_message import router as generate_message_router
from api.post_chat import router as post_chat_router
from api.full_flow import router as full_flow_router
from api.status import router as status_router
app = FastAPI(

    title="CoinMarketCap Bot",

    description="Automated CoinMarketCap Community Bot",

    version="2.0.0"

)
app.add_middleware(

    CORSMiddleware,

    allow_origins=[

        "http://localhost:8000",

        "http://127.0.0.1:8000",

        "https://YOUR-RENDER-URL.onrender.com"

    ],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"]

)

# =====================================================
# API ROUTES
# =====================================================

app.include_router(

    check_login_router,

    tags=["Login"]

)

app.include_router(

    fetch_trending_router,

    tags=["Trending Coins"]

)

app.include_router(

    generate_message_router,

    tags=["Message Generation"]

)

app.include_router(

    post_chat_router,

    tags=["Chat Posting"]

)
app.include_router(

    status_router,

    tags=["Status"]

)
app.include_router(

    full_flow_router,

    tags=["Full Flow"]

)

# =====================================================
# FRONTEND
# =====================================================

BASE_DIR = Path(__file__).resolve().parent

FRONTEND_DIR = BASE_DIR / "frontend"

CSS_DIR = FRONTEND_DIR / "css"
JS_DIR = FRONTEND_DIR / "js"
ASSETS_DIR = FRONTEND_DIR / "assets"

if CSS_DIR.exists():

    app.mount(

        "/css",

        StaticFiles(directory=CSS_DIR),

        name="css"

    )

if JS_DIR.exists():

    app.mount(

        "/js",

        StaticFiles(directory=JS_DIR),

        name="js"

    )

if ASSETS_DIR.exists():

    app.mount(

        "/assets",

        StaticFiles(directory=ASSETS_DIR),

        name="assets"

    )


@app.get("/", include_in_schema=False)
def frontend():

    index_file = FRONTEND_DIR / "index.html"

    if index_file.exists():

        return FileResponse(index_file)

    return {

        "status": "success",

        "message": "Frontend not found."

    }
@app.get("/favicon.ico", include_in_schema=False)
def favicon():

    favicon_file = ASSETS_DIR / "favicon.ico"

    if favicon_file.exists():

        return FileResponse(favicon_file)

    return {

        "status": "success",

        "message": "Favicon not found."

    }

@app.get("/health", include_in_schema=False)
def health():

    return {

        "status": "online"

    }
