import os
import random

import fastapi
import fastapi.staticfiles
import fastapi.responses
import fastapi.templating

import pydantic

from models_api.main_module import ModelModule

BASE_DIR = os.path.dirname(os.path.realpath(__file__));
TEST_VIEWS = random.randint(1, 200)
TEST_RECOMMENDATION = "It is a long established fact that a reader will be distracted by the readable content of a page when looking at its layout. The point of using Lorem Ipsum is that it has a more-or-less normal distribution of letters, as opposed to using 'Content here, content here', making it look like readable English. Many desktop publishing packages and web page editors now use Lorem Ipsum as their default model text, and a search for 'lorem ipsum' will uncover many web sites still in their infancy."

cat2id = {
   "Film & Animation": 1,
   "Autos & Vehicles": 2,
   "Music": 10,
   "Pets & Animals": 15,
   "Sports": 17,
   "Short Movies": 18,
   "Travel & Events": 19,
   "Gaming": 20,
   "Videoblogging": 21,
   "People & Blogs": 22,
   "Comedy": 23,
   "Entertainment": 24,
   "News & Politics": 25,
   "Howto & Style": 26,
   "Education": 27,
   "Science & Technology": 28,
   "Nonprofits & Activism": 29,
   "Movies": 30,
   "Anime/Animation": 31,
   "Action/Adventure": 32,
   "Classics": 33,
   "Comedy": 34,
   "Documentary": 35,
   "Drama": 36,
   "Family": 37,
   "Foreign": 38,
   "Horror": 39,
   "Sci-Fi/Fantasy": 40,
   "Thriller": 41,
   "Shorts": 42,
   "Shows": 43,
   "Trailers": 44,
}


class PodcastDesc(pydantic.BaseModel):
    title: str
    description: str
    tags: list[str]
    link: str | None
    category: str


class SummationResponse(pydantic.BaseModel):
    views: str
    recommendation: str

module = ModelModule()

app = fastapi.FastAPI()

app.mount("/static", fastapi.staticfiles.StaticFiles(directory="static"), name="static")
templates = fastapi.templating.Jinja2Templates(directory="templates")


@app.get("/", response_class=fastapi.responses.HTMLResponse)
async def read_root(request: fastapi.Request):
    return templates.TemplateResponse(name="index.html", request=request)


@app.post("/process", response_model=SummationResponse)
async def get_summation(podcast_desc: PodcastDesc):
    if len(podcast_desc.description) == 0:
        return fastapi.HTTPException(400, "No description provided")
    if len(podcast_desc.title) == 0:
        return fastapi.HTTPException(400, "No description provided")
    
    result = module.get_result(title=podcast_desc.title, 
                               description=podcast_desc.description,
                               tags=podcast_desc.tags,
                               link=podcast_desc.link,
                               category=cat2id[podcast_desc.category])

    response = SummationResponse(
        views=result['views_prediction'],
        recommendation=result['llama_response'],
    )
    return response

