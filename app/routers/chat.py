from fastapi import APIRouter, Request, Response, HTTPException
from fastapi.responses import StreamingResponse
from controllers.chat import ChatController
from utils.session_util import SessionUtils

from tools.web_tools import WebTools

router = APIRouter()
chat_controller = ChatController()

@router.post("/")
async def send_chat_message(request: Request):
    if request.headers.get('Content-Type') != 'application/json':
        raise HTTPException(status_code=400, detail="Invalid Content-Type. Expected application/json")
    try:
        data = await request.json()
        print(data)
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid JSON format")
    response = chat_controller.start_chat(data)
    return {"response": response}


@router.post("/custom")
async def send_custom_chat_message(request: Request, response: Response):
    # Check Content-Type header
    if request.headers.get('Content-Type') != 'application/json':
        raise HTTPException(status_code=400, detail="Invalid Content-Type. Expected application/json")
    try:
        data = await request.json()
        print("data: " + str(data))
        uuid = SessionUtils.get_session_id(request)
        if uuid is None:
            response.set_cookie(
                key="uuid",
                value=SessionUtils.generate_session_id(),
                max_age=86400,  # Cookie expires in 1 day
                httponly=True,
                samesite="None",  # Allow cross-site cookies
                secure=False,  # Only send cookie over HTTPS if True
            )
        else:
            data["uuid"] = uuid
            print("uuid: " + data["uuid"])  
            print("data: " + str(data))
        # data["uuid"] = uuid
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON format")
    print("cookies: " + str(SessionUtils.get_session_id(request)))
    response_data = chat_controller.start_custom_chat(data)
    return {"response": response_data}



@router.get("/platforms")
async def get_platforms(response: Response, request: Request):
    uuid = SessionUtils.get_session_id(request)
    if uuid is None:
        response.set_cookie(
            key="uuid",
            value=SessionUtils.generate_session_id(),
            max_age=86400,  # Cookie expires in 1 day
            httponly=True,
            samesite="None",  # Allow cross-site cookies
            secure=False,  # Only send cookie over HTTPS if True
        )
    platforms = chat_controller.get_llm_platforms()
    return platforms


@router.post("/stream_chat")
async def stream_chat(request: Request):
    if request.headers.get('Content-Type') != 'application/json':
        raise HTTPException(status_code=400, detail="Invalid Content-Type. Expected application/json")
    try:
        data = await request.json()
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid JSON format")
    
    try:
        generator = await chat_controller.stream_chat(data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    return StreamingResponse(generator, media_type="text/event-stream")



@router.post("/stream_chat_memory")
async def stream_chat_memory(request: Request):
    data = await request.json()
    gen = await chat_controller.stream_chat_memory(data)
    return StreamingResponse(gen, media_type="text/event-stream")


@router.post("/stream_chat_es")
async def stream_chat_es(request: Request):
    data = await request.json()
    gen = chat_controller.stream_chat_es(data)
    return StreamingResponse(
            gen,
            media_type="text/event-stream"
        )

@router.get('/search')    
async def search_google():
    # webTool = WebTools()
    # return webTool.scrap_main_page_link('what is on on oknha news') 
    # return webTool.google_custom_search("Go to oknha.news")
    # return webTool.google_search("Go to www.oknha.news")

    # result = chat_controller.web_chat("Give me trending news on oknha.news website related to bussiness and give the summary information in Khmer language also give me the link that you get the information from")
    # result = chat_controller.web_chat("What is the cuurent weather today in Phnom Penh. Get the results and then save it to a file")
    # result = chat_controller.web_chat("War ‘tour’, football and graffiti: How Russia is trying to influence Africa. Search the internet and tell me is this news fake or real?")
    # result = chat_controller.web_chat("what is the article in this website talk about https://www.oknha.news/social-eco/159782 . Give your answer in Khmer and save it to a file")
    # tool = WebTools();
    # result = tool.scrap_main_page_content("Give me a summary on website oknha.news")
    # result = chat_controller.web_chat("Give me a summary of trending news on website oknha.news. And save it to a text file")
    # result = chat_controller.web_chat("Give me a summary of trending news on CNN. Just give me the response and Do not save it to txt file!") 
    # result = chat_controller.web_chat("Give me the recent trending news on oknha.news website")
    # result = chat_controller.web_chat("Give me what is on edition.cnn.com. Provide me a summary of it")
    result = chat_controller.web_chat("Go to this website and summerize for me https://medium.com/@workboxtech/ai-in-test-data-generation-a-leap-in-software-testing-efficiency-76e7b8ee5667")
    # result = chat_controller.web_chat("Use the web_content_reader_tool to find the latest saved content, with query_type set to 'latest' and value set to empty string")
    # result = chat_controller.web_chat("Go to oknha.news and Give me more detail based on this news titleអ្នកឧកញ៉ា ហ៊ុន ឡាក់ ចូលរួមពិធីចុះហត្ថលេខាលើអនុស្សរណៈនៃការយោគយល់គ្នា")
    return result

@router.get('/chat_tool')
async def chat_tool():
    # result = chat_controller.chat_with_tool("Go to this website and summerize for me https://medium.com/@workboxtech/ai-in-test-data-generation-a-leap-in-software-testing-efficiency-76e7b8ee5667")
    result = chat_controller.chat_with_tool("use the tool that is provide to DuckDuckGo search tool and give me the answer who is barack obama?")

    return result

# @router.get('/search')    
# async def search_google():
#     return chat_controller.web_chat('give me what are the topics on cnn news') 

        
    