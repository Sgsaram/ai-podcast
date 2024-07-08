import os
import random

import fastapi
import fastapi.staticfiles
import fastapi.responses
import fastapi.templating

import pydantic

BASE_DIR = os.path.dirname(os.path.realpath(__file__));
TEST_VIEWS = random.randint(1, 200)
TEST_RECOMMENDATION = "It is a long established fact that a reader will be distracted by the readable content of a page when looking at its layout. The point of using Lorem Ipsum is that it has a more-or-less normal distribution of letters, as opposed to using 'Content here, content here', making it look like readable English. Many desktop publishing packages and web page editors now use Lorem Ipsum as their default model text, and a search for 'lorem ipsum' will uncover many web sites still in their infancy."


class PodcastDesc(pydantic.BaseModel):
    description: str
    link: str | None


class SummationResponse(pydantic.BaseModel):
    views: int
    recommendation: str


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
    response = SummationResponse(
        views = TEST_VIEWS,
        recommendation=TEST_RECOMMENDATION,
    )
    return response

