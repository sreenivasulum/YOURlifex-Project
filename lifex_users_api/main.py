import logging
import os
from fastapi import FastAPI

from vocode.streaming.agent.restful_user_implemented_agent import RESTfulUserImplementedAgent
from vocode.streaming.models.agent import RESTfulUserImplementedAgentConfig
from vocode.streaming.models.synthesizer import ElevenLabsSynthesizerConfig
from vocode.streaming.models.transcriber import AssemblyAITranscriberConfig

from customConversation import ConversationRouter
from vocode.streaming.models.message import BaseMessage

from dotenv import load_dotenv

from vocode.streaming.synthesizer.eleven_labs_synthesizer import ElevenLabsSynthesizer
from vocode.streaming.transcriber.assembly_ai_transcriber import AssemblyAITranscriber

from config import get_user_voice_id

load_dotenv()

app = FastAPI()

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

def rest_lifex_call(agent_user_id: str):
    api_url = f"https://api-v1.yourlifex.com/api/v1/response_api/{agent_user_id}/"
    logger.debug(f"RESTful user implemented agent: {api_url}")

    return RESTfulUserImplementedAgent(
            RESTfulUserImplementedAgentConfig(
                initial_message=BaseMessage(text="How are you doing you?"),
                respond=RESTfulUserImplementedAgentConfig.EndpointConfig(
                    url=api_url,
                    method="POST"
                ),
                generate_responses=False,
            ),
            logger=logger,
            )

conversation_router = ConversationRouter(
    agent_thunk=rest_lifex_call,
    transcriber_thunk=lambda input_audio_config: AssemblyAITranscriber(
            AssemblyAITranscriberConfig.from_input_audio_config(
                input_audio_config=input_audio_config,
                api_key=os.getenv("ASSEMBLY_AI_API_KEY"),
            )
        ),
        synthesizer_thunk= lambda output_audio_config, agent_user_id: ElevenLabsSynthesizer(
            ElevenLabsSynthesizerConfig.from_output_audio_config(
                output_audio_config=output_audio_config,
                api_key=os.getenv("ELEVENLABS_API_KEY"),
                voice_id=get_user_voice_id(user_id=agent_user_id),
                stability=1.0,
                similarity_boost=1.0,
            ),
        ),
    logger=logger,
)

app.include_router(conversation_router.get_router())
