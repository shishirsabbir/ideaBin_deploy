# IMPORTING MODULES
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from database import Base, engine
from routers import auth, admin, superuser, ideas, interaction
from fastapi.middleware.cors import CORSMiddleware


# API INFORMATION
api_meta_desc = """
**Overview**

The Ideas Storing API is a versatile platform that empowers users to unleash their creativity by sharing and storing their innovative ideas. With this API, users can effortlessly create, curate, and showcase their unique concepts, while also fostering a dynamic and engaging community.

Key Features:
1. **Idea Creation:** Users can easily draft and publish their original ideas, complete with titles, descriptions, and tags, allowing them to capture their creativity in a structured format.

2. **Comment System:** Encourage collaboration and discussion by enabling other users to post comments on shared ideas. This fosters a sense of community and provides valuable feedback.

3. **User Profiles:** Each user gets a personalized profile, which serves as a hub for all their ideas and contributions. This allows users to build a portfolio of their innovative thoughts.

4. **Tagging and Categorization:** Ideas can be tagged and categorized, making it simple to browse and discover related concepts, thus enhancing the overall user experience.

5. **Search and Filtering:** Users can search for specific ideas or explore topics of interest using powerful search and filtering options, ensuring they find the ideas that resonate with them.

6. **Notification System:** Stay informed about interactions with your ideas and comments through a comprehensive notification system, ensuring you never miss valuable feedback.

8. **Scalability:** The API is designed to scale seamlessly as your user base grows, ensuring a responsive and reliable experience for both creators and commenters.

The Ideas Storing API is the ideal solution for building a collaborative and innovative platform where users can express their creativity, receive input from a vibrant community, and collectively bring their ideas to life. Whether you're building a brainstorming tool, a creative writing platform, or a hub for tech innovations, this API provides the foundation for transforming ideas into reality.
"""

tags_metadata = [
    {
        "name": "Super",
        "description": "Maintainance for the Website, This section will be deleted after the final version"
    },
    {
        "name": "Admin",
        "description": "Administration Routes, Get Users and Delete Users Account"
    },
    {
        "name": "Account",
        "description": "Create Account, Login and Authentication Routes"
    },
    {
        "name": "Ideas",
        "description": "Get, Post, Update and Delete Idea's Routes"
    },
    {
        "name": "Interacts",
        "description": "Vote and Comment Interaction Routes"
    },
    {
        "name": "Terms of Services",
        "description": "Terms of Service for the API"
    },
    {
        "name": "Homepage",
        "description": "Root Address of the API application"
    },
    # {
    #     "name": "Validator",
    #     "description": "Validation data fetching for Frontend"
    # },
]

app = FastAPI(
    title = "IdeaBin API",
    summary = "Ideas Storing API",
    description = api_meta_desc,
    version = "1.0.1",
    terms_of_service = "/terms",
    openapi_tags = tags_metadata,
    contact = {
        "name": "Shishir Sabbir",
        "url": "http://www.shishirsabbir.com",
        "email": "shishir.sabbir@gmail.com"
    },
    license_info = {
        "name": "MIT License",
        "url": "https://github.com/shishirsabbir/idea_bin/blob/main/LICENSE"
    }
)


# SETTING UP CORS
origins = [
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# SETTING UP THE DATABASE CONNECTION
Base.metadata.create_all(bind=engine)


# DEFINING TEMPLATE DIRECTORY
templates = Jinja2Templates(directory="templates")


# MOUNTING STATIC FILES
app.mount('/static', StaticFiles(directory="static"), name="static")



# API HOME PAGE ROUTE
@app.get('/', response_class=HTMLResponse, tags=["Homepage"])
async def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})


# TERMS ROUTE
@app.get('/terms', response_class=HTMLResponse, tags=["Terms of Services"])
async def terms_of_services(request: Request):
    return templates.TemplateResponse("terms.html", {"request": request})


# INCLUDING OTHER ROUTES
app.include_router(superuser.router, tags=["Super"])
app.include_router(admin.router, tags=["Admin"])
app.include_router(auth.router, tags=["Account"])
app.include_router(ideas.router, tags=["Ideas"])
app.include_router(interaction.router, tags=["Interacts"])
# app.include_router(validator.router, tags=["Validator"])
