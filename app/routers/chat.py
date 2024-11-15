from fastapi import APIRouter, Request, Response, HTTPException
from fastapi.responses import StreamingResponse
from controllers.chat import ChatController
from utils.session_util import SessionUtils

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


@router.get('/chat_tool')
async def chat_tool():
    # result = chat_controller.chat_with_tool("Go to this website and summerize for me https://medium.com/@workboxtech/ai-in-test-data-generation-a-leap-in-software-testing-efficiency-76e7b8ee5667")
    # result = chat_controller.chat_with_tool("use the tool that is provide to google search tool and give me the answer who won American Election 2024?. After giving the answer please save it to a file using file tool")
    # result = chat_controller.chat_with_tool("with the providing file tool, search in the file cabinet and give me a content about barack obama")
    # result = chat_controller.chat_with_tool("with the providing file tool, search in the file cabinet and give me a content the latest save file")
    # result = chat_controller.chat_with_ollama_tool("use the tool that is provide to google search tool and give me a summary about Macbook Pro M4 chip`. After giving the answer please do not forget to  save it to a file using write file tool. It is a must to invoke write_file tool to save the content after searching.")
    # result = chat_controller.chat_with_groq_tool("use the tool that is provide to google search tool and give me a summary of what is langgraph`. After giving the answer please save it to a file using file tool")
    # result = chat_controller.chat_with_anthropic_tool("use the tool that is provide to google search tool and give me a summary of why Donuld Trump won 2024 election. Do not give me the answer directly, use the google search first and give me a response from there. After giving the answer please save it to a file using file tool")
    # result = chat_controller.chat_with_deepinfra_tool("use the tool that is provide to google search tool and give me a summary of Venom 2024 movie. Do not give me the answer directly, use the google search first and give me a response from there. After giving the answer please do not forget to save it to a file using file tool")
    # result = chat_controller.chat_with_gemini_tool("use the tool that is provide to google search tool and give me a summary of 2024 Apple Stock. Do not give me the answer directly, use the google search first and give me a response from there. After giving the answer please do not forget to save it to a file using file tool")
    # result = chat_controller.chat_with_groq_tool("use the tool that is provide to google search tool and give me a summary of new topic on oknha.news`. Scrape the content and please save it to a file using file tool")
    # result = chat_controller.chat_with_groq_tool("use the tools that are provided to use google search tool to search who is samnang pheng, then using the first link from the output of the search result, go to it and scrape the webpage. After giving the answer please save it to a file using file tool")
    result = chat_controller.chat_with_groq_tool("use the tools that are provided to tell me what is the tending topic on oknha.news. After giving the answer please save it to a file using file tool")
    return result

@router.post('/chat_with_tool')
async def chat_with_tool(request: Request, response: Response):
    if request.headers.get('Content-Type') != 'application/json':
        raise HTTPException(status_code=400, detail="Invalid Content-Type. Expected application/json")
    try:
        data = await request.json()
        print("data: " + str(data))
        # uuid = SessionUtils.get_session_id(request)
        uuid = "123456781111"
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
    response_data = chat_controller.start_chat_with_tool(data)
    return {"response": response_data}



        
    