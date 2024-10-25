import json
import logging
import os
from typing import Callable, Optional
import typing

from fastapi import APIRouter, WebSocket, Path
from vocode.streaming.agent.base_agent import BaseAgent
from vocode.streaming.models.client_backend import InputAudioConfig, OutputAudioConfig
from vocode.streaming.models.synthesizer import ElevenLabsSynthesizerConfig
from vocode.streaming.models.transcriber import (
    AssemblyAITranscriberConfig,
)
from vocode.streaming.models.websocket import (
    AudioConfigStartMessage,
    AudioMessage,
    ReadyMessage,
    WebSocketMessage,
    WebSocketMessageType,
)

from vocode.streaming.output_device.websocket_output_device import WebsocketOutputDevice
from vocode.streaming.streaming_conversation import StreamingConversation
from vocode.streaming.synthesizer.base_synthesizer import BaseSynthesizer
from vocode.streaming.synthesizer.eleven_labs_synthesizer import ElevenLabsSynthesizer
from vocode.streaming.transcriber.assembly_ai_transcriber import AssemblyAITranscriber
from vocode.streaming.transcriber.base_transcriber import BaseTranscriber
from vocode.streaming.utils.base_router import BaseRouter

BASE_CONVERSATION_ENDPOINT = "/conversation/{agent_user_id}/{user_id}"


class ConversationRouter(BaseRouter):
    def __init__(
        self,
        agent_thunk: Callable[[], BaseAgent],
        transcriber_thunk: Callable[
            [InputAudioConfig], BaseTranscriber
        ] = lambda input_audio_config: AssemblyAITranscriber(
            AssemblyAITranscriberConfig.from_input_audio_config(
                input_audio_config=input_audio_config,
                api_key=os.getenv("ASSEMBLY_AI_API_KEY"),
            )
        ),
        synthesizer_thunk: Callable[
            [OutputAudioConfig], BaseSynthesizer
        ] = lambda output_audio_config,agent_user_id: ElevenLabsSynthesizer(
            ElevenLabsSynthesizerConfig.from_output_audio_config(
                output_audio_config=output_audio_config,
                api_key=os.getenv("ELEVENLABS_API_KEY"),
                voice_id=os.getenv("ELEVENLABS_VOICE_ID"),
                stability=1.0,
                similarity_boost=1.0,
                model_id="eleven_turbo_v2",
            ),
        ),
        logger: Optional[logging.Logger] = None,
        conversation_endpoint: str = BASE_CONVERSATION_ENDPOINT,
    ):
        super().__init__()
        self.transcriber_thunk = transcriber_thunk
        self.agent_thunk = agent_thunk
        self.synthesizer_thunk = synthesizer_thunk
        self.logger = logger or logging.getLogger(__name__)
        self.router = APIRouter()
        self.router.websocket(conversation_endpoint)(self.conversation)

    def get_conversation(
        self,
        output_device: WebsocketOutputDevice,
        start_message: AudioConfigStartMessage,
        agent_user_id: str,
    ) -> StreamingConversation:
        transcriber = self.transcriber_thunk(start_message.input_audio_config)
        synthesizer = self.synthesizer_thunk(start_message.output_audio_config, agent_user_id)
        synthesizer.synthesizer_config.should_encode_as_wav = True
        return StreamingConversation(
            output_device=output_device,
            transcriber=transcriber,
            agent=self.agent_thunk(agent_user_id=agent_user_id),
            synthesizer=synthesizer,
            conversation_id=start_message.conversation_id,
            logger=self.logger,
        )

    async def conversation(
            self, 
            websocket: WebSocket,
            user_id: str = Path(...),
            agent_user_id: str = Path(...),
        ):
        await websocket.accept()

        #audio configs
        start_message: AudioConfigStartMessage = AudioConfigStartMessage.parse_obj(
            {
                'type': 'websocket_audio_config_start',
                'input_audio_config': {
                    'sampling_rate': 48000,
                    'audio_encoding': 'linear16',
                    'chunk_size': 2048
                },
                'output_audio_config': {
                    'sampling_rate': 16000,
                    'audio_encoding': 'linear16'
                }
            }
        )
        #dispose vocode api first message
        _ = await websocket.receive_json()


        self.logger.debug(f"Conversation started")
        output_device = WebsocketOutputDevice(
            websocket,
            start_message.output_audio_config.sampling_rate,
            start_message.output_audio_config.audio_encoding,
        )
        conversation = self.get_conversation(output_device, start_message, agent_user_id)
        await conversation.start(lambda: websocket.send_text(ReadyMessage().json()))
        last_messages = { 'transcripted': None, 'received': None }
        while conversation.is_active():
            message: WebSocketMessage = WebSocketMessage.parse_obj(
                await websocket.receive_json()
            )
            if message.type == WebSocketMessageType.STOP:
                break
            audio_message = typing.cast(AudioMessage, message)
            conversation.receive_audio(audio_message.get_bytes())

            # log to websocket
            last_transcript_message_tuple = conversation.transcript.get_last_user_message()
            if last_transcript_message_tuple:
                last_transcript_message_raw : str = list(last_transcript_message_tuple).pop()
                last_transcript_message:str = last_transcript_message_raw.split(':')[-1]
            else:
                last_transcript_message = None
                
            last_agent_message : str = conversation.agent.last_sent_message

            if last_messages['transcripted'] != last_transcript_message:
                await websocket.send_text(json.dumps({"user":last_transcript_message}))
                self.logger.info(last_transcript_message)
                last_messages['transcripted'] = last_transcript_message


            if last_messages['received'] != last_agent_message:
                await websocket.send_text(json.dumps({"agent":last_agent_message}))
                self.logger.info(last_agent_message)
                last_messages['received'] = last_agent_message

        output_device.mark_closed()
        await conversation.terminate()

    def get_router(self) -> APIRouter:
        return self.router



