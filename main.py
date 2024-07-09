import os
import random

import fastapi
import fastapi.staticfiles
import fastapi.responses
import fastapi.templating

import pydantic

from models_api.main_module import ModelModule

BASE_DIR = os.path.dirname(os.path.realpath(__file__));
TEST_VIEWS = "SERVER"
TEST_RECOMMENDATION = "Topic: Really Bit Ctick You Have Never Seen Before\n\nAnalysis:\n\n    Current popularity: Medium\n    Trends: The title's use of \"bit\" and \"ctick\" suggests that it may be related to the growing trend of niche content focused on specific topics or skills. Additionally, the title's uniqueness and curiosity-driven nature could attract viewers looking for something new and interesting.\n\nSuggestions to Maximize Listeners:\n\n1. Emphasize the unique aspect: Highlight what makes this \"bit\" so special and different from others in the description, tags, and social media promotions.\n2. Target specific audiences: Use relevant keywords and hashtags to reach viewers interested in niche topics or skills related to the content.\n3. Create engaging thumbnails: Design eye-catching thumbnails that showcase the unusual nature of the content and entice viewers to click.\n\nAs a good idea for podcast:\n\n* The topic's uniqueness could generate significant interest, especially if it appeals to a specific audience.\n* With 24.6 million subscribers, there is already a large potential audience for this type of content.\n* By emphasizing the unique aspect and targeting relevant audiences, the podcast has a high chance of attracting more listeners.\n\nHowever, please note that the provided description does not provide much insight into the actual content of the podcast. It's crucial to create engaging and informative content to keep viewers interested in the long run."

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

    response = SummationResponse(
        views=TEST_VIEWS,
        recommendation=TEST_RECOMMENDATION,
    )
    return response

